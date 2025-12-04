import logging
import time
import uuid
import traceback
import re
import io
import tempfile
import networkx as nx

from django.conf import settings
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.metadata import BaseMetadata
from rest_framework.renderers import BaseRenderer, JSONRenderer
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.pagination import PageNumberPagination
from cacheops import cached_as, invalidate_model
from django.core.cache import cache
from django.http import StreamingHttpResponse
from django.core.exceptions import ImproperlyConfigured
from django.db import transaction
from django.db.models import Q
from django_redis import get_redis_connection
from celery.result import AsyncResult


from .utils import password_handler, celery_manager
from .excel import ExcelHandler
from .constants import FieldMapping, FieldType, limit_field_names
from .tasks import process_import_data, update_instance_names_for_model_template_change
from .filters import *
from .models import *
from .serializers import *
from .services import *
from .message import bulk_creation_audit
from .schemas import *
from audit.context import audit_context
from audit.mixins import AuditContextMixin
from permissions.manager import PermissionManager

logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = settings.REST_FRAMEWORK.get('PAGE_SIZE', 20)
    page_size_query_param = 'page_size'
    max_page_size = 1000


class CmdbBaseViewSet(AuditContextMixin, viewsets.ModelViewSet):
    """
    CMDB 应用专属的 ViewSet 基类。
    它自动集成了 AuditContextMixin，确保所有继承自它的 ViewSet都会被置于审计上下文中。
    同时，它还提供了基于当前用户的数据范围过滤功能，确保用户只能访问其有权限查看的数据。

    ** 子类必须通过 self.get_queryset() 方法获取查询集 **
    ** 子类重写get_queryset()方法时必须在首行调用 super().get_queryset() **
    ** 子类中禁止通过以下方法获取查询集，功能需要查询非权限内实例的需要转移到模型层设计为特权方法 **
    1. self.queryset（使用self.get_queryset()代替）
    2. Model.objects.all()（使用PermissionManager(user).get_queryset(Model)代替）
    3. Model.objects.filter()（使用PermissionManager(user).get_queryset(Model)代替）
    4. 定义了类级别的 queryset 后必须重写 get_queryset() 方法以确保权限过滤生效
    """
    pagination_class = StandardResultsSetPagination
    _visible_queryset = None

    def get_base_queryset(self):
        """
        特殊情况下提供的获取基础查询集的方法，子类可以重写此方法以动态生成基础查询集。
        ** 正常情况下只调用 super().get_queryset() 避免权限漏洞。 **
        """
        if not hasattr(self, 'queryset') or self.queryset is None:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} must define a 'queryset' attribute or override get_base_queryset()."
            )
        # 如果 queryset 是一个 QuerySet 对象，需要先克隆它以避免修改类属性
        if hasattr(self.queryset, '_clone'):
            return self.queryset._clone()
        return self.queryset

    def get_queryset(self):
        base_queryset = self.get_base_queryset()
        filtered_queryset = super().filter_queryset(base_queryset)
        return filtered_queryset

    def filter_queryset(self, queryset):
        """
        在被 DRF 意外调用时，防止DRF的默认行为绕过权限过滤。
        """
        # 直接返回已经完整过滤的 get_queryset 结果，确保数据源唯一。
        return self.get_queryset()

    def get_current_user(self):
        if self.request and hasattr(self.request, 'user'):
            return self.request.username
        return 'unknown'

    def perform_create(self, serializer):
        """在创建对象时，自动设置 create_user 和 update_user。"""
        username = self.get_current_user()
        serializer.save(create_user=username, update_user=username)
        return serializer.instance

    def perform_update(self, serializer):
        """在更新对象时，自动设置 update_user。"""
        username = self.get_current_user()
        serializer.save(update_user=username)


class CmdbReadOnlyBaseViewSet(AuditContextMixin, viewsets.ReadOnlyModelViewSet):
    """
    为只读视图提供的基类。
    """
    pagination_class = StandardResultsSetPagination

    def get_base_queryset(self):
        if not hasattr(self, 'queryset') or self.queryset is None:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} must define a 'queryset' attribute or override get_base_queryset()."
            )
        if hasattr(self.queryset, '_clone'):
            return self.queryset._clone()
        return self.queryset

    def get_queryset(self):
        base_queryset = self.get_base_queryset()
        filtered_queryset = super().filter_queryset(base_queryset)
        return filtered_queryset

    def filter_queryset(self, queryset):
        return self.get_queryset()

    def get_current_user(self):
        if self.request and hasattr(self.request, 'user'):
            return self.request.username
        return 'unknown'


@model_groups_schema
class ModelGroupsViewSet(CmdbBaseViewSet):
    queryset = ModelGroups.objects.all().order_by('create_time')
    serializer_class = ModelGroupsSerializer
    filterset_class = ModelGroupsFilter
    ordering_fields = ['name', 'built_in', 'editable', 'create_time', 'update_time']
    search_fields = ['name', 'description', 'create_user', 'update_user']

    def get_queryset(self):
        return super().get_queryset()

    def perform_destroy(self, instance):
        if instance.built_in:
            logger.warning(f"Attempt to delete built-in model group denied: {instance.name}")
            raise PermissionDenied({
                'detail': 'Built-in model group cannot be deleted'
            })
        if not instance.editable:
            logger.warning(f"Attempt to delete non-editable model group denied: {instance.name}")
            raise PermissionDenied({
                'detail': 'Non-editable model group cannot be deleted'
            })

        super().perform_destroy(instance)


@models_schema
class ModelsViewSet(CmdbBaseViewSet):
    queryset = Models.objects.all().order_by('create_time')
    serializer_class = ModelsSerializer
    filterset_class = ModelsFilter
    ordering_fields = ['name', 'type', 'create_time', 'update_time']
    search_fields = ['name', 'type', 'description', 'create_user', 'update_user']

    def get_queryset(self):
        return super().get_queryset()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance = ModelsService.create_model(
            validated_data=serializer.validated_data,
            user=self.request.user
        )

        if instance.instance_name_template:
            UniqueConstraintService.sync_from_instance_name_template(
                model=instance,
                instance_name_template=list(instance.instance_name_template),
                user=self.request.user,
                audit_ctx=self.get_audit_context()
            )

        # 重新序列化返回结果
        return Response(
            self.get_serializer(instance).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        old_instance_name_template = list(instance.instance_name_template) if instance.instance_name_template else []

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        instance = self.get_object()  # 获取更新后的实例

        logger.debug(f'user {self.request.user} type {type(self.request.user)}')

        new_instance_name_template = list(instance.instance_name_template) if instance.instance_name_template else []
        if old_instance_name_template != new_instance_name_template:
            UniqueConstraintService.sync_from_instance_name_template(
                model=instance,
                instance_name_template=new_instance_name_template,
                user=self.request.user,
                audit_ctx=self.get_audit_context()
            )

        return Response(
            self.get_serializer(instance).data,
            status=status.HTTP_200_OK
        )

    def perform_destroy(self, instance):
        ModelsService.delete_model(
            model=instance,
            user=self.request.user
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        pm = PermissionManager(user=self.request.username)
        field_groups_qs = pm.get_queryset(ModelFieldGroups).filter(model=instance).order_by('create_time')
        fields_qs = pm.get_queryset(ModelFields).filter(model=instance).order_by('order')

        model_data = self.get_serializer(instance).data
        field_groups_data = ModelFieldGroupsSerializer(field_groups_qs, many=True).data
        fields_data = ModelFieldsSerializer(fields_qs, many=True).data

        data = ModelsService.get_model_details(model_data, field_groups_data, fields_data)
        return Response(data, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        page = self.paginate_queryset(queryset)
        models_list = page if page is not None else list(queryset)

        if not models_list:
            return self.get_paginated_response([]) if page is not None else Response([])

        model_ids = [m.id for m in models_list]
        pm = PermissionManager(user=self.request.username)

        field_groups_qs = pm.get_queryset(ModelFieldGroups).filter(model_id__in=model_ids).order_by('create_time')
        fields_qs = pm.get_queryset(ModelFields).filter(model_id__in=model_ids).order_by('order')
        instances_qs = pm.get_queryset(ModelInstance).filter(model_id__in=model_ids)

        models_data = ModelsSerializer(models_list, many=True).data
        field_groups_data = ModelFieldGroupsSerializer(field_groups_qs, many=True).data
        fields_data = ModelFieldsSerializer(fields_qs, many=True).data

        enriched_data = ModelsService.enrich_models_list(models_data, field_groups_data, fields_data, instances_qs)

        return self.get_paginated_response(enriched_data) if page is not None else Response(enriched_data)

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

    def get_queryset(self):
        return super().get_queryset()

    def perform_destroy(self, instance):
        ModelFieldGroupsService.delete_field_group(instance, user=self.request.user)


@validation_rules_schema
class ValidationRulesViewSet(CmdbBaseViewSet):
    queryset = ValidationRules.objects.all()
    serializer_class = ValidationRulesSerializer
    filterset_class = ValidationRulesFilter
    ordering_fields = ['name', 'field_type', 'type', 'create_time', 'update_time']
    search_fields = ['name', 'type', 'description', 'rule']

    def get_queryset(self):
        return super().get_queryset()

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

    def get_queryset(self):
        return super().get_queryset()

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

    def get_queryset(self):
        return super().get_queryset()

    def list(self, request, *args, **kwargs):
        username = self.get_current_user()
        model = request.query_params.get('model')
        if username and model:
            model = Models.objects.get(id=model)
            preference = ModelFieldPreference.objects.filter(model=model, create_user=username).first()
            if not preference:
                preference = ModelFieldPreferenceService.create_default_user_preference(model, self.request.user)
            return Response(ModelFieldPreferenceSerializer(preference).data, status=status.HTTP_200_OK)
        else:
            return Response([], status=status.HTTP_200_OK)


@unique_constraint_schema
class UniqueConstraintViewSet(CmdbBaseViewSet):
    queryset = UniqueConstraint.objects.all().order_by('-create_time')
    serializer_class = UniqueConstraintSerializer
    filterset_class = UniqueConstraintFilter
    ordering_fields = ['model', 'create_time', 'update_time']

    def get_queryset(self):
        # 根据请求用户的字段权限过滤唯一约束
        model_id = self.request.query_params.get('model')
        pm = PermissionManager(self.request.user)
        query = Q()
        if model_id:
            query &= Q(model_id=model_id)

        fields = pm.get_queryset(ModelFields).filter(query).values_list('id', flat=True)
        field_ids = set(str(fid) for fid in fields)
        queryset = super().get_base_queryset()
        for constraint in queryset:
            if not set(constraint.fields).issubset(field_ids):
                queryset = queryset.exclude(id=constraint.id)
        return queryset

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
    queryset = ModelInstance.objects.all().order_by('-create_time')
    serializer_class = ModelInstanceSerializer
    filterset_class = ModelInstanceFilter
    ordering_fields = ['create_time', 'update_time']
    search_fields = ['model', 'instance_name', 'create_user', 'update_user']

    def _get_serializer_context_for_instances(self, instances):
        base_context = self.get_serializer_context()
        read_context = ModelInstanceService.get_read_context(instances, self.request.user)
        base_context.update(read_context)

        return base_context

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        context = self._get_serializer_context_for_instances([instance])
        serializer = self.get_serializer(instance, context=context)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
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
        params = filter_params.copy()
        query = Q()

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

        # 过滤ModelInstance字段
        if standard_fields:
            filterset = ModelInstanceFilter(standard_fields, queryset=queryset)
            queryset = filterset.qs

        # 过滤动态字段
        for field_name, field_value in filter_params.items():
            # 忽略特殊参数
            if field_name in limit_field_names:
                continue

            try:
                if isinstance(field_value, str):
                    if field_value.startswith('like:'):
                        value = field_value[5:]
                        query &= Q(data__icontains=value)
                    elif field_value.startswith('in:'):
                        values = field_value[3:].split(',')
                        query &= Q(data__in=values)
                    elif field_value.startswith('regex:'):
                        pattern = field_value[6:]
                        query &= Q(data__regex=pattern)
                    elif field_value.startswith('not:'):
                        # 反选匹配
                        value = field_value[4:]
                        if value.startswith('like:'):
                            v = value[5:]
                            query &= ~Q(data__icontains=v)
                        elif value.startswith('in:'):
                            v = value[3:].split(',')
                            query &= ~Q(data__in=v)
                        elif value.startswith('regex:'):
                            pattern = value[6:]
                            query &= ~Q(data__regex=pattern)
                        else:
                            if value == 'null':
                                query &= ~Q(data__isnull=True)
                            else:
                                query &= ~Q(data=value)
                    else:
                        if value == 'null':
                            query &= Q(data__isnull=True)
                        else:
                            query &= Q(data=field_value)

            except ModelFields.DoesNotExist:
                logger.warning(f"Field not found: {field_name}")
                continue
            except Exception as e:
                logger.error(f"Error processing field {field_name}: {traceback.format_exc()}")
                continue

        queryset = queryset.filter(query)
        return queryset

    # @cached_as(ModelInstance, timeout=600)
    def get_queryset(self):
        queryset = super().get_queryset().order_by('-create_time').select_related('model')

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

    def create(self, request, *args, **kwargs):
        request.data['input_mode'] = 'manual'

        model_id = request.data.get('model')
        if not model_id:
            raise ValidationError({'detail': 'Model ID is required'})
        pm = PermissionManager(user=self.request.user)
        model = pm.get_queryset(Models).get(id=model_id)
        if not model:
            raise ValidationError({'detail': f'Model {model_id} not found for user {self.request.user.username}'})

        context = self.get_serializer_context()
        write_context = ModelInstanceService.get_write_context(
            model,
            request.data.get('fields', {}),
            self.request.user
        )
        context.update(write_context)

        serializer = self.get_serializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)

        # 获取分组
        instance_group_ids = request.data.get('instance_group', [])
        if isinstance(instance_group_ids, str):
            instance_group_ids = [instance_group_ids]

        # 创建实例
        instance = ModelInstanceService.create_instance(
            validated_data=serializer.validated_data,
            user=self.request.user,
            instance_group_ids=instance_group_ids
        )

        # 重新获取完整数据用于返回
        context = self._get_serializer_context_for_instances([instance])
        return Response(
            self.get_serializer(instance, context=context).data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # 调用 Service 更新实例
        updated_instance = ModelInstanceService.update_instance(
            instance=instance,
            validated_data=serializer.validated_data,
            user=self.request.user
        )

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        context = self._get_serializer_context_for_instances([updated_instance])
        return Response(self.get_serializer(updated_instance, context=context).data)

    @action(detail=False, methods=['patch'])
    def bulk_update_fields(self, request):
        instance_ids = request.data.get('instances', [])
        model_id = request.data.get('model')
        fields_data = request.data.get('fields', {})
        filter_by_params = request.data.get('all', False)
        params = request.data.get('params', {})
        group_id = request.data.get('group')
        using_template = request.data.get('using_template')

        if group_id:
            params['model_instance_group'] = group_id

        if filter_by_params and params:
            instances = self.get_queryset().all()
            instances = self._apply_filters(instances, model_id, params)
        elif instance_ids:
            instances = self.get_queryset().filter(id__in=instance_ids)
        else:
            raise ValidationError("Insufficient query parameters provided.")

        if not instances.exists():
            raise ValidationError("No instances found with the provided criteria.")

        # 批量更新必须针对同一模型
        first_instance = instances.first()
        target_model_id = first_instance.model_id

        # 如果前端没传 model_id，使用实例的 model_id
        if not model_id:
            model_id = str(target_model_id)

        if instances.filter(model_id=target_model_id).count() != instances.count():
            raise ValidationError("Instances belong to multiple models; bulk update requires a single model.")

        # 调用 Serializer 进行数据校验
        validation_data = {
            'model': model_id,
            'fields': fields_data
        }

        serializer = self.get_serializer(data=validation_data, partial=True)
        try:
            serializer.is_valid(raise_exception=True)
            validated_fields = serializer.validated_data.get('fields', {})
        except ValidationError as e:
            logger.error(f"Bulk update validation failed: {e}")
            raise e

        # 记录审计信息并执行批量更新
        correlation_id = str(uuid.uuid4())
        with audit_context(correlation_id=correlation_id):
            updated_count = ModelInstanceService.bulk_update_instances(
                instances_qs=instances,
                validated_fields=validated_fields,
                user=self.request.user,
                using_template=using_template
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
            model_id = request.data.get('model')
            if not model_id:
                raise ValidationError({'detail': 'Model ID is required'})

            pm = PermissionManager(user=self.request.user)
            model = pm.get_queryset(Models).get(id=model_id)
            fields = pm.get_queryset(ModelFields).filter(
                model=model
            ).select_related(
                'validation_rule',
                'model_field_group',
                'ref_model'
            ).order_by('model_field_group__create_time', 'order')

            # 生成 Excel 模板
            excel_handler = ExcelHandler()
            workbook = excel_handler.generate_template(fields)

            excel_file = io.BytesIO()
            workbook.save(excel_file)
            excel_file.seek(0)

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
        """
        导出实例数据。
        导出格式与导入模板一致，包含枚举/引用的锁定 sheet。
        """
        try:
            instance_ids = request.data.get('instances', [])
            model_id = request.data.get('model')
            filter_by_params = request.data.get('all', False)
            params = request.data.get('params', {})
            group_id = request.data.get('group')
            restricted_fields = request.data.get('fields', [])

            if not model_id:
                raise ValidationError({'detail': 'Model ID is required'})

            pm = PermissionManager(user=self.request.user)
            model = pm.get_queryset(Models).get(id=model_id)

            # 构建实例查询集
            instances = self.get_queryset().filter(model_id=model_id)

            if group_id:
                params['model_instance_group'] = group_id

            if filter_by_params and params:
                instances = self._apply_filters(instances, model_id, params)
            elif instance_ids:
                instances = instances.filter(id__in=instance_ids)

            if not instances.exists():
                raise ValidationError("No instances found with the provided criteria.")

            # 获取字段查询集
            fields_qs = pm.get_queryset(ModelFields).filter(model=model)

            # 调用服务层导出数据
            export_result = ModelInstanceService.export_instances_data(
                model=model,
                instances_qs=instances,
                fields_qs=fields_qs,
                user=self.request.user,
                restricted_field_names=restricted_fields if restricted_fields else None
            )

            if not export_result['fields']:
                raise ValidationError({'detail': 'No fields available for export'})

            # 生成 Excel 文件（复用模板格式）
            excel_handler = ExcelHandler()
            workbook = excel_handler.generate_data_export_with_template(
                fields=export_result['fields'],
                instances_data=export_result['instances_data'],
                enum_data=export_result['enum_data'],
                ref_data=export_result['ref_data']
            )

            excel_file = io.BytesIO()
            workbook.save(excel_file)
            excel_file.seek(0)

            headers = {
                'Content-Disposition': f'attachment; filename="{model.name}_data.xlsx"'
            }

            logger.info(
                f"Data exported successfully for model: {model.name}, instances: {len(export_result['instances_data'])}")

            return Response(
                {
                    'filename': f"{model.name}_data.xlsx",
                    'file_content': excel_file.getvalue()
                },
                status=status.HTTP_200_OK,
                headers=headers
            )

        except Models.DoesNotExist:
            raise ValidationError({'detail': f'Model {model_id} not found'})
        except Exception as e:
            logger.error(f"Error exporting data: {traceback.format_exc()}")
            raise ValidationError({'detail': f'Failed to export data: {str(e)}'})

    @action(detail=False, methods=['post'])
    def import_data(self, request):
        file = request.FILES.get('file')
        model_id = request.data.get('model')

        if not file or not model_id:
            raise ValidationError({'detail': 'Missing file or model ID'})

        results = {'cache_key': None}

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

            headers = excel_data.get('headers', [])
            pm = PermissionManager(user=request.user)
            model = pm.get_queryset(Models).get(id=model_id)

            if not model:
                raise ValidationError({'detail': f'Model {model_id} not found for current user'})

            warning_msg = ''

            # 检查实例权限
            disarded_instance_names = []
            instance_names_query = pm.get_queryset(ModelInstance).filter(
                model=model).values_list('instance_name', flat=True)
            for instance_name in excel_data.get('instance_names', []):
                if ModelInstance.objects.check_instance_name_exists(model_id, instance_name) and instance_name not in instance_names_query:
                    logger.warning(f'Discarding instance name without permission: {instance_name}...')
                    disarded_instance_names.append(instance_name)
            if disarded_instance_names:
                warning_msg = f'Discarded instance names without permission: {", ".join(disarded_instance_names)}'

            # 检查是否有未知字段
            fields_query = pm.get_queryset(ModelFields).filter(model=model).values_list('name', flat=True)
            unknown_fields = set(headers) - set(fields_query)
            if unknown_fields:
                logger.warning(f'Discarding unknown fields in import: {unknown_fields}...')
                if warning_msg:
                    warning_msg += '; '
                warning_msg += f'Unknown fields in Excel: {", ".join(unknown_fields)}'

            if not celery_manager.check_heartbeat():
                raise ValidationError({'detail': 'Celery worker is not available'})

            audit_ctx = self.get_audit_context()
            logger.debug(f'Audit context for import: {audit_ctx}')
            task = process_import_data.delay(
                excel_data,
                model_id,
                str(request.user.id),
                audit_ctx
            )

            cache_key = f'import_task_{task.id}'
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

            results['cache_key'] = cache_key
            if warning_msg:
                results['warning'] = warning_msg
            return Response(results, status=status.HTTP_200_OK)

        except Models.DoesNotExist:
            raise ValidationError({'detail': f'Model {model_id} not found'})
        except Exception as e:
            logger.error(f"Error loading Excel data: {traceback.format_exc()}")
            raise ValidationError({'detail': f'Failed to load Excel data: {str(e)}'})
        finally:
            import os
            if os.path.exists(temp_path):
                os.remove(temp_path)

    @action(detail=False, methods=['post'])
    def _import_data(self, request):
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

            pm = PermissionManager(user=self.request.username)

            model = pm.get_queryset(Models).get(id=model_id)

            if not model:
                raise ValidationError({'detail': f'Model {model_id} not found for current user'})

            fields_query = pm.get_queryset(ModelFields).filter(model=model).values_list('name', flat=True)
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
        pm = PermissionManager(user=self.request.username)

        groups = pm.get_queryset(ModelInstanceGroupRelation).filter(instance=instance).values_list('group', flat=True)
        groups = pm.get_queryset(ModelInstanceGroup).filter(id__in=groups)
        if '空闲池' not in groups.values_list('label', flat=True):
            raise PermissionDenied({'detail': 'Instance is not in unassigned group'})
        instance.delete()

    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        instance_ids = request.data.get('instances', [])
        model_id = request.data.get('model')
        filter_by_params = request.data.get('all', False)
        params = request.data.get('params', {})
        group_id = request.data.get('group')
        instances = self.get_queryset().all()
        pm = PermissionManager(user=self.request.username)
        if group_id:
            group = pm.get_queryset(ModelInstanceGroup).get(id=group_id)
            if group and group.label != '空闲池' and group.path != '所有/空闲池':
                raise ValidationError({'detail': 'Instances not in the unassigned group cannot be deleted'})
            instance_in_group = pm.get_queryset(ModelInstanceGroupRelation).filter(
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

            unassigned_group = ModelInstanceGroup.objects.get_unassigned_group(model_id)
            relations = pm.get_queryset(ModelInstanceGroupRelation).filter(instance__in=valid_id)
            group_invalid_ids = relations.exclude(group=unassigned_group).values_list('instance_id', flat=True)
            invalid_id = {instance_id: 'Instance is not in unassigned group' for instance_id in group_invalid_ids}

            if ModelFields.objects.check_ref_fields_exists(model_id):
                for instance in instances:
                    if ModelFieldMeta.objects.check_data_exists(str(instance.id)):
                        invalid_id[instance.id] = 'Referenced by other model field meta'
            valid_id = set(valid_id) - set(invalid_id.keys())

            self.get_queryset().filter(id__in=valid_id).delete()
            return Response({
                'success': len(valid_id),
                'errors': list(invalid_id)
            }, status=status.HTTP_200_OK)
        except Exception as e:
            raise ValidationError(f'Error deleting instances: {str(e)}')

    @action(detail=False, methods=['post'])
    def search(self, request):
        """
        全文检索实例数据

        使用 MySQL FULLTEXT 索引进行高效搜索，支持：
        - 跨模型搜索
        - 枚举 key/value 自动转换
        - 引用字段 instance_name/instance_id 自动转换
        - 中文分词（ngram）

        请求体:
        {
            "query": "搜索关键词",
            "models": ["model_id1", "model_id2"],  // 可选，限定搜索模型
            "limit": 100,  // 可选，默认100，最大500
            "threshold": 0.0,  // 可选，相似度阈值，默认0
            "search_mode": "boolean"  // 可选：natural/boolean/expansion
        }
        """
        query = request.data.get('query', '')
        model_ids = request.data.get('models', [])
        limit = request.data.get('limit', 100)
        threshold = request.data.get('threshold', 0.0)
        search_mode = request.data.get('search_mode', 'boolean')
        logger.debug(f"Search request: query={query}, models={model_ids}, limit={limit}, "
                     f"threshold={threshold}, search_mode={search_mode}")
        if not query:
            raise ValidationError({'detail': 'Search query is required'})

        # 参数验证
        try:
            limit = max(1, min(int(limit), 500))
            threshold = max(0.0, min(float(threshold), 0.0))
        except (ValueError, TypeError):
            raise ValidationError({'detail': 'Invalid limit or threshold value'})

        if search_mode not in ('natural', 'boolean', 'expansion'):
            search_mode = 'boolean'

        result = ModelFieldMetaSearchService.search(
            query=query,
            user=self.request.user,
            model_ids=model_ids if model_ids else None,
            limit=limit,
            threshold=threshold,
            search_mode=search_mode
        )

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def quick_search(self, request):
        """
        快速搜索（GET 方式，适合前端搜索框/自动补全）

        查询参数:
        - q: 搜索关键词（必填）
        - model: 模型ID（可选）
        - limit: 返回数量（可选，默认20，最大100）
        """
        query = request.query_params.get('query', '')
        model_id = request.query_params.get('model')
        limit = request.query_params.get('limit', 20)

        if not query:
            return Response({
                'results': [],
                'total': 0,
                'query': ''
            })

        try:
            limit = max(1, min(int(limit), 100))
        except (ValueError, TypeError):
            limit = 20

        result = ModelFieldMetaSearchService.search(
            query=query,
            user=self.request.user,
            model_ids=[model_id] if model_id else None,
            limit=limit,
            threshold=0.0,
            search_mode='boolean',
            quick=True
        )

        # 简化返回结果，适合下拉框展示
        simplified_results = []
        for item in result['results']:
            best_match = item['matches'][0] if item['matches'] else None
            simplified_results.append({
                'instance_id': item['instance_id'],
                'instance_name': item['instance_name'],
                'model_id': item['model_id'],
                'model_name': item['model_verbose_name'] or item['model_name'],
                'matched_field': best_match['field_verbose_name'] if best_match else None,
                'matched_value': best_match['display_value'] if best_match else None,
                'score': item['max_score']
            })

        return Response({
            'results': simplified_results,
            'total': result['total'],
            'query': query
        })


@model_ref_schema
class ModelInstanceBasicViewSet(CmdbReadOnlyBaseViewSet):
    serializer_class = ModelInstanceBasicViewSerializer
    queryset = ModelInstance.objects.all().order_by('-create_time')
    filterset_class = ModelInstanceBasicFilter
    search_fields = ['model', 'instance_name', 'create_user', 'update_user']
    ordering_fields = ['name', 'create_time', 'update_time']

    def get_queryset(self):
        return super().get_queryset()


# 禁止通过API直接操作字段数据
# @model_field_meta_schema
# class ModelFieldMetaViewSet(CmdbBaseViewSet):
#     queryset = ModelFieldMeta.objects.all().order_by('-create_time')
#     serializer_class = ModelFieldMetaSerializer
#     filterset_class = ModelFieldMetaFilter
#     ordering_fields = ['create_time', 'update_time']


@model_instance_group_schema
class ModelInstanceGroupViewSet(CmdbBaseViewSet):
    queryset = ModelInstanceGroup.objects.all().order_by('create_time')
    serializer_class = ModelInstanceGroupSerializer
    pagination_class = None
    filterset_class = ModelInstanceGroupFilter
    ordering_fields = ['label', 'order', 'path', 'create_time', 'update_time']

    def get_queryset(self):
        queryset = super().get_queryset()
        model_id = self.request.query_params.get('model')

        if model_id:
            queryset = queryset.filter(model_id=model_id)
            logger.debug(f"Filtering groups by model: {model_id}")
        try:
            if self.action in ['retrieve', 'update', 'partial_update', 'destroy', 'list']:
                return queryset.select_related('model', 'parent')
            if self.action in ['add_instances', 'remove_instances', 'search_instances']:
                return queryset

            return queryset

        except Exception as e:
            logger.error(f"Error in get_queryset: {str(e)}")
            return ModelInstanceGroup.objects.none()

    def list(self, request, *args, **kwargs):
        try:
            model_id = request.query_params.get('model')

            # 获取所有模型的分组树
            if not model_id:
                tree_structure, context = ModelInstanceGroupService.build_model_groups_tree(self.request.user)
                response_data = []
                for group_item in tree_structure:
                    model_group = group_item['model_group']
                    models_list = []

                    for model_item in group_item['models']:
                        model = model_item['model']
                        groups = model_item['groups']

                        # 调用序列化器
                        groups_data = ModelInstanceGroupSerializer(
                            groups,
                            many=True,
                            context=context
                        ).data

                        models_list.append({
                            'model_id': str(model.id),
                            'model_name': model.name,
                            'model_verbose_name': model.verbose_name,
                            'groups': groups_data
                        })

                    response_data.append({
                        'model_group_id': str(model_group.id),
                        'model_group_name': model_group.name,
                        'model_group_verbose_name': model_group.verbose_name,
                        'models': models_list
                    })

                return Response(response_data)

            # 获取特定模型的分组树
            root_node, context = ModelInstanceGroupService.get_single_model_group_tree(model_id, self.request.user)

            if not root_node:
                return Response({}, status=status.HTTP_200_OK)

            serializer = self.get_serializer(root_node, context=context)
            return Response(serializer.data)

        except Exception as e:
            logger.error(f"Error in list view: {traceback.format_exc()}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        target_id = request.data.get('target_id')
        position = request.data.get('position')

        if target_id and position:
            ModelInstanceGroupService.update_group_position(
                instance, target_id, position, self.request.user
            )

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
            return Response(serializer.data)

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            result = ModelInstanceGroupService.delete_group(instance, self.request.user)

            return Response({
                'message': f'Successfully deleted group {instance.label} and its children',
                **result
            }, status=status.HTTP_200_OK)

        except (ModelInstanceGroup.DoesNotExist, PermissionDenied) as e:
            raise e
        except Exception as e:
            logger.error(f"Error deleting group: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def tree(self, request):
        model_id = request.query_params.get('model')
        model = Models.objects.filter(id=model_id).first()
        if not model:
            return Response({'detail': f'Model {model_id} not found'}, status=status.HTTP_404_NOT_FOUND)
        root_nodes, context = ModelInstanceGroupService.get_tree(model, request.user)
        data = ModelInstanceGroupTreeSerializer(root_nodes, many=True, context=context).data
        return Response(data, status=status.HTTP_200_OK)


@model_instance_group_relation_schema
class ModelInstanceGroupRelationViewSet(CmdbBaseViewSet):
    queryset = ModelInstanceGroupRelation.objects.all().order_by('-create_time')
    # serializer_class = ModelInstanceGroupRelationSerializer
    filterset_class = ModelInstanceGroupRelationFilter
    ordering_fields = ['create_time', 'update_time']
    http_method_names = ['get', 'post']

    def get_queryset(self):
        return super().get_queryset()

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

    def get_queryset(self):
        return super().get_queryset()

    def perform_destroy(self, instance):
        # 检查关系定义是否已被使用
        if Relations.objects.filter(relation=instance).exists():
            logger.warning(f"Trying to delete a relation definition in use: {instance.name}")
            raise PermissionDenied(
                "This relation definition is in use by at least one relation instance and cannot be deleted.")
        logger.info(f"Relation definition '{instance.name}' has been deleted.")
        super().perform_destroy(instance)


class RelationsViewSet(CmdbBaseViewSet):
    queryset = Relations.objects.all().select_related(
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

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'source_instance__model', 'target_instance__model', 'relation'
        ).order_by('-create_time')

        return queryset

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
            created_objects = Relations.objects.bulk_create(relations_to_create, ignore_conflicts=True)
            bulk_creation_audit.send(sender=Relations, instances=created_objects)

            return Response(
                {
                    "created_count": len(created_objects)
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.error(f"Error creating relations: {e}", exc_info=True)
            raise ValidationError(f"Failed to create relations: {e}")

    @action(detail=False, methods=['post'])
    def bulk_create(self, request, *args, **kwargs):
        """
        批量创建多个关联关系。
        接收一个包含多个关系定义的列表。
        数据格式: {"relations": [{"source_instance": "uuid", "target_instance": "uuid", "relation": "uuid", ...}]}
        """
        relations_data = request.data.get('relations', [])
        if not isinstance(relations_data, list) or not relations_data:
            raise ValidationError("A non-empty list of relations is required.")

        serializer = self.get_serializer(data=relations_data, many=True)
        serializer.is_valid(raise_exception=True)

        user = self.get_current_user()
        relations_to_create = []

        for relation_data in serializer.validated_data:
            relation_data['create_user'] = user
            relation_data['update_user'] = user
            relations_to_create.append(Relations(**relation_data))

        try:
            created_objects = Relations.objects.bulk_create(relations_to_create, ignore_conflicts=True)
            bulk_creation_audit.send(sender=Relations, instances=created_objects)

            return Response(
                {
                    "created_count": len(created_objects)
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.error(f"Error occurred while bulk creating relations: {e}", exc_info=True)
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

            logger.info(f"Processing topology query with mode: {mode}, depth: {depth}, direction: {direction}")

            G = self._build_graph_on_demand(
                start_node_ids, end_node_ids, depth, direction, mode
            )

            logger.info(f"Graph constructed with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")

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
        path_graph = nx.DiGraph()

        for start_node in start_node_ids:
            for end_node in end_node_ids:
                if G.has_node(start_node) and G.has_node(end_node):
                    try:
                        self._filter_path_edges(G, start_node, end_node, depth, path_graph)
                    except nx.NetworkXNoPath:
                        continue
        return path_graph

    def _find_blast_neighbors(self, start_node_ids, end_node_ids, direction, depth):
        """
        在图G中查找从start_node_ids出发，按照direction方向，深度为depth的邻接节点。
        如果提供了end_node_ids，则只返回包含这些终点的子图。
        """
        graph = nx.DiGraph()
        queue = set(start_node_ids)
        seen_nodes = set()

        logger.info(
            f"Finding blast neighbors from nodes: {start_node_ids} with depth: {depth} and direction: {direction}")
        for _ in range(depth):
            if not queue:
                break
            logger.info(f"Current queue: {queue}")
            current_level_nodes = list(queue)
            seen_nodes.update(current_level_nodes)
            queue.clear()

            q_filter = Q()
            if direction in ('forward', 'both'):
                q_filter |= Q(source_instance_id__in=current_level_nodes)
            if direction in ('reverse', 'both'):
                q_filter |= Q(target_instance_id__in=current_level_nodes)

            relations_qs = Relations.objects.filter(q_filter).select_related(
                'source_instance', 'target_instance', 'relation')
            logger.info(f"Found {relations_qs.count()} relations at current depth")
            newly_found_nodes = self._add_edges_to_graph(graph, relations_qs)
            logger.info(f"Newly found nodes: {newly_found_nodes}")
            queue.update(newly_found_nodes - seen_nodes)

        if not end_node_ids:
            return graph

        path_subgraph = self._find_path_between_nodes(graph, start_node_ids, end_node_ids, depth)
        return path_subgraph

    def _build_graph_on_demand(self, start_node_ids, end_node_ids, depth, direction, mode):
        """
        按需从数据库查询数据来构建图，避免一次性加载所有数据。
        """
        G = nx.DiGraph()
        logger.info(f"Building graph on demand with mode: {mode}")
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
            G = self._find_blast_neighbors(start_node_ids, end_node_ids, direction, depth)

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
                G.add_edge(target_id, source_id, relation=rel)  # 添加反向边以模拟无向

        return new_nodes


@password_manage_schema
class PasswordManageViewSet(CmdbBaseViewSet):

    @action(detail=False, methods=['post'])
    def re_encrypt(self, request):
        """重新加密密码"""
        username = self.get_current_user()
        if username != 'admin':
            raise PermissionDenied("Only admin can perform password re-encryption.")
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
        username = self.get_current_user()
        if username != 'admin':
            raise PermissionDenied("Only admin can perform password reset.")
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
        username = self.get_current_user()
        if username != 'admin':
            raise PermissionDenied("Only admin can perform cache clearing.")
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
