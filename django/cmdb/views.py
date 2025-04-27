import logging
import time
import uuid
import traceback
import re
import io
import tempfile
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
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .utils import password_handler, celery_manager
from .excel import ExcelHandler
from .constants import FieldMapping, limit_field_names
from .tasks import process_import_data, setup_host_monitoring, install_zabbix_agent, sync_zabbix_host_task, update_instance_names_for_model_template_change, update_zabbix_interface_availability
from .filters import (
    ModelGroupsFilter,
    ModelsFilter,
    ModelFieldGroupsFilter,
    ValidationRulesFilter,
    ModelFieldsFilter,
    ModelFieldPreferenceFilter,
    UniqueConstraintFilter,
    ModelInstanceFilter,
    ModelInstanceBasicFilter,
    ModelFieldMetaFilter,
    ModelInstanceGroupFilter,
    ModelInstanceGroupRelationFilter,
    RelationDefinitionFilter,
    RelationsFilter,
    ZabbixSyncHostFilter,
)
from .models import (
    ModelGroups,
    Models,
    ModelFieldGroups,
    ValidationRules,
    ModelFields,
    ModelFieldPreference,
    UniqueConstraint,
    ModelInstance,
    ModelFieldMeta,
    ModelInstanceGroup,
    ModelInstanceGroupRelation,
    RelationDefinition,
    Relations,
    ZabbixSyncHost,
)
from .serializers import (
    ModelGroupsSerializer,
    ModelsSerializer,
    ModelFieldGroupsSerializer,
    ValidationRulesSerializer,
    ModelFieldsSerializer,
    ModelFieldPreferenceSerializer,
    UniqueConstraintSerializer,
    ModelInstanceSerializer,
    ModelInstanceBasicViewSerializer,
    ModelFieldMetaSerializer,
    ModelInstanceGroupSerializer,
    ModelInstanceGroupRelationSerializer,
    BulkInstanceGroupRelationSerializer,
    RelationDefinitionSerializer,
    RelationsSerializer,
    ZabbixSyncHostSerializer
)
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

logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = settings.REST_FRAMEWORK.get('PAGE_SIZE', 20)
    page_size_query_param = 'page_size'
    max_page_size = 1000


@model_groups_schema
class ModelGroupsViewSet(viewsets.ModelViewSet):
    queryset = ModelGroups.objects.all().order_by('create_time')
    serializer_class = ModelGroupsSerializer
    pagination_class = StandardResultsSetPagination
    filterset_class = ModelGroupsFilter
    ordering_fields = ['name', 'built_in', 'editable', 'create_time', 'update_time']
    search_fields = ['name', 'description', 'create_user', 'update_user']


@models_schema
class ModelsViewSet(viewsets.ModelViewSet):
    queryset = Models.objects.all().order_by('create_time')
    serializer_class = ModelsSerializer
    pagination_class = StandardResultsSetPagination
    filterset_class = ModelsFilter
    # lookup_field = 'id'
    ordering_fields = ['name', 'type', 'create_time', 'update_time']
    search_fields = ['name', 'type', 'description', 'create_user', 'update_user']

    def generate_unique_id(self):
        while True:
            new_id = str(uuid.uuid4())
            if Models.objects.filter(id=new_id).count() == 0:
                return new_id

    def perform_create(self, serializer):
        unique_id = self.generate_unique_id()
        instance = serializer.save(id=unique_id)
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

        return instance

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

        # 触发异步任务
        task = update_instance_names_for_model_template_change.delay(
            str(model.id),
            [],
            list(model.instance_name_template)
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
class ModelFieldGroupsViewSet(viewsets.ModelViewSet):
    queryset = ModelFieldGroups.objects.all().order_by('-create_time')
    serializer_class = ModelFieldGroupsSerializer
    pagination_class = StandardResultsSetPagination
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
class ValidationRulesViewSet(viewsets.ModelViewSet):
    queryset = ValidationRules.objects.all()
    serializer_class = ValidationRulesSerializer
    pagination_class = StandardResultsSetPagination
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
class ModelFieldsViewSet(viewsets.ModelViewSet):
    metadata_class = ModelFieldsMetadata
    queryset = ModelFields.objects.all().order_by('-create_time')
    serializer_class = ModelFieldsSerializer
    pagination_class = StandardResultsSetPagination
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
class ModelFieldPreferenceViewSet(viewsets.ModelViewSet):
    queryset = ModelFieldPreference.objects.all().order_by('-create_time')
    serializer_class = ModelFieldPreferenceSerializer
    pagination_class = StandardResultsSetPagination
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
class UniqueConstraintViewSet(viewsets.ModelViewSet):
    queryset = UniqueConstraint.objects.all().order_by('-create_time')
    serializer_class = UniqueConstraintSerializer
    pagination_class = StandardResultsSetPagination
    filterset_class = UniqueConstraintFilter
    ordering_fields = ['model', 'create_time', 'update_time']

    def perform_create(self, serializer):
        instance = serializer.save()
        logger.info(f"New unique constraint created: {instance.fields}")
        return instance

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
class ModelInstanceViewSet(viewsets.ModelViewSet):
    queryset = ModelInstance.objects.all().order_by('-create_time').prefetch_related('field_values__model_fields')
    serializer_class = ModelInstanceSerializer
    pagination_class = StandardResultsSetPagination
    filterset_class = ModelInstanceFilter
    ordering_fields = ['create_time', 'update_time']
    search_fields = ['model', 'instance_name', 'create_user', 'update_user']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['decrypt_password'] = self.request.query_params.get('decrypt_password', 'false').lower() == 'true'
        return context

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
            logger.info(f"Applied standard filters: {standard_fields}")

        for field_name, field_value in filter_params.items():
            # 忽略特殊参数
            if field_name in limit_field_names:
                continue

            try:
                field = ModelFields.objects.get(
                    model=model_id if model_id else queryset.first().model_id,
                    name=field_name
                )
                logger.debug(f"Processing field: {field.name}")

                meta_query = ModelFieldMeta.objects.filter(model_fields=field)
                all_instance_ids = set(meta_query.values_list('model_instance_id', flat=True))
                exclude_ids = set()

                # 处理各种过滤条件逻辑（从现有的get_queryset复制过来的代码）
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
                logger.debug(f"Found matching IDs for {field_name}: {matching_ids}")

            except ModelFields.DoesNotExist:
                logger.warning(f"Field not found: {field_name}")
                continue
            except Exception as e:
                logger.error(f"Error processing field {field_name}: {traceback.format_exc()}")
                continue

        # 取交集并过滤queryset
        if matching_ids_list:
            final_ids = reduce(lambda x, y: x & y, matching_ids_list)
            logger.debug(f"Final matching IDs: {final_ids}")

            if final_ids:
                queryset = queryset.filter(id__in=final_ids)
                logger.debug("Final query generated successfully")
            else:
                # 当没有匹配的 ID 时，返回空查询集
                queryset = queryset.none()
                logger.debug("No matching results found, returning empty queryset")

        return queryset

    @cached_as(ModelInstance, timeout=600)
    def get_queryset(self):
        queryset = ModelInstance.objects.all()\
            .order_by('-create_time')\
            .prefetch_related(
                'field_values__model_fields',
                'field_values__model_fields__validation_rule',
        ).select_related('model')

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
        update_user = request.data.get('update_user')
        filter_by_params = request.data.get('all', False)
        params = request.data.get('params', {})
        group_id = request.data.get('group')

        if filter_by_params and (group_id or params):
            instances = ModelInstance.objects.all()
            if params:
                instances = self._apply_filters(instances, model_id, params)
        elif instance_ids:
            instances = ModelInstance.objects.filter(id__in=instance_ids)
        else:
            # 给定的查询参数不足
            raise ValidationError("Insufficient query parameters provided.")

        if group_id:
            instance_in_group = ModelInstanceGroupRelation.objects.filter(
                group=group_id
            ).values_list('instance_id', flat=True)
            instances = instances.filter(id__in=instance_in_group)

        if not instances.exists():
            raise ValidationError("No instances found with the provided criteria.")

        serializer = self.get_serializer(
            instance=instances.first(),
            data={
                'fields': fields_data,
                'update_user': update_user
            },
            partial=True,
            context={
                'request': request,
                'bulk_update': True,
                'instances': instances
            }
        )
        logger.info(f'Updating {len(instances)} instances with fields: {fields_data}')
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.debug(f'Serializer data: {serializer.data}')
        logger.info(f'Instances updated successfully')

        return Response({
            'status': 'success',
            'updated_instances_count': instances.count()
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

            if filter_by_params and (group_id or params):
                instances = ModelInstance.objects.all()
                if params:
                    instances = self._apply_filters(instances, model_id, params)
            elif instance_ids:
                instances = instances.filter(id__in=instance_ids)

            if group_id:
                instance_in_group = ModelInstanceGroupRelation.objects.filter(
                    group=group_id
                ).values_list('instance_id', flat=True)
                instances = instances.filter(id__in=instance_in_group)

            if not instances.exists():
                raise ValidationError("No instances found with the provided criteria.")

            # 获取缓存的查询结果
            cached_queryset = self.get_queryset().filter(model_id=model_id)

            # 如果有指定实例ID，则从缓存结果中过滤
            if instance_ids:
                instances = cached_queryset.filter(id__in=instance_ids)
            else:
                instances = cached_queryset
            logger.info(f'Exporting data for {len(instances)} instances')

            # 获取模型及其字段
            model = Models.objects.get(id=model_id)
            fields_query = ModelFields.objects.filter(model=model)

            # 字段过滤
            if restricted_fields:
                fields_query = fields_query.filter(name__in=restricted_fields)

            fields = fields_query.select_related(
                'validation_rule',
                'model_field_group'
            ).order_by('order')

            # 生成Excel导出
            excel_handler = ExcelHandler()
            workbook = excel_handler.generate_data_export(fields, instances)

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
            logger.error(f"Error exporting data: {str(e)}")
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

            task = process_import_data.delay(
                excel_data,
                model_id,
                request_context
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
        response['X-Accel-Buffering'] = 'no'
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
            raise PermissionDenied({'detail': '实例不在空闲池中，无法删除，请先移动到空闲池'})
        ModelInstanceGroup.clear_groups_cache(groups)
        instance.delete()

    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):

        instance_ids = request.data.get('instances', [])
        model_id = request.data.get('model')
        filter_by_params = request.data.get('all', False)
        params = request.data.get('params', {})
        group_id = request.data.get('group')

        a = time.perf_counter()

        instances = ModelInstance.objects.all()

        b = time.perf_counter()

        logger.info(f'Fetch all instances takes {b - a}s')

        if group_id:
            group = ModelInstanceGroup.objects.get(id=group_id)
            if group and group.label != '空闲池' and group.path != '所有/空闲池':
                raise ValidationError({'detail': 'Instances not in the unassigned group cannot be deleted'})
            instance_in_group = ModelInstanceGroupRelation.objects.filter(
                group=group_id
            ).values_list('instance_id', flat=True)
            instances = instances.filter(id__in=instance_in_group)

        c = time.perf_counter()
        logger.info(f'Filter by group takes {c - b}s')

        if filter_by_params and (group_id or params):
            if params:
                instances = self._apply_filters(instances, model_id, params)
        elif instance_ids:
            instances = instances.filter(id__in=instance_ids)
        else:
            # 给定的查询参数不足
            raise ValidationError("Insufficient query parameters provided.")

        d = time.perf_counter()
        logger.info(f'Filter by params takes {d - c}s')

        if not instances.exists():
            raise ValidationError("No instances found with the provided criteria.")

        try:
            model_id = instances.first().model_id
            if instances.filter(model_id=model_id).count() != instances.count():
                raise ValidationError("Instances do not belong to the same model.")

            e = time.perf_counter()
            logger.info(f'Check model ID takes {e - d}s')

            valid_id = instances.values_list('id', flat=True)
            invalid_id = {}

            unassigned_group = ModelInstanceGroup.objects.get(
                model=model_id,
                label='空闲池'
            )
            relations = ModelInstanceGroupRelation.objects.filter(instance__in=valid_id)
            group_invalid_ids = relations.exclude(group=unassigned_group).values_list('instance_id', flat=True)
            invalid_id = {instance_id: 'Instance is not in unassigned group' for instance_id in group_invalid_ids}
            f = time.perf_counter()
            logger.info(f'Check unassigned group takes {f - e}s')

            if ModelFields.objects.filter(ref_model_id=model_id).exists():
                for instance in instances:
                    if ModelFieldMeta.objects.filter(data=str(instance.id)).exists():
                        invalid_id[instance.id] = 'Referenced by other model field meta'
            g = time.perf_counter()
            logger.info(f'Check unassigned group takes {g - f}s')
            valid_id = set(valid_id) - set(invalid_id.keys())

            ModelInstance.objects.filter(id__in=valid_id).delete()
            h = time.perf_counter()
            logger.info(f'Bulk delete operation takes {h - g}s')
            logger.info(f'All operations take {h - a}s')

            return Response({
                'success': len(valid_id),
                'errors': list(invalid_id)
            }, status=status.HTTP_200_OK)
        except Exception as e:
            raise ValidationError(f'Error deleting instances: {str(e)}')


@model_ref_schema
class ModelInstanceBasicViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ModelInstanceBasicViewSerializer
    queryset = ModelInstance.objects.all().order_by('-create_time')
    filterset_class = ModelInstanceBasicFilter
    pagination_class = StandardResultsSetPagination
    search_fields = ['model', 'instance_name', 'create_user', 'update_user']
    ordering_fields = ['name', 'create_time', 'update_time']


@model_field_meta_schema
class ModelFieldMetaViewSet(viewsets.ModelViewSet):
    queryset = ModelFieldMeta.objects.all().order_by('-create_time')
    serializer_class = ModelFieldMetaSerializer
    pagination_class = StandardResultsSetPagination
    filterset_class = ModelFieldMetaFilter
    ordering_fields = ['create_time', 'update_time']


@model_instance_group_schema
class ModelInstanceGroupViewSet(viewsets.ModelViewSet):
    queryset = ModelInstanceGroup.objects.all().order_by('create_time')
    serializer_class = ModelInstanceGroupSerializer
    # pagination_class = StandardResultsSetPagination
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

    @action(detail=True, methods=['post'])
    def add_instances(self, request, pk=None):
        """添加实例到分组"""
        group = self.get_object()
        self._check_root_group_operation(group)
        instance_ids = request.data.get('instances', [])
        user = request.data.get('update_user')

        try:
            logger.info(f"Adding instances {instance_ids} to group {group.label}")

            with transaction.atomic():
                unassigned_group = ModelInstanceGroup.objects.get(
                    model=group.model,
                    label='空闲池',
                    built_in=True
                )

                if group.label == '空闲池' and group.built_in:
                    # 如果目标组是空闲池，删除所有其他组关系
                    logger.info(f"Target group is unassigned pool, removing all other group relations")
                    ModelInstanceGroupRelation.objects.filter(
                        instance_id__in=instance_ids
                    ).delete()
                else:
                    # 如果目标组不是空闲池，只删除与空闲池的关系
                    logger.info(f"Target group is not unassigned pool, removing unassigned pool relations")
                    ModelInstanceGroupRelation.objects.filter(
                        instance_id__in=instance_ids,
                        group=unassigned_group
                    ).delete()

                # 批量创建新的关系
                relations_to_create = [
                    ModelInstanceGroupRelation(
                        instance_id=instance_id,
                        group=group,
                        create_user=user
                    )
                    for instance_id in instance_ids
                    if not ModelInstanceGroupRelation.objects.filter(
                        instance_id=instance_id,
                        group=group
                    ).exists()
                ]

                if relations_to_create:
                    ModelInstanceGroupRelation.objects.bulk_create(relations_to_create)
                    logger.info(f"Created {len(relations_to_create)} new group relations")

            return Response({
                'message': f'Successfully added {len(instance_ids)} instances to group {group.label}',
                'added_count': len(relations_to_create)
            }, status=status.HTTP_201_CREATED)

        except ModelInstanceGroup.DoesNotExist as e:
            logger.error(f"Group not found: {str(e)}")
            return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error adding instances to group: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def remove_instances(self, request, pk=None):
        """从分组移除实例"""
        try:
            group = self.get_object()
            self._check_root_group_operation(group)
            instance_ids = request.data.get('instances', [])
            user = request.data.get('update_user')

            logger.info(f"Removing instances {instance_ids} from group {group.label}")

            if group.label == '空闲池' and group.built_in:
                logger.warning("Cannot remove instances from unassigned pool")
                return Response({
                    'error': 'Cannot remove instances from unassigned pool'
                }, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                unassigned_group = ModelInstanceGroup.objects.get(
                    model=group.model,
                    label='空闲池',
                    built_in=True
                )

                deleted_count = ModelInstanceGroupRelation.objects.filter(
                    instance_id__in=instance_ids,
                    group=group
                ).delete()[0]
                logger.info(f"Deleted {deleted_count} group relations")

                # 检查每个实例是否还有其他组关系
                instances_to_unassign = []
                for instance_id in instance_ids:
                    other_relations = ModelInstanceGroupRelation.objects.filter(
                        instance_id=instance_id
                    ).exclude(group=unassigned_group)

                    if not other_relations.exists():
                        instances_to_unassign.append(
                            ModelInstanceGroupRelation(
                                instance_id=instance_id,
                                group=unassigned_group,
                                create_user=user,
                                update_user=user
                            )
                        )
                        logger.info(f"Instance {instance_id} will be moved to unassigned pool")

                # 批量创建空闲池关系
                if instances_to_unassign:
                    ModelInstanceGroupRelation.objects.bulk_create(instances_to_unassign)
                    logger.info(f"Added {len(instances_to_unassign)} instances to unassigned pool")

            return Response({
                'message': f'Successfully removed {deleted_count} instances from group {group.label}',
                'removed_count': deleted_count,
                'unassigned_count': len(instances_to_unassign)
            }, status=status.HTTP_200_OK)

        except ModelInstanceGroup.DoesNotExist as e:
            logger.error(f"Group not found: {str(e)}")
            return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error removing instances from group: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def search_instances(self, request, pk=None):
        """搜索分组及其子分组下的所有实例"""
        try:
            group = self.get_object()
            logger.info(f'Searching instances in group {group.label}')

            group_ids = list(set(self._get_all_child_groups(group.id)))
            group_ids.append(group.id)
            logger.info(f'Found {len(group_ids)} groups in total')
            logger.info(f'Group IDs: {group_ids}')
            # 获取实例ID
            instance_ids = ModelInstanceGroupRelation.objects.filter(
                group_id__in=group_ids
            ).values_list('instance_id', flat=True)

            # 构建查询
            instances = ModelInstance.objects.filter(id__in=instance_ids)

            logger.info(f'Found {instances.count()} instances in total')
            # 分页
            paginator = StandardResultsSetPagination()
            paginated_instances = paginator.paginate_queryset(
                instances.order_by('id'),
                request
            )

            if paginated_instances is not None:
                serializer = ModelInstanceSerializer(
                    paginated_instances,
                    many=True,
                    context={'request': request}
                )
                return paginator.get_paginated_response(serializer.data)

            return Response([])

        except Exception as e:
            logger.error(f"Error searching instances: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@model_instance_group_relation_schema
class ModelInstanceGroupRelationViewSet(viewsets.ModelViewSet):
    queryset = ModelInstanceGroupRelation.objects.all().order_by('-create_time')
    # serializer_class = ModelInstanceGroupRelationSerializer
    pagination_class = StandardResultsSetPagination
    filterset_class = ModelInstanceGroupRelationFilter
    ordering_fields = ['create_time', 'update_time']
    http_method_names = ['get', 'post']

    def get_serializer_class(self):
        if self.action == 'create_relations':
            return BulkInstanceGroupRelationSerializer
        return ModelInstanceGroupRelationSerializer

    @action(detail=False, methods=['post'])
    def create_relations(self, request):
        """批量创建或更新实例分组关联"""
        logger.info(f"Creating or updating instance group relations")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        logger.debug(f"Data validated. Saving relations...")

        try:
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


# class RelationDefinitionViewSet(viewsets.ModelViewSet):
#     queryset = RelationDefinition.objects.all().order_by('-create_time')
#     serializer_class = RelationDefinitionSerializer


# class RelationsViewSet(viewsets.ModelViewSet):
#     queryset = Relations.objects.all().order_by('-create_time')
#     serializer_class = RelationsSerializer


@password_manage_schema
class PasswordManageViewSet(viewsets.ViewSet):

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


class ZabbixSyncHostViewSet(viewsets.ModelViewSet):
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

            hosts.update(agent_installed=False, installation_error=None)

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
                    setup_host_monitoring.delay(
                        str(host.instance.id),
                        host.name,
                        host.ip,
                        password,
                        force=force_flag)
                    logger.info(f"Triggered Zabbix agent installation for host {host.ip}")

                except Exception as e:
                    logger.error(f"Failed to trigger Zabbix agent installation for host {host.ip}: {str(e)}")
                    continue

            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error triggering Zabbix agent installation: {str(e)}")
            return Response(
                {'status': 'failed', 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def installation_status_sse(self, request):
        """使用SSE实时获取Zabbix客户端安装状态"""
        try:
            ids = request.query_params.get('ids', [])
            all_failed = request.query_params.get('all', False)

            if not ids and not all_failed:
                raise ValidationError('缺少sufficient params')

            if all_failed:
                ids = ZabbixSyncHost.objects.filter(agent_installed=False).values_list('id', flat=True)
                ids = [str(id) for id in ids]

            def event_stream():
                last_status = {}

                for _ in range(1200):
                    current_status = {}

                    hosts = ZabbixSyncHost.objects.filter(id__in=ids).values(
                        'id', 'host_id', 'ip', 'name', 'agent_installed',
                        'interface_available', 'installation_error', 'update_time'
                    )

                    all_completed = True

                    for host in hosts:
                        host_pk = str(host['id'])
                        current_status[host_pk] = host

                        if not host['agent_installed'] and not host['installation_error']:
                            all_completed = False

                    if current_status != last_status and current_status:
                        last_status = current_status.copy()
                        data = {
                            'status': 'success',
                            'hosts': list(current_status.values())
                        }
                        yield f"data: {data}\n\n"

                    if all_completed:
                        final_data = {
                            'status': 'completed',
                            'hosts': list(current_status.values())
                        }
                        yield f"data: {final_data}\n\n"
                        break

                    time.sleep(2)

            response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
            response['Cache-Control'] = 'no-cache'
            response['X-Accel-Buffering'] = 'no'
            return response

        except Exception as e:
            logger.error(f"Error in get installation status: {str(e)}")
            return Response({
                'status': 'error',
                'message': f'Error in get installation status: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
