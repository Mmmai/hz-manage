import logging
import time
import uuid
import traceback
import re
import io
import tempfile
import networkx as nx
from celery import shared_task
from functools import reduce
from django.conf import settings
from rest_framework import viewsets
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.metadata import BaseMetadata
from rest_framework.renderers import BaseRenderer, JSONRenderer
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.pagination import PageNumberPagination
from cacheops import cached_as, invalidate_model
from django.core.cache import cache
from django.http import HttpResponse, StreamingHttpResponse
from django.db import transaction
from django.utils import timezone
from django.db.models import Q
from django.db.models import Max, Case, When, Value, IntegerField
from django_redis import get_redis_connection
from drf_spectacular.utils import extend_schema, OpenApiParameter
from celery.result import AsyncResult
from .utils import password_handler, celery_manager, zabbix_config
from .excel import ExcelHandler
from .constants import FieldMapping, FieldType, limit_field_names
from .tasks import process_import_data, setup_host_monitoring, install_zabbix_agent, sync_zabbix_host_task, update_instance_names_for_model_template_change, update_zabbix_interface_availability
from .filters import *
from .models import *
from .serializers import *
from .schemas import (
    model_groups_schema,
    models_schema,
    model_field_groups_schema,
    validation_rules_schema,
    model_fields_schema,
    model_field_preference_schema,
    unique_constraint_schema,
    model_instance_schema,
    model_ref_schema,
    model_field_meta_schema,
    model_instance_group_schema,
    model_instance_group_relation_schema,
    password_manage_schema,
)
from audit.context import audit_context
from audit.mixins import AuditContextMixin

logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = settings.REST_FRAMEWORK.get('PAGE_SIZE', 20)
    page_size_query_param = 'page_size'
    max_page_size = 1000
    
    
class CmdbBaseViewSet(AuditContextMixin, viewsets.ModelViewSet):
    """
    CMDB 应用专属的 ViewSet 基类。

    它自动集成了 AuditContextMixin，确保所有继承自它的 ViewSet
    都会被置于审计上下文中。
    """
    pagination_class = StandardResultsSetPagination
    
    def get_current_user(self):
        if self.request and hasattr(self.request, 'user'):
            return self.request.username
        return 'unknown'

    def perform_create(self, serializer):
        """在创建对象时，自动设置 create_user 和 update_user。"""
        username = self.get_current_user()
        serializer.save(create_user=username, update_user=username)

    def perform_update(self, serializer):
        """在更新对象时，自动设置 update_user。"""
        username = self.get_current_user()
        serializer.save(update_user=username)

class CmdbReadOnlyBaseViewSet(AuditContextMixin, viewsets.ReadOnlyModelViewSet):
    """
    为只读视图提供的基类，同样集成了审计上下文。
    """
    pagination_class = StandardResultsSetPagination

@model_groups_schema
class ModelGroupsViewSet(CmdbBaseViewSet):
    queryset = ModelGroups.objects.all().order_by('create_time')
    serializer_class = ModelGroupsSerializer
    filterset_class = ModelGroupsFilter
    ordering_fields = ['name', 'built_in', 'editable', 'create_time', 'update_time']
    search_fields = ['name', 'description', 'create_user', 'update_user']


@models_schema
class ModelsViewSet(CmdbBaseViewSet):
    queryset = Models.objects.all().order_by('create_time')
    serializer_class = ModelsSerializer
    filterset_class = ModelsFilter
    ordering_fields = ['name', 'type', 'create_time', 'update_time']
    search_fields = ['name', 'type', 'description', 'create_user', 'update_user']

    def generate_unique_id(self):
        while True:
            new_id = str(uuid.uuid4())
            if Models.objects.filter(id=new_id).count() == 0:
                return new_id

    def perform_create(self, serializer):
        unique_id = self.generate_unique_id()
        user = self.get_current_user()
        instance = serializer.save(id=unique_id, create_user=user, update_user=user)
        logger.info(f"New model created: {instance.name} (ID: {unique_id})")


        default_group, created = ModelFieldGroups.objects.get_or_create(
            name='basic',
            model=instance,
            defaults={
                'verbose_name': '基础配置',
                'built_in': True,
                'editable': False,
                'description': '默认字段组',
                'create_user': 'system',
                'update_user': 'system'
            }
        )
        # return instance

    def perform_destroy(self, instance):
        if instance.built_in:
            logger.warning(f"Attempt to delete built-in model denied: {instance.name}")
            raise PermissionDenied({
                'detail': 'Built-in model cannot be deleted'
            })
        logger.info(f"Model deleted successfully: {instance.name}")
        instance.delete()

    def retrieve(self, request, *args, **kwargs):
        model = self.get_object()

        field_groups = ModelFieldGroups.objects.filter(model=model).order_by('create_time')
        field_groups_data = ModelFieldGroupsSerializer(field_groups, many=True).data

        fields = ModelFields.objects.filter(model=model).order_by('order')
        fields_data = ModelFieldsSerializer(fields, many=True).data

        grouped_fields = {}
        for field in fields_data:
            group_id = field.get('model_field_group')
            grouped_fields.setdefault(str(group_id), []).append(field)
        for group in field_groups_data:
            group['fields'] = grouped_fields.get(group['id'], [])

        return Response({
            'model': ModelsSerializer(model).data,
            'field_groups': field_groups_data
        })

    @action(detail=True, methods=['post'])
    def rename_instances(self, request, pk=None):
        model = self.get_object()

        if not model:
            return Response(
                {"detail": "Model not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if not model.instance_name_template:
            return Response(
                {"detail": "No instance name template set for this model."},
                status=status.HTTP_400_BAD_REQUEST
            )

        audit_context = self.get_audit_context()
        # logger.debug(f'Audit context for instance name change: {audit_context}')
        # 触发异步任务
        task = update_instance_names_for_model_template_change.delay(
            str(model.id),
            [],
            list(model.instance_name_template),
            context=audit_context
        )

        cache_key = f"rename_task_{task.id}"
        result_dict = {
            'status': 'pending'
        }
        cache.set(cache_key, result_dict, timeout=600)
        return Response({
            "cache_key": cache_key
        }, status=status.HTTP_202_ACCEPTED)

    @action(detail=False, methods=['get'])
    def rename_status(self, request):
        cache_key = request.query_params.get('cache_key')
        if not cache_key:
            raise ValidationError({'detail': 'Missing cache key'})
        result = cache.get(cache_key)
        if not result:
            raise ValidationError({'detail': 'Cache key not found'})
        return Response(result, status=status.HTTP_200_OK)


@model_field_groups_schema
class ModelFieldGroupsViewSet(CmdbBaseViewSet):
    queryset = ModelFieldGroups.objects.all().order_by('-create_time')
    serializer_class = ModelFieldGroupsSerializer
    filterset_class = ModelFieldGroupsFilter
    ordering_fields = ['name', 'built_in', 'editable', 'create_time', 'update_time']
    search_fields = ['name', 'description', 'create_user', 'update_user']

    def perform_destroy(self, instance):
        if instance.built_in:
            logger.warning(f"Attempt to delete built-in field group denied: {instance.name}")
            raise PermissionDenied({
                'detail': 'Built-in model field group cannot be deleted'
            })
        if not instance.editable:
            logger.warning(f"Attempt to delete non-editable model group denied: {instance.name}")
            raise PermissionDenied({
                'detail': 'Non-editable model field group cannot be deleted'
            })

        default_group, created = ModelFieldGroups.objects.get_or_create(
            name='basic',
            model=instance.model,
            defaults={
                'verbose_name': '基础配置',
                'built_in': True,
                'editable': False,
                'description': '默认字段组',
                'create_user': 'system',
                'update_user': 'system'
            }
        )

        ModelFields.objects.filter(model_field_group=instance).update(model_field_group=default_group)

        super().perform_destroy(instance)
        logger.info(f"Field group deleted successfully: {instance.name}")


@validation_rules_schema
class ValidationRulesViewSet(CmdbBaseViewSet):
    queryset = ValidationRules.objects.all()
    serializer_class = ValidationRulesSerializer
    filterset_class = ValidationRulesFilter
    ordering_fields = ['name', 'field_type', 'type', 'create_time', 'update_time']
    search_fields = ['name', 'type', 'description', 'rule']

    def perform_destroy(self, instance):
        if instance.built_in:
            logger.warning(f"Attempt to delete built-in validation rule denied: {instance.name}")
            raise PermissionDenied({
                'detail': 'Built-in validation rule cannot be deleted'
            })
        elif not instance.editable:
            logger.warning(f"Attempt to delete non-editable validation rule denied: {instance.name}")
            raise PermissionDenied({
                'detail': 'Non-editable validation rule cannot be deleted'
            })
        if ModelFields.objects.filter(validation_rule=instance).exists():
            logger.warning(f"Attempt to delete validation rule in use: {instance.name}")
            raise PermissionDenied({
                'detail': 'Validation rule is in use and cannot be deleted'
            })
        instance.delete()
        logger.info(f"Validation rule deleted successfully: {instance.name}")


class ModelFieldsMetadata(BaseMetadata):
    def determine_metadata(self, request, view):
        # metadata = super().determine_metadata(request, view)
        metadata = {
            'name': 'Model Fields Options',
            'description': "Options for type and validation rules of model fields",
            'renders': [renderer.media_type for renderer in view.renderer_classes],
            'parses': [parser.media_type for parser in view.parser_classes],
        }
        metadata['field_types'] = FieldMapping.FIELD_TYPES
        metadata.setdefault('field_validations', {})
        for field_type, info in FieldMapping.TYPE_VALIDATIONS.items():
            metadata['field_validations'][field_type] = info
        metadata['limit_fields'] = limit_field_names
        return metadata


@model_fields_schema
class ModelFieldsViewSet(CmdbBaseViewSet):
    metadata_class = ModelFieldsMetadata
    queryset = ModelFields.objects.all().order_by('-create_time')
    serializer_class = ModelFieldsSerializer
    filterset_class = ModelFieldsFilter
    ordering_fields = ['name', 'type', 'order', 'create_time', 'update_time']

    def perform_destroy(self, instance):
        if instance.built_in:
            logger.warning(f"Attempt to delete built-in field group denied: {instance.name}")
            raise PermissionDenied({
                'detail': 'Built-in field cannot be deleted'
            })
        if not instance.editable:
            logger.warning(f"Attempt to delete non-editable model group denied: {instance.name}")
            raise PermissionDenied({
                'detail': 'Non-editable field cannot be deleted'
            })
        # 检测字段是否存在于unique constraints配置中，如果存在则不允许删除
        constraints = UniqueConstraint.objects.filter(model=instance.model)
        for constraint in constraints:
            if instance.name in constraint.fields:
                logger.warning(f"Attempt to delete field {instance.name} in unique constraint {constraint.name}")
                raise PermissionDenied({
                    'detail': f'Field {instance.name} is used in unique constraint {constraint.name}'
                })
        # 删除字段时，需要将字段从偏好设置中移除
        preferences = ModelFieldPreference.objects.filter(fields_preferred=[str(instance.id)])
        for preference in preferences:
            preference.fields_preferred.remove(instance.id)
            preference.save()

        ModelFieldMeta.objects.filter(model_fields=instance).delete()

        super().perform_destroy(instance)

    @action(detail=False, methods=['get'])
    def metadata(self, request):
        return Response(self.metadata_class().determine_metadata(request, self))


@model_field_preference_schema
class ModelFieldPreferenceViewSet(CmdbBaseViewSet):
    queryset = ModelFieldPreference.objects.all().order_by('-create_time')
    serializer_class = ModelFieldPreferenceSerializer
    filterset_class = ModelFieldPreferenceFilter
    search_fields = ['model', 'create_user', 'update_user']
    ordering_fields = ['model', 'create_time', 'update_time']

    def list(self, request, *args, **kwargs):
        user = request.query_params.get('user', 'system')
        model = request.query_params.get('model')
        if user and model:
            model = Models.objects.get(id=model)
            preference = ModelFieldPreference.objects.filter(model=model, create_user=user).first()
            if not preference:
                fields = list(
                    ModelFields.objects.filter(
                        model=model
                    ).order_by('order').values_list('id', flat=True)
                )
                serializer = ModelFieldPreferenceSerializer(
                    data={
                        'model': model.id,
                        'fields_preferred': fields,
                        'create_user': user,
                        'update_user': user
                    }
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()
                # fields_str_list = [str(field_id) for field_id in system_preference.fields_preferred]
                # system_preference.fields_preferred = fields_str_list
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                # fields_str_list = [str(field_id) for field_id in preference.fields_preferred]
                # preference.fields_preferred = fields_str_list
                return Response(ModelFieldPreferenceSerializer(preference).data, status=status.HTTP_200_OK)
        else:
            return super().list(request, *args, **kwargs)


@unique_constraint_schema
class UniqueConstraintViewSet(CmdbBaseViewSet):
    queryset = UniqueConstraint.objects.all().order_by('-create_time')
    serializer_class = UniqueConstraintSerializer
    filterset_class = UniqueConstraintFilter
    ordering_fields = ['model', 'create_time', 'update_time']

    def perform_destroy(self, instance):
        if instance.built_in:
            logger.warning(f"Attempt to delete built-in unique constraint denied: {instance}")
            raise PermissionDenied({
                'detail': 'Built-in unique constraint cannot be deleted'
            })
        return super().perform_destroy(instance)


class BinaryFileRenderer(BaseRenderer):
    media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    format = 'xlsx'
    charset = None

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data.get('file_content') if isinstance(data, dict) else data


@model_instance_schema
class ModelInstanceViewSet(CmdbBaseViewSet):
    queryset = ModelInstance.objects.all().order_by('-create_time').prefetch_related('field_values__model_fields')
    serializer_class = ModelInstanceSerializer
    filterset_class = ModelInstanceFilter
    ordering_fields = ['create_time', 'update_time']
    search_fields = ['model', 'instance_name', 'create_user', 'update_user']

    def _get_serializer_context_for_instances(self, instances):
        context = self.get_serializer_context()
        instance_ids = [instance.id for instance in instances]

        # 获取字段元数据
        field_meta_map = {}
        meta_qs = ModelFieldMeta.objects.filter(
            model_instance_id__in=instance_ids
        ).select_related('model_fields', 'model_fields__validation_rule')
        for meta in meta_qs:
            field_meta_map.setdefault(str(meta.model_instance_id), []).append(meta)
        context['field_meta'] = field_meta_map

        # 获取分组信息
        instance_group_map = {}
        group_relations = ModelInstanceGroupRelation.objects.filter(
            instance_id__in=instance_ids
        ).select_related('group').values('instance_id', 'group_id', 'group__path')
        for rel in group_relations:
            instance_group_map.setdefault(str(rel['instance_id']), []).append({
                'group_id': str(rel['group_id']),
                'group_path': rel['group__path']
            })
        context['instance_group'] = instance_group_map

        # 获取引用实例的名称
        ref_model_ids = set(
            meta_qs.filter(
                model_fields__type=FieldType.MODEL_REF
            ).values_list('data', flat=True)
        )
        ref_instances_map = {}
        if ref_model_ids:
            ref_instances = ModelInstance.objects.filter(id__in=ref_model_ids).values('id', 'instance_name')
            ref_instances_map = {str(inst['id']): inst['instance_name'] for inst in ref_instances}
        context['ref_instances'] = ref_instances_map
        
        return context

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        context = self._get_serializer_context_for_instances([instance])
        serializer = self.get_serializer(instance, context=context)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            context = self._get_serializer_context_for_instances(page)
            serializer = self.get_serializer(page, many=True, context=context)
            return self.get_paginated_response(serializer.data)

        context = self._get_serializer_context_for_instances(queryset)
        serializer = self.get_serializer(queryset, many=True, context=context)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def _apply_filters(self, queryset, model, filter_params):
        model_id = model
        matching_ids_list = []
        params = filter_params.copy()

        if model_id:
            queryset = queryset.filter(model_id=model_id)
            logger.debug(f"Filtered by model ID: {model_id}")

        standard_fields = {}
        for field_name in ModelInstanceFilter.Meta.fields:
            if field_name in params:
                field_value = params.pop(field_name)
                if isinstance(field_value, list) and field_value:
                    standard_fields[field_name] = field_value[0]
                else:
                    standard_fields[field_name] = field_value

        if standard_fields:
            filterset = ModelInstanceFilter(standard_fields, queryset=queryset)
            queryset = filterset.qs

        for field_name, field_value in filter_params.items():
            # 忽略特殊参数
            if field_name in limit_field_names:
                continue

            try:
                field = ModelFields.objects.get(
                    model=model_id if model_id else queryset.first().model_id,
                    name=field_name
                )

                meta_query = ModelFieldMeta.objects.filter(model_fields=field)
                all_instance_ids = set(meta_query.values_list('model_instance_id', flat=True))
                exclude_ids = set()

                if isinstance(field_value, str):
                    if field_value.startswith('like:'):
                        value = field_value[5:]
                        meta_query = meta_query.filter(data__icontains=value)
                        all_instance_ids = set(meta_query.values_list('model_instance_id', flat=True))
                    elif field_value.startswith('in:'):
                        values = field_value[3:].split(',')
                        meta_query = meta_query.filter(data__in=values)
                        all_instance_ids = set(meta_query.values_list('model_instance_id', flat=True))
                    elif field_value.startswith('regex:'):
                        pattern = field_value[6:]
                        meta_query = meta_query.filter(data__regex=pattern)
                        all_instance_ids = set(meta_query.values_list('model_instance_id', flat=True))
                    elif field_value.startswith('not:'):
                        # 反选匹配
                        value = field_value[4:]
                        if value.startswith('like:'):
                            v = value[5:]
                            exclude_ids = set(
                                meta_query.filter(
                                    data__icontains=v).values_list(
                                    'model_instance_id', flat=True))
                        elif value.startswith('in:'):
                            v = value[3:].split(',')
                            exclude_ids = set(meta_query.filter(data__in=v).values_list('model_instance_id', flat=True))
                        elif value.startswith('regex:'):
                            pattern = value[6:]
                            exclude_ids = set(
                                meta_query.filter(
                                    data__regex=pattern).values_list(
                                    'model_instance_id', flat=True))
                        else:
                            if value == 'null':
                                exclude_ids = set(
                                    meta_query.filter(
                                        data__isnull=True).values_list(
                                        'model_instance_id', flat=True))
                            else:
                                exclude_ids = set(
                                    meta_query.filter(
                                        data=value).values_list(
                                        'model_instance_id',
                                        flat=True))
                    else:
                        meta_query = meta_query.filter(
                            data=field_value) if field_value != 'null' else meta_query.filter(
                            data__isnull=True)
                        all_instance_ids = set(meta_query.values_list('model_instance_id', flat=True))

                # 获取匹配的实例ID
                matching_ids = all_instance_ids - exclude_ids
                matching_ids_list.append(matching_ids)

            except ModelFields.DoesNotExist:
                logger.warning(f"Field not found: {field_name}")
                continue
            except Exception as e:
                logger.error(f"Error processing field {field_name}: {traceback.format_exc()}")
                continue

        # 取交集并过滤queryset
        if matching_ids_list:
            final_ids = reduce(lambda x, y: x & y, matching_ids_list)

            if final_ids:
                queryset = queryset.filter(id__in=final_ids)
            else:
                # 当没有匹配的 ID 时，返回空查询集
                queryset = queryset.none()
                logger.debug("No matching results found, returning empty queryset")

        return queryset

    @cached_as(ModelInstance, timeout=600)
    def get_queryset(self):
        queryset = ModelInstance.objects.all().order_by('-create_time').select_related('model')

        if self.action == 'retrieve' and self.kwargs.get('pk'):
            return queryset

        query_params = self.request.query_params

        model_id = None
        if 'model' in query_params:
            model_id = query_params['model']
        logger.debug(f"Query parameters: {query_params}")

        if not query_params:
            return queryset

        return self._apply_filters(queryset, model_id, query_params)

    def get_all_child_groups(self, group):
        """递归获取所有子分组ID"""
        group_ids = [group.id]
        children = ModelInstanceGroup.objects.filter(parent=group)
        for child in children:
            group_ids.extend(self.get_all_child_groups(child))
        return group_ids

    @action(detail=False, methods=['patch'])
    def bulk_update_fields(self, request):
        instance_ids = request.data.get('instances', [])
        model_id = request.data.get('model')
        fields_data = request.data.get('fields', {})
        update_user = self.get_current_user()
        filter_by_params = request.data.get('all', False)
        params = request.data.get('params', {})
        group_id = request.data.get('group')

        if group_id:
            params['model_instance_group'] = group_id

        if filter_by_params and params:
            instances = ModelInstance.objects.all()
            instances = self._apply_filters(instances, model_id, params)
        elif instance_ids:
            instances = ModelInstance.objects.filter(id__in=instance_ids)
        else:
            # 给定的查询参数不足
            raise ValidationError("Insufficient query parameters provided.")

        if not instances.exists():
            raise ValidationError("No instances found with the provided criteria.")

        model_count = instances.values('model').distinct().count()
        if model_count > 1:
            raise ValidationError("Instances belong to multiple models; bulk update requires a single model.")

        correlation_id = str(uuid.uuid4())
        with audit_context(correlation_id=correlation_id):
            updated_count = self.get_serializer_class().bulk_update_instances(
                instances_qs=instances,
                fields_data=fields_data,
                context=self.get_serializer_context()
            )

        return Response({
            'status': 'success',
            'updated_instances_count': updated_count
        }, status=status.HTTP_200_OK)

    def get_renderers(self):
        if self.action in ['export_template', 'export_data', 'download_error_records']:
            return [BinaryFileRenderer()]
        return [JSONRenderer()]

    @action(detail=False, methods=['post'])
    def export_template(self, request):
        """导出实例数据模板"""
        try:
            # 获取模型ID
            model_id = request.data.get('model')
            if not model_id:
                raise ValidationError({'detail': 'Model ID is required'})

            # 获取模型及其字段
            model = Models.objects.get(id=model_id)
            fields = ModelFields.objects.filter(
                model=model
            ).select_related(
                'validation_rule',
                'model_field_group'
            ).order_by('model_field_group__create_time', 'order')

            # 生成Excel模板
            excel_handler = ExcelHandler()
            workbook = excel_handler.generate_template(fields)

            excel_file = io.BytesIO()
            workbook.save(excel_file)
            excel_file.seek(0)

            # 返回文件响应
            headers = {
                'Content-Disposition': f'attachment; filename="{model.name}_template.xlsx"'
            }

            logger.info(f"Template exported successfully for model: {model.name}")
            return Response(
                {
                    'filename': f"{model.name}_template.xlsx",
                    'file_content': excel_file.getvalue()
                },
                status=status.HTTP_200_OK,
                headers=headers
            )

        except Models.DoesNotExist:
            raise ValidationError({'detail': f'Model {model_id} not found'})
        except Exception as e:
            logger.error(f"Error exporting template: {str(e)}")
            raise ValidationError({'detail': f'Failed to export template: {str(e)}'})

    @action(detail=False, methods=['post'])
    def export_data(self, request):
        """导出实例数据"""
        try:
            instance_ids = request.data.get('instances', [])
            model_id = request.data.get('model')
            filter_by_params = request.data.get('all', False)
            params = request.data.get('params', {})
            group_id = request.data.get('group')
            restricted_fields = request.data.get('fields', [])

            if not model_id:
                raise ValidationError({'detail': 'Model ID is required'})

            instances = ModelInstance.objects.filter(model_id=model_id)

            if group_id:
                params['model_instance_group'] = group_id

            if filter_by_params and params:
                instances = ModelInstance.objects.all()
                instances = self._apply_filters(instances, model_id, params)
            elif instance_ids:
                instances = instances.filter(id__in=instance_ids)

            # if group_id:
            #     instance_in_group = ModelInstanceGroupRelation.objects.filter(
            #         group=group_id
            #     ).values_list('instance_id', flat=True)
            #     instances = instances.filter(id__in=instance_in_group)

            if not instances.exists():
                raise ValidationError("No instances found with the provided criteria.")

            if instance_ids:
                instances = instances.filter(id__in=instance_ids)
            logger.info(f'Exporting data for {len(instances)} instances')

            field_meta_map = {}
            instances_meta_qs = ModelFieldMeta.objects.filter(
                model_instance__in=instances
            ).select_related('model_fields', 'model_fields__validation_rule')
            for meta in instances_meta_qs:
                field_meta_map.setdefault(str(meta.model_instance_id), []).append(meta)

            ref_model_ids = set()
            ref_model_qs = instances_meta_qs.filter(
                model_fields__type=FieldType.MODEL_REF
            ).exclude(
                model_fields__ref_model_id__isnull=True
            ).values_list('model_fields__ref_model_id', flat=True)
            for id in ref_model_qs:
                ref_model_ids.add(str(id))

            ref_instances_map = {}
            if ref_model_ids:
                ref_instances_list = ModelInstance.objects.filter(
                    model_id__in=ref_model_ids
                ).values('id', 'instance_name')
                ref_instances_map = {
                    str(instance['id']): instance['instance_name']
                    for instance in ref_instances_list
                }

            context = self.get_serializer_context()
            context['field_meta'] = field_meta_map
            context['ref_instances'] = ref_instances_map

            serialized_instances_data = self.get_serializer(instances, many=True, context=context).data

            # 获取模型及其字段
            model = Models.objects.get(id=model_id)
            fields_query = ModelFields.objects.filter(model=model)

            # 字段过滤
            if restricted_fields:
                fields_query = fields_query.filter(name__in=restricted_fields)

            fields = fields_query.select_related(
                'validation_rule',
                'model_field_group'
            ).order_by('model_field_group__create_time', 'order')

            for instance_data in serialized_instances_data:
                for field in fields:
                    if field.type == FieldType.ENUM:
                        data = instance_data['fields'].get(field.name, {})
                        if data:
                            instance_data['fields'][field.name] = data.get('label')
                    elif field.type == FieldType.MODEL_REF:
                        data = instance_data['fields'].get(field.name, {})
                        if data:
                            instance_data['fields'][field.name] = data.get('instance_name')
                    elif field.type == FieldType.PASSWORD:
                        data = instance_data['fields'].get(field.name, None)
                        instance_data['fields'][field.name] = password_handler.decrypt_sm4(data)

            # 生成Excel导出
            excel_handler = ExcelHandler()
            workbook = excel_handler.generate_data_export(fields, serialized_instances_data)

            excel_file = io.BytesIO()
            workbook.save(excel_file)
            excel_file.seek(0)

            # 返回文件响应
            headers = {
                'Content-Disposition': f'attachment; filename="{model.name}_data.xlsx"'
            }

            logger.info(f"Data exported successfully for model: {model.name}")
            return Response(
                {
                    'filename': f"{model.name}_data.xlsx",
                    'file_content': excel_file.getvalue()
                },
                status=status.HTTP_200_OK,
                headers=headers
            )

        except Exception as e:
            logger.error(f"Error exporting data: {traceback.format_exc()}")
            raise ValidationError({'detail': f'Failed to export data: {str(e)}'})

    @action(detail=False, methods=['post'])
    def import_data(self, request):
        file = request.FILES.get('file')
        model_id = request.data.get('model')

        if not file or not model_id:
            raise ValidationError({'detail': 'Missing file or model ID'})

        results = {
            'cache_key': None,
        }
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp:
            for chunk in file.chunks():
                temp.write(chunk)
            temp_path = temp.name
        logger.info(f"Temp file created: {temp_path}")

        try:
            excel_handler = ExcelHandler()
            excel_data = excel_handler.load_data(temp_path)
            if excel_data['status'] == 'failed':
                raise ValidationError({'detail': f'Failed to load Excel data: {excel_data["errors"][-1]}'})
            else:
                logger.info(f"Excel data loaded successfully: {excel_data}")

            headers = excel_data.get('headers', [])
            model = Models.objects.get(id=model_id)
            fields_query = ModelFields.objects.filter(model=model).values_list('name', flat=True)
            if set(fields_query) != set(headers):
                raise ValidationError({'detail': 'Excel headers do not match model fields'})

            cache_key = f"import_task_{uuid.uuid4()}"
            request_context = {
                'data': {},
            }

            if not celery_manager.check_heartbeat():
                raise ValidationError({'detail': 'Celery worker is not available'})

            audit_context = self.get_audit_context()
            task = process_import_data.delay(
                excel_data,
                model_id,
                request_context,
                audit_context
            )
            results['cache_key'] = f'import_task_{task.id}'
            cache_results = {
                'status': 'pending',
                'total': len(excel_data.get('instances', [])),
                'progress': 0,
                'created': 0,
                'updated': 0,
                'skipped': 0,
                'failed': 0,
                'errors': [],
                'error_file_key': None
            }
            cache.set(cache_key, cache_results, timeout=600)
            return Response(results, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error loading Excel data: {str(e)}")
            raise ValidationError({'detail': f'Failed to load Excel data: {str(e)}'})

    @action(detail=False, methods=['get'])
    def import_status(self, request):
        cache_key = request.query_params.get('cache_key')
        if not cache_key:
            raise ValidationError({'detail': 'Missing cache key'})
        result = cache.get(cache_key)
        if not result:
            raise ValidationError({'detail': 'Cache key not found'})
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def import_status_sse(self, request):
        cache_key = request.query_params.get('cache_key')
        if not cache_key:
            raise ValidationError({'detail': 'Missing cache key'})

        def event_stream():
            last = None

            for _ in range(600):
                result = cache.get(cache_key)
                if not result:
                    yield ValidationError({'detail': 'Cache key not found'})
                    break

                current = (result.get('progress'), result.get('status'))
                if current != last:
                    last = current
                    yield f'data: {result}'

                if result.get('status') in ['completed', 'failed']:
                    break

                time.sleep(1)

        response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        # response['X-Accel-Buffering'] = 'no'
        return response

    @action(detail=False, methods=['post'])
    def download_error_records(self, request):
        cache_key = request.data.get('error_file_key')
        if not cache_key:
            raise ValidationError({'detail': 'Missing error file key'})
        error_file = cache.get(cache_key)
        if not error_file:
            raise ValidationError({'detail': 'Error file not found'})

        headers = {
            'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'Content-Disposition': 'attachment; filename="import_errors.xlsx"'
        }

        return Response(
            {
                'filename': f"import_errors.xlsx",
                'file_content': error_file
            },
            status=status.HTTP_200_OK,
            headers=headers
        )

    def perform_destroy(self, instance):
        groups = ModelInstanceGroupRelation.objects.filter(instance=instance).values_list('group', flat=True)
        groups = ModelInstanceGroup.objects.filter(id__in=groups)
        if '空闲池' not in groups.values_list('label', flat=True):
            raise PermissionDenied({'detail': 'Instance is not in unassigned group'})
        ModelInstanceGroup.clear_groups_cache(groups)
        instance.delete()

    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        instance_ids = request.data.get('instances', [])
        model_id = request.data.get('model')
        filter_by_params = request.data.get('all', False)
        params = request.data.get('params', {})
        group_id = request.data.get('group')
        instances = ModelInstance.objects.all()

        if group_id:
            group = ModelInstanceGroup.objects.get(id=group_id)
            if group and group.label != '空闲池' and group.path != '所有/空闲池':
                raise ValidationError({'detail': 'Instances not in the unassigned group cannot be deleted'})
            instance_in_group = ModelInstanceGroupRelation.objects.filter(
                group=group_id
            ).values_list('instance_id', flat=True)
            instances = instances.filter(id__in=instance_in_group)

        if filter_by_params and (group_id or params):
            if params:
                instances = self._apply_filters(instances, model_id, params)
        elif instance_ids:
            instances = instances.filter(id__in=instance_ids)
        else:
            # 给定的查询参数不足
            raise ValidationError("Insufficient query parameters provided.")

        if not instances.exists():
            raise ValidationError("No instances found with the provided criteria.")

        try:
            model_id = instances.first().model_id
            if instances.filter(model_id=model_id).count() != instances.count():
                raise ValidationError("Instances do not belong to the same model.")

            valid_id = instances.values_list('id', flat=True)
            invalid_id = {}

            unassigned_group = ModelInstanceGroup.objects.get(
                model=model_id,
                label='空闲池'
            )
            relations = ModelInstanceGroupRelation.objects.filter(instance__in=valid_id)
            group_invalid_ids = relations.exclude(group=unassigned_group).values_list('instance_id', flat=True)
            invalid_id = {instance_id: 'Instance is not in unassigned group' for instance_id in group_invalid_ids}

            if ModelFields.objects.filter(ref_model_id=model_id).exists():
                for instance in instances:
                    if ModelFieldMeta.objects.filter(data=str(instance.id)).exists():
                        invalid_id[instance.id] = 'Referenced by other model field meta'
            valid_id = set(valid_id) - set(invalid_id.keys())

            ModelInstance.objects.filter(id__in=valid_id).delete()

            return Response({
                'success': len(valid_id),
                'errors': list(invalid_id)
            }, status=status.HTTP_200_OK)
        except Exception as e:
            raise ValidationError(f'Error deleting instances: {str(e)}')


@model_ref_schema
class ModelInstanceBasicViewSet(CmdbReadOnlyBaseViewSet):
    serializer_class = ModelInstanceBasicViewSerializer
    queryset = ModelInstance.objects.all().order_by('-create_time')
    filterset_class = ModelInstanceBasicFilter
    search_fields = ['model', 'instance_name', 'create_user', 'update_user']
    ordering_fields = ['name', 'create_time', 'update_time']


@model_field_meta_schema
class ModelFieldMetaViewSet(CmdbBaseViewSet):
    queryset = ModelFieldMeta.objects.all().order_by('-create_time')
    serializer_class = ModelFieldMetaSerializer
    filterset_class = ModelFieldMetaFilter
    ordering_fields = ['create_time', 'update_time']


@model_instance_group_schema
class ModelInstanceGroupViewSet(CmdbBaseViewSet):
    queryset = ModelInstanceGroup.objects.all().order_by('create_time')
    serializer_class = ModelInstanceGroupSerializer
    pagination_class = None
    filterset_class = ModelInstanceGroupFilter
    ordering_fields = ['label', 'order', 'path', 'create_time', 'update_time']

    def _build_model_groups_tree(self):
        """构建所有模型的分组树"""
        result = {}
        models = Models.objects.all()

        for model in models:
            root_groups = ModelInstanceGroup.objects.filter(
                model=model,
                parent=None
            ).order_by('order')

            if root_groups.exists():
                result[str(model.id)] = {
                    'model_name': model.name,
                    'model_verbose_name': model.verbose_name,
                    'groups': self.get_serializer(root_groups, many=True).data
                }

        return result

    def get_queryset(self):
        queryset = self.queryset
        model_id = self.request.query_params.get('model')

        try:
            if self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
                return queryset.select_related('model')
            if self.action in ['add_instances', 'remove_instances', 'search_instances']:
                return queryset
            if model_id:
                queryset = queryset.filter(model_id=model_id)
                logger.debug(f"Filtering groups by model: {model_id}")

            # 只返回顶层节点，子节点通过序列化器递归获取
            queryset = queryset.filter(parent=None)

            # 添加排序
            # queryset = queryset.select_related('model').order_by('label')

            return queryset

        except Exception as e:
            logger.error(f"Error in get_queryset: {str(e)}")
            return ModelInstanceGroup.objects.none()

    def list(self, request, *args, **kwargs):
        try:
            model_id = request.query_params.get('model')

            if model_id:
                # 返回特定模型的分组树
                queryset = self.get_queryset()
                serializer = self.get_serializer(queryset, many=True)
                groups_data = {}
                for group_data in serializer.data:
                    groups_data.update(group_data)

                return Response(groups_data)
            else:
                # 返回所有模型的分组树
                return Response(self._build_model_groups_tree())

        except Exception as e:
            logger.error(f"Error in list view: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def _get_all_child_groups(self, group):
        """递归获取所有子组"""
        children = list(ModelInstanceGroup.objects.filter(parent=group))
        logger.debug(f'Found {len(children)} children for group {group}')
        all_children = children.copy()
        if len(children) == 0:
            return list()
        for child in children:
            all_children.extend(self._get_all_child_groups(child))
        logger.debug(f'Groups: {all_children}')
        return all_children

    def _check_root_group_operation(self, group):
        """检查是否是对【所有】分组的操作"""
        if group.label == '所有' and group.built_in:
            logger.warning(f"Attempt to modify root group {group.label}")
            raise PermissionDenied({
                'detail': 'Cannot modify root group "所有"'
            })

    def update(self, request, *args, **kwargs):
        """禁止更新内置分组"""
        instance = self.get_object()
        self._check_root_group_operation(instance)

        target_id = request.data.get('target_id')
        position = request.data.get('position')

        if target_id and position:
            serializer = self.get_serializer(
                instance,
                data=request.data,
                partial=True,
                context={
                    'target_id': target_id,
                    'position': position
                })
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """禁止删除内置分组"""
        try:
            instance = self.get_object()
            if instance.built_in:
                logger.warning(f"Attempt to delete built-in group {instance.label}")
                raise PermissionDenied({
                    'detail': f'Cannot delete built-in group "{instance.label}"'
                })
            logger.info(f"Starting deletion process for group: {instance.label}")

            with transaction.atomic():
                unassigned_group = ModelInstanceGroup.objects.get(
                    model=instance.model,
                    label='空闲池',
                    built_in=True
                )

                child_groups = self._get_all_child_groups(instance)
                all_groups = [instance] + child_groups
                group_ids = [g.id for g in all_groups]

                logger.info(f"Found {len(child_groups)} child groups")

                instances_to_move = set()
                for group in all_groups:
                    group_instances = ModelInstanceGroupRelation.objects.filter(
                        group=group
                    ).values_list('instance_id', flat=True)

                    # 对于每个实例，检查是否还有其他非待删除组的关系
                    for instance_id in group_instances:
                        other_relations = ModelInstanceGroupRelation.objects.filter(
                            instance_id=instance_id
                        ).exclude(
                            group_id__in=group_ids
                        ).exclude(
                            group=unassigned_group
                        )

                        if not other_relations.exists():
                            instances_to_move.add(instance_id)

                logger.debug(f"Found {len(instances_to_move)} instances to move to unassigned pool")

                deleted_relations = ModelInstanceGroupRelation.objects.filter(
                    group_id__in=group_ids
                ).delete()[0]
                logger.debug(f"Deleted {deleted_relations} group relations")

                # 将实例移动到空闲池
                if instances_to_move:
                    relations_to_create = [
                        ModelInstanceGroupRelation(
                            instance_id=instance_id,
                            group=unassigned_group,
                            create_user=request.user.username if hasattr(request.user, 'username') else request.user
                        )
                        for instance_id in instances_to_move
                    ]
                    ModelInstanceGroupRelation.objects.bulk_create(relations_to_create)
                    logger.debug(f"Created {len(relations_to_create)} relations in unassigned pool")

                for child in child_groups:
                    child.delete()
                    logger.debug(f"Deleted child group: {child.label}")

                instance.delete()
                logger.info(f"Deleted group: {instance.label}")

                ModelInstanceGroup.clear_group_cache(instance)

                return Response({
                    'message': f'Successfully deleted group {instance.label} and its children',
                    'deleted_groups_count': len(all_groups),
                    'moved_instances_count': len(instances_to_move)
                }, status=status.HTTP_200_OK)

        except ModelInstanceGroup.DoesNotExist as e:
            logger.error(f"Group not found: {str(e)}")
            return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting group: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=['get'])
    def tree(self, request):
        model_id = request.query_params.get('model')
        if not model_id:
            return Response({'detail': 'Missing model parameter'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            root_groups = ModelInstanceGroup.objects.filter(model_id=model_id, parent=None).order_by('order')
            context = self.get_serializer_context()
            
            # 获取所有分组与实例的关联关系
            all_group_ids = ModelInstanceGroup.objects.filter(model_id=model_id).values_list('id', flat=True)
            relations = ModelInstanceGroupRelation.objects.filter(
                group_id__in=all_group_ids
            ).values('group_id', 'instance_id')

            relation_map = {}
            instance_ids = set()
            for r in relations:
                gid = str(r['group_id'])
                iid = str(r['instance_id'])
                relation_map.setdefault(gid, []).append(iid)
                instance_ids.add(iid)
            context['relation_map'] = relation_map

            # 获取instance_name
            instance_map = {}
            if instance_ids:
                inst_qs = ModelInstance.objects.filter(id__in=instance_ids).values('id', 'instance_name')
                instance_map = {str(row['id']): row['instance_name'] for row in inst_qs}
            context['instance_map'] = instance_map

            serializer = ModelInstanceGroupTreeSerializer(root_groups, many=True, context=context)
            
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error building instance group tree for model {model_id}: {str(e)}", exc_info=True)
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@model_instance_group_relation_schema
class ModelInstanceGroupRelationViewSet(CmdbBaseViewSet):
    queryset = ModelInstanceGroupRelation.objects.all().order_by('-create_time')
    # serializer_class = ModelInstanceGroupRelationSerializer
    filterset_class = ModelInstanceGroupRelationFilter
    ordering_fields = ['create_time', 'update_time']
    http_method_names = ['get', 'post']

    def get_serializer_class(self):
        if self.action == 'create_relations':
            return BulkInstanceGroupRelationSerializer
        elif self.action == 'tree':
            return ModelInstanceGroupTreeSerializer
        return ModelInstanceGroupRelationSerializer

    @action(detail=False, methods=['post'])
    def create_relations(self, request):
        """批量创建或更新实例分组关联"""
        logger.info(f"Creating or updating instance group relations")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        logger.debug(f"Data validated. Saving relations...")

        try:
            correlation_id = str(uuid.uuid4())
            with audit_context(correlation_id=correlation_id):
                relations = serializer.save()
                logger.info(f"Successfully created or updated {len(relations)} instance group relations.")
            return Response(
                ModelInstanceGroupRelationSerializer(
                    relations,
                    many=True
                ).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.error(f"Error creating or updating instance group relations: {str(e)}")
            raise ValidationError(str(e))


class RelationDefinitionViewSet(CmdbBaseViewSet):
    queryset = RelationDefinition.objects.all().order_by('name')
    serializer_class = RelationDefinitionSerializer
    filterset_class = RelationDefinitionFilter
    ordering_fields = ['name', 'create_time', 'update_time']

    def perform_destroy(self, instance):
        # 检查关系定义是否已被使用
        if Relations.objects.filter(relation=instance).exists():
            logger.warning(f"Trying to delete a relation definition in use: {instance.name}")
            raise PermissionDenied("This relation definition is in use by at least one relation instance and cannot be deleted.")
        logger.info(f"Relation definition '{instance.name}' has been deleted.")
        super().perform_destroy(instance)


class RelationsViewSet(CmdbBaseViewSet):
    queryset = Relations.objects.select_related(
        'source_instance__model', 'target_instance__model', 'relation'
    ).order_by('-create_time')
    serializer_class = RelationsSerializer
    filterset_class = RelationsFilter
    search_fields = [
        'source_instance__instance_name',
        'target_instance__instance_name',
        'relation__name'
    ]
    ordering_fields = ['create_time', 'update_time']

    @action(detail=False, methods=['post'])
    def bulk_associate(self, request, *args, **kwargs):
        """
        批量创建多对一或一对多的关联关系。
        例如：将多个主机（多）关联到一个交换机（一）。
        """
        serializer = BulkAssociateRelationsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        instance_ids = data['instance_ids']
        target_instance_id = data['target_instance_id']
        relation_id = data['relation_id']
        direction = data['direction']
        attributes = data['relation_attributes']
        user = self.get_current_user()

        relations_to_create = []
        for instance_id in instance_ids:
            if direction == 'target-source':
                source_id, target_id = instance_id, target_instance_id
            elif direction == 'source-target':
                source_id, target_id = target_instance_id, instance_id
            else:
                raise ValidationError(f"Invalid direction: {direction}. Must be 'source-target' or 'target-source'.")
            
            relations_to_create.append(
                Relations(
                    source_instance_id=source_id,
                    target_instance_id=target_id,
                    relation_id=relation_id,
                    relation_attributes=attributes,
                    create_user=user,
                    update_user=user
                )
            )

        try:
            with capture_audit_snapshots(relations_to_create, created=True):
                created_objects = Relations.objects.bulk_create(relations_to_create, ignore_conflicts=True)
            
            return Response(
                {
                    "detail": f"Successfully created {len(created_objects)} relations.",
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.error(f"Error creating relations: {e}", exc_info=True)
            raise ValidationError(f"Failed to create relations: {e}")

    @action(detail=False, methods=['post'])
    def bulk_delete(self, request, *args, **kwargs):
        relation_ids = request.data.get('ids', [])
        if not isinstance(relation_ids, list) or not relation_ids:
            raise ValidationError("Require a non-empty list of relation IDs to delete.")

        queryset = self.get_queryset().filter(id__in=relation_ids)
        
        with capture_audit_snapshots(list(queryset)):
            deleted_count, _ = queryset.delete()

        return Response(
            {"deleted_count": deleted_count},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'])
    def get_topology(self, request):
        try:
            start_node_ids = request.data.get('start_nodes', [])
            end_node_ids = request.data.get('end_nodes', [])
            depth = int(request.data.get('depth', 3))
            direction = request.data.get('direction', 'both')
            mode = request.data.get('mode', 'blast')

            if not start_node_ids:
                return Response({"detail": "Start nodes are required."}, status=status.HTTP_400_BAD_REQUEST)
            if mode == 'path' and not end_node_ids:
                return Response({"detail": "End nodes are required when using path mode."}, status=status.HTTP_400_BAD_REQUEST)

            G, involved_nodes, involved_edges = self._build_graph_on_demand(
                start_node_ids, end_node_ids, depth, direction, mode
            )

            node_objects = [data['instance'] for _, data in G.nodes(data=True)]
            edge_objects = [data['relation'] for u, v, data in G.edges(data=True)]

            node_serializer = ModelInstanceBasicViewSerializer(node_objects, many=True)
            edge_serializer = RelationsSerializer(edge_objects, many=True)

            return Response({
                "nodes": node_serializer.data,
                "edges": edge_serializer.data
            })

        except Exception as e:
            logger.error(f"Error occurred when processing topology query: {e}", exc_info=True)
            return Response({"detail": "Internal server error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _filter_path_edges(self, G, start_node, end_node, depth, subgraph):
        paths = nx.all_simple_paths(G, source=start_node, target=end_node, cutoff=depth)
        for path in paths:
            for i in range(len(path) - 1):
                u, v = path[i], path[i+1]
                if not subgraph.has_node(u): 
                    subgraph.add_node(u, **G.nodes[u])
                if not subgraph.has_node(v): 
                    subgraph.add_node(v, **G.nodes[v])
                if not subgraph.has_edge(u, v): 
                    subgraph.add_edge(u, v, **G.get_edge_data(u, v))
        return subgraph

    def _find_path_between_nodes(self, G, start_node_ids, end_node_ids, depth):
        """
        在给定的图G中查找从start_node_ids到end_node_ids的所有简单路径，路径长度不超过depth。
        返回包含这些路径的子图。
        """
        subgraph = nx.DiGraph()

        for start_node in start_node_ids:
            for end_node in end_node_ids:
                if G.has_node(start_node) and G.has_node(end_node):
                    try:
                        return self._filter_path_edges(G, start_node, end_node, depth, subgraph)
                    except nx.NetworkXNoPath:
                        continue
        return subgraph

    def _find_blast_neighbors(self, G, start_node_ids, end_node_ids, direction, depth):
        """
        在图G中查找从start_node_ids出发，按照direction方向，深度为depth的邻接节点。
        如果提供了end_node_ids，则只返回包含这些终点的子图。
        """
        subgraph = nx.DiGraph()
        queue = set(start_node_ids)
        seen_nodes = set()

        for _ in range(depth):
            if not queue:
                break

            current_level_nodes = list(queue)
            seen_nodes.update(current_level_nodes)
            queue.clear()

            q_filter = Q()
            if direction in ('forward', 'both'):
                q_filter |= Q(source_instance_id__in=current_level_nodes)
            if direction in ('reverse', 'both'):
                q_filter |= Q(target_instance_id__in=current_level_nodes)

            relations_qs = Relations.objects.filter(q_filter).select_related('source_instance', 'target_instance', 'relation')
            newly_found_nodes = self._add_edges_to_graph(G, relations_qs)
            queue.update(newly_found_nodes - seen_nodes)

        if not end_node_ids:
            return subgraph
        
        final_subgraph = nx.DiGraph()
        for start_node in start_node_ids:
            for end_node in end_node_ids:
                if subgraph.has_node(start_node) and subgraph.has_node(end_node):
                    try:
                        return self._filter_path_edges(subgraph, start_node, end_node, depth, final_subgraph)
                    except nx.NetworkXNoPath:
                        continue
        return final_subgraph

    def _build_graph_on_demand(self, start_node_ids, end_node_ids, depth, direction, mode):
        """
        按需从数据库查询数据来构建图，避免一次性加载所有数据。
        """
        G = nx.DiGraph()

        # 路径查询
        if mode == 'path':
            initial_nodes = set(start_node_ids + end_node_ids)
            temp_G = nx.DiGraph()
            queue = set(initial_nodes)
            seen_nodes = set()
            
            for _ in range(depth + 1):
                if not queue:
                    break
                
                current_level_nodes = list(queue)
                seen_nodes.update(current_level_nodes)
                queue.clear()

                relations_qs = Relations.objects.filter(
                    Q(source_instance_id__in=current_level_nodes) | Q(target_instance_id__in=current_level_nodes)
                ).select_related('source_instance', 'target_instance', 'relation')

                new_nodes = self._add_edges_to_graph(temp_G, relations_qs)
                queue.update(new_nodes - seen_nodes)
            
            G = self._find_path_between_nodes(temp_G, start_node_ids, end_node_ids, depth)
                        
        # 爆炸分析
        elif mode == 'blast':
            G = self._find_blast_neighbors(G, start_node_ids, end_node_ids, direction, depth)
            
        # 邻接查询
        elif mode == 'neighbor':
            for start_node in start_node_ids:
                q_filter = Q()
                if direction in ('forward', 'both'):
                    q_filter |= Q(source_instance_id=start_node)
                if direction in ('reverse', 'both'):
                    q_filter |= Q(target_instance_id=start_node)

                relations_qs = Relations.objects.filter(q_filter).select_related(
                    'source_instance', 'target_instance', 'relation'
                )
                self._add_edges_to_graph(G, relations_qs)

        # 模式匹配
        elif mode == 'pattern':
            pass
        
        # 孤立节点
        elif mode == 'isolate':
            instances = ModelInstance.objects.filter(id__in=start_node_ids).values_list('id', flat=True)
            instance_id_map = {instance.id: instance for instance in instances}
            in_rel_instances = Relations.objects.filter(
                Q(source_instance_id__in=start_node_ids) | Q(target_instance_id__in=start_node_ids)
            ).values_list('source_instance_id', 'target_instance_id')
            in_rel_instance_ids = set(id for pair in in_rel_instances for id in pair)
            isolated_ids = set(instance_id_map.keys()) - in_rel_instance_ids
            for instance_id in isolated_ids:
                instance = instance_id_map.get(instance_id)
                if instance:
                    G.add_node(str(instance.id), instance=instance)

        return G

    def _add_edges_to_graph(self, G, relations_qs):
        """
        将查询到的关系添加到图中，并根据topology_type处理边的方向。
        返回本次添加操作中新发现的所有节点的ID集合。
        """
        new_nodes = set()
        
        # 预加载所有涉及的实例对象，减少循环内查询
        instance_ids = set()
        for rel in relations_qs:
            instance_ids.add(rel.source_instance_id)
            instance_ids.add(rel.target_instance_id)
        
        instances = ModelInstance.objects.in_bulk([str(uuid) for uuid in instance_ids])
        
        for rel in relations_qs:
            source_id = str(rel.source_instance_id)
            target_id = str(rel.target_instance_id)
            
            source_inst = instances.get(rel.source_instance_id)
            target_inst = instances.get(rel.target_instance_id)

            if not source_inst or not target_inst:
                continue

            # 添加节点（如果不存在）
            if source_id not in G:
                G.add_node(source_id, instance=source_inst)
                new_nodes.add(source_id)
            if target_id not in G:
                G.add_node(target_id, instance=target_inst)
                new_nodes.add(target_id)

            # 根据关系类型添加边
            topology_type = rel.relation.topology_type
            
            if topology_type in ('directed', 'daggered'):
                G.add_edge(source_id, target_id, relation=rel)
            elif topology_type == 'undirected':
                G.add_edge(source_id, target_id, relation=rel)
                G.add_edge(target_id, source_id, relation=rel) # 添加反向边以模拟无向

        return new_nodes

@password_manage_schema
class PasswordManageViewSet(CmdbBaseViewSet):

    @action(detail=False, methods=['post'])
    def re_encrypt(self, request):
        """重新加密密码"""
        try:
            password_meta = ModelFieldMeta.objects.filter(model_fields__type='password').values('id', 'data')
            if not password_meta:
                return Response(status=status.HTTP_204_NO_CONTENT)
            password_dict = {
                str(password['id']): password['data']
                for password in password_meta
            }
            encrypted = password_handler.re_encrypt(password_dict)
            with transaction.atomic():
                to_update = []
                for meta_id, encrypted_password in encrypted.items():
                    to_update.append(
                        ModelFieldMeta(
                            id=meta_id,
                            data=encrypted_password
                        )
                    )
                ModelFieldMeta.objects.bulk_update(to_update, ['data'])
            invalidate_model(ModelFieldMeta)
            invalidate_model(ModelInstance)
            return Response({
                'status': 'success',
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error re-encrypting password: {traceback.format_exc()}")
            return Response({'status': 'fail', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def reset_passwords(self, request):
        """将所有密码置空"""
        try:
            password_meta = ModelFieldMeta.objects.filter(model_fields__type='password').values('id')
            if not password_meta:
                return Response(status=status.HTTP_204_NO_CONTENT)
            with transaction.atomic():
                ModelFieldMeta.objects.filter(id__in=[p['id'] for p in password_meta]).update(data='')
            return Response({
                'status': 'success'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error resetting passwords: {str(e)}")
            return Response({'status': 'fail', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SystemCacheViewSet(CmdbBaseViewSet):
    
    @action(detail=False, methods=['post'])
    def clear_cache(self, request):
        """清理系统缓存"""
        try:
            conn = get_redis_connection("default")
            key_prefix = settings.CACHES['default'].get('KEY_PREFIX', '')
            
            if not key_prefix:
                return Response({
                    'status': 'failed',
                    'message': 'Cache key prefix is not set in settings.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            pattern = f'{key_prefix}*'
            keys_to_delete = conn.keys(pattern)
            
            if keys_to_delete:
                deleted_count = conn.delete(*keys_to_delete)
            else:
                deleted_count = 0
            logger.warning(f'Manually cleared {deleted_count} cache keys with prefix {key_prefix}')
            return Response({
                'status': 'success',
                'deleted_keys_count': deleted_count
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
            return Response({
                'status': 'failed',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            

class ZabbixSyncHostViewSet(CmdbBaseViewSet):
    queryset = ZabbixSyncHost.objects.all().order_by('create_time')
    serializer_class = ZabbixSyncHostSerializer
    pagination_class = StandardResultsSetPagination
    filterset_class = ZabbixSyncHostFilter
    ordering_fields = ['host_id', 'ip', 'name', 'agent_installed', 'interface_available', 'create_time', 'update_time']

    @action(detail=False, methods=['post'])
    def update_zabbix_availability(self, request):
        """手动触发 Zabbix 接口可用性更新"""
        try:
            result = update_zabbix_interface_availability.delay()

            return Response({
                'status': 'success',
                'task_id': result.id
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error triggering Zabbix interface availability update: {str(e)}")
            return Response(
                {'status': 'fail', 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def sync_zabbix_host(self, request):
        try:
            # 触发异步任务
            task = sync_zabbix_host_task.delay()

            return Response({
                'status': 'success',
                'task_id': task.id
            }, status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            logger.error(f"Failed to trigger sync task: {str(e)}")
            return Response({
                'status': 'error',
                'message': f'Failed to trigger sync task: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def install_agents(self, request):
        try:
            ids = request.data.get('ids', [])
            all_failed = request.data.get('all', False)

            force_flag = False

            if not ids and not all_failed:
                return Response({
                    'status': 'failed',
                    'message': 'No IDs provided and all failed flag is not set.'
                })

            if all_failed:
                hosts = ZabbixSyncHost.objects.filter(agent_installed=False)
            else:
                force_flag = True
                hosts = ZabbixSyncHost.objects.filter(id__in=ids)

            if not hosts.exists():
                return Response({
                    'status': 'failed',
                    'message': 'No hosts found matching the criteria.'
                }, status=status.HTTP_200_OK)

            # hosts.update(agent_installed=False, installation_error=None)

            cache_key = f'install_status_{str(uuid.uuid4())}'
            task_info = {
                'host_task_map': {},
                'total': hosts.count()
            }

            for host in hosts:
                # 获取主机的密码
                try:
                    # 从实例中获取密码字段
                    host_instance = host.instance
                    password_meta = ModelFieldMeta.objects.filter(
                        model_instance=host_instance,
                        model_fields__name='system_password'
                    ).first()

                    if not password_meta or not password_meta.data:
                        logger.warning(f"No password found for host {host.ip}")
                        continue

                    # 获取解密后的密码
                    password = password_handler.decrypt_to_plain(password_meta.data)

                    # 触发安装任务
                    task = setup_host_monitoring.delay(
                        str(host.instance.id),
                        host.name,
                        host.ip,
                        password,
                        force=force_flag)
                    logger.info(f"Triggered Zabbix agent installation for host {host.ip}")

                    task_info['host_task_map'][str(host.id)] = task.id

                except Exception as e:
                    logger.error(f"Failed to trigger Zabbix agent installation for host {host.ip}: {str(e)}")
                    continue

            cache.set(cache_key, task_info, timeout=1200)
            return Response(
                {'status': 'success', 'cache_key': cache_key},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Error triggering Zabbix agent installation: {str(e)}")
            return Response(
                {'status': 'failed', 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def installation_status_sse(self, request):
        """使用 SSE 实时获取 Zabbix 安装状态"""
        try:
            cache_key = request.query_params.get('cache_key')
            if not cache_key:
                raise ValidationError({'detail': 'Missing cache key'})
            task_info = cache.get(cache_key)
            logger.info(f'{task_info}')
            if not task_info:
                raise ValidationError({'detail': 'Cache key not found'})

            result = {
                'status': 'pending',
                'total': task_info['total'],
                'success': 0,
                'failed': 0,
                'progress': 0
            }

            def event_stream():
                result['status'] = 'processing'
                last_progress = 0
                completed_hosts = set()

                for _ in range(600):
                    for zsh_id, task_id in task_info['host_task_map'].items():
                        if zsh_id in completed_hosts:
                            continue

                        check_result = self.check_chain_task(task_id)
                        if check_result is None:
                            continue
                        elif check_result == 1:
                            result['success'] += 1
                            completed_hosts.add(zsh_id)
                        elif check_result == -1:
                            result['failed'] += 1
                            completed_hosts.add(zsh_id)

                    result['progress'] = (result['success'] + result['failed']) * 100 // result['total']

                    if result['progress'] == 100:
                        result['status'] = 'completed'
                        yield f"data: {result}\n\n"
                        break

                    if result['progress'] != last_progress:
                        last_progress = result['progress']
                        yield f"data: {result}\n\n"

                    # 暂停 2 秒后继续检查
                    time.sleep(2)

            # 返回 SSE 响应
            response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
            response['Cache-Control'] = 'no-cache'
            response['X-Accel-Buffering'] = 'no'
            return response

        except Exception as e:
            logger.error(f"Error in installation status SSE: {str(e)}")
            return Response({
                'error': f'Error in installation status SSE: {str(e)}'
            }, status=500)

    @staticmethod
    def check_chain_task(task_id):
        """检查链式任务的状态"""
        task = AsyncResult(task_id)
        if not task.ready():
            return None
        if task.successful():
            if task.result:
                chain_task_id = task.result.get('chain_task_id')
                chain_task = AsyncResult(chain_task_id)
                if not chain_task.ready():
                    return None
                if chain_task.successful():
                    return 1
                else:
                    return -1
            else:
                logger.info(f"Task {task_id} has no result")
                return -1
        else:
            return -1


class ZabbixProxyViewSet(CmdbBaseViewSet):
    queryset = ZabbixProxy.objects.all().order_by('create_time')
    serializer_class = ZabbixProxySerializer
    filterset_class = ZabbixProxyFilter
    ordering_fields = ['proxy_id', 'name', 'ip', 'create_time', 'update_time']


class ProxyAssignRuleViewSet(CmdbBaseViewSet):
    queryset = ProxyAssignRule.objects.all().order_by('create_time')
    serializer_class = ProxyAssignRuleSerializer
    filterset_class = ProxyAssignRuleFilter
    ordering_fields = ['rule', 'type', 'proxy', 'create_time', 'update_time']
