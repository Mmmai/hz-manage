import logging

from collections import defaultdict
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.db.models import Q

from mapi.models import UserInfo, UserGroup, Role
from .tools import clear_data_scope_cache
from .models import DataScope
from .serializers import DataScopeSerializer

logger = logging.getLogger(__name__)


class DataScopeViewSet(ModelViewSet):
    queryset = DataScope.objects.all().prefetch_related('targets', 'targets__content_type')
    serializer_class = DataScopeSerializer
    filterset_fields = ['role', 'user', 'user_group', 'scope_type']
    search_fields = ['description']
    ordering_fields = ['create_time', 'update_time']

    def _build_target_key(self, target) -> str:
        """构建 target 的唯一标识 key"""
        return f"{target.content_type.app_label}.{target.content_type.model}"

    def _get_targets_detail(self, instance) -> dict:
        """获取单个 DataScope 实例的 targets 详情"""
        targets_detail = defaultdict(list)
        for target in instance.targets.all():
            key = self._build_target_key(target)
            targets_detail[key].append(str(target.object_id))
        return dict(targets_detail)

    def _get_targets_detail_map(self, queryset) -> dict:
        """批量构建 targets 详情映射"""
        logger.debug(f'Building targets detail map for queryset of size: {len(queryset)}')
        targets_map = {}

        for scope in queryset:
            logger.debug(f'Processing DataScope ID: {scope.id}')
            targets_map[str(scope.id)] = self._get_targets_detail(scope)

        logger.debug(f'Constructed targets detail map with {len(targets_map)} entries')
        return targets_map

    def _format_response_data(self, data, targets_map: dict):
        """格式化响应数据，添加 targets_detail"""
        if isinstance(data, list):
            for item in data:
                item['targets_detail'] = targets_map.get(item.get('id'), {})
        else:
            data['targets_detail'] = targets_map.get(data.get('id'), {})
        return data

    def _build_response_with_targets(self, instance):
        """构建带 targets 详情的响应数据"""
        serializer = self.get_serializer(instance)
        targets_map = self._get_targets_detail_map([instance])
        return self._format_response_data(serializer.data, targets_map)

    def _collect_scopes_for_user(self, user) -> list:
        """
        收集用户相关的所有 DataScope（直接权限 + 用户组权限 + 角色权限）
        返回格式：[{scope, owner_type, owner_id, owner_name}]
        """
        scopes_with_sources = []

        # 用户直接权限
        user_scopes = DataScope.objects.filter(user=user).prefetch_related(
            'targets', 'targets__content_type'
        )
        for scope in user_scopes:
            scopes_with_sources.append({
                'scope': scope,
                'owner_type': 'user',
                'owner_id': str(user.id),
                'owner_name': user.username,
            })

        # 用户组权限
        user_groups = user.groups.all()
        for group in user_groups:
            group_scopes = DataScope.objects.filter(user_group=group).prefetch_related(
                'targets', 'targets__content_type'
            )
            for scope in group_scopes:
                scopes_with_sources.append({
                    'scope': scope,
                    'owner_type': 'user_group',
                    'owner_id': str(group.id),
                    'owner_name': group.group_name
                })

            # 用户组关联的角色权限
            group_roles = group.roles.all()
            for role in group_roles:
                role_scopes = DataScope.objects.filter(role=role).prefetch_related(
                    'targets', 'targets__content_type'
                )
                for scope in role_scopes:
                    scopes_with_sources.append({
                        'scope': scope,
                        'owner_type': 'role',
                        'owner_id': str(role.id),
                        'owner_name': role.role_name
                    })

        # 用户直接关联的角色权限
        user_roles = user.roles.all()
        for role in user_roles:
            role_scopes = DataScope.objects.filter(role=role).prefetch_related(
                'targets', 'targets__content_type'
            )
            for scope in role_scopes:
                scopes_with_sources.append({
                    'scope': scope,
                    'owner_type': 'role',
                    'owner_id': str(role.id),
                    'owner_name': role.role_name
                })

        return scopes_with_sources

    def _collect_scopes_for_user_group(self, user_group) -> list:
        """收集用户组相关的所有 DataScope（直接权限 + 角色权限）"""
        scopes_with_sources = []

        # 用户组直接权限
        group_scopes = DataScope.objects.filter(user_group=user_group).prefetch_related(
            'targets', 'targets__content_type'
        )
        for scope in group_scopes:
            scopes_with_sources.append({
                'scope': scope,
                'owner_type': 'user_group',
                'owner_id': str(user_group.id),
                'owner_name': user_group.group_name
            })

        # 用户组关联的角色权限
        group_roles = user_group.roles.all()
        for role in group_roles:
            role_scopes = DataScope.objects.filter(role=role).prefetch_related(
                'targets', 'targets__content_type'
            )
            for scope in role_scopes:
                scopes_with_sources.append({
                    'scope': scope,
                    'owner_type': 'role',
                    'owner_id': str(role.id),
                    'owner_name': role.role_name
                })

        return scopes_with_sources

    def _collect_scopes_for_role(self, role) -> list:
        """收集角色相关的所有 DataScope"""
        scopes_with_sources = []

        role_scopes = DataScope.objects.filter(role=role).prefetch_related(
            'targets', 'targets__content_type'
        )
        for scope in role_scopes:
            scopes_with_sources.append({
                'scope': scope,
                'owner_type': 'role',
                'owner_id': str(role.id),
                'owner_name': role.role_name
            })

        return scopes_with_sources

    def _aggregate_permissions_to_list(self, scopes_with_sources: list) -> list:
        """
        将权限聚合为列表格式

        返回格式：
        [
            {
                "app_label": "cmdb",
                "model": "model_instance",
                "target": "obj_id",
                "owner_type": "user",
                "owner_id": "111",
                "owner_name": "test",
                "scope_type": "read"
            },
            ...
        ]

        每个权限来源单独一条记录
        """
        result = []

        for item in scopes_with_sources:
            scope = item['scope']
            owner_type = item['owner_type']
            owner_id = item['owner_id']
            owner_name = item['owner_name']

            for target in scope.targets.all():
                record = {
                    'app_label': target.content_type.app_label,
                    'model': target.content_type.model,
                    'target': str(target.object_id),
                    'owner_type': owner_type,
                    'owner_id': owner_id,
                    'owner_name': owner_name,
                    'scope_type': scope.scope_type,
                    'scope_id': str(scope.id),
                }

                result.append(record)

        return result

    def _aggregate_permissions_grouped(self, permissions_list: list) -> dict:
        """
        将权限列表按 app_label.model 和 target 分组

        返回格式：
        {
            "cmdb.model_instance": {
                "obj_id_1": [
                    {"owner_type": "user", "owner_id": "111", ...},
                    {"owner_type": "role", "owner_id": "222", ...}
                ]
            }
        }
        """
        grouped = defaultdict(lambda: defaultdict(list))

        for perm in permissions_list:
            key = f"{perm['app_label']}.{perm['model']}"
            target = perm['target']

            grouped[key][target].append({
                'owner_type': perm['owner_type'],
                'owner_id': perm['owner_id'],
                'owner_name': perm['owner_name'],
                'scope_type': perm['scope_type'],
                'scope_id': perm['scope_id'],
                'via': perm['via']
            })

        # 转换为普通字典
        return {k: dict(v) for k, v in grouped.items()}

    def _filter_permissions(self, permissions_list: list, app_label: str = None, model: str = None) -> list:
        """
        根据条件过滤权限列表

        Args:
            permissions_list: 原始权限列表
            app_label: 应用标签过滤
            model: 模型名称过滤

        Returns:
            过滤后的权限列表
        """
        if not any([app_label, model]):
            return permissions_list

        filtered = permissions_list

        if app_label:
            filtered = [p for p in filtered if p['app_label'] == app_label]

        if model:
            filtered = [p for p in filtered if p['model'] == model]

        return filtered

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            targets_map = self._get_targets_detail_map(page)
            formatted_data = self._format_response_data(serializer.data, targets_map)
            return self.get_paginated_response(formatted_data)

        serializer = self.get_serializer(queryset, many=True)
        targets_map = self._get_targets_detail_map(queryset)
        formatted_data = self._format_response_data(serializer.data, targets_map)
        return Response(formatted_data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        formatted_data = self._build_response_with_targets(instance)
        return Response(formatted_data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        formatted_data = self._build_response_with_targets(serializer.instance)
        headers = self.get_success_headers(formatted_data)
        clear_data_scope_cache(self.request.user.username)
        return Response(formatted_data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        clear_data_scope_cache(self.request.user.username)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        formatted_data = self._build_response_with_targets(instance)
        return Response(formatted_data)

    @action(detail=False, methods=['get'])
    def aggregated_permissions(self, request):
        """
        获取用户/用户组/角色的聚合权限列表

        Query Parameters:
            - user: 用户ID
            - user_group: 用户组ID  
            - role: 角色ID
            - app_label: 应用标签（可选）
            - model: 模型名称（可选）

        返回格式:
        {
            "results": [
                {
                    "app_label": "cmdb",
                    "model": "model_instance",
                    "target": "obj_id",
                    "owner_type": "user",
                    "owner_id": "111",
                    "owner_name": "test",
                    "scope_type": "read",
                    "scope_id": "xxx"
                },
                ...
            ]
        }
        """
        user_id = request.query_params.get('user')
        user_group_id = request.query_params.get('user_group')
        role_id = request.query_params.get('role')
        app_label = request.query_params.get('app_label')
        model = request.query_params.get('model')

        # 验证参数：只能指定一个
        params_count = sum(1 for p in [user_id, user_group_id, role_id] if p)
        if params_count == 0:
            return Response(
                {'error': 'Please provide one of user, user_group, or role parameters'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if params_count > 1:
            return Response(
                {'error': 'Only one of user, user_group, or role can be specified'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            if user_id:
                user = UserInfo.objects.prefetch_related(
                    'groups', 'groups__roles', 'roles'
                ).get(id=user_id)
                scopes_with_sources = self._collect_scopes_for_user(user)
            elif user_group_id:
                user_group = UserGroup.objects.prefetch_related('roles').get(id=user_group_id)
                scopes_with_sources = self._collect_scopes_for_user_group(user_group)
            else:  # role_id
                role = Role.objects.get(id=role_id)
                scopes_with_sources = self._collect_scopes_for_role(role)

            # 聚合为列表格式
            permissions_list = self._aggregate_permissions_to_list(scopes_with_sources)

            permissions = self._filter_permissions(
                permissions_list,
                app_label=app_label,
                model=model,
            )

            return Response({
                'results': permissions
            })

        except UserInfo.DoesNotExist:
            return Response(
                {'error': f'User {user_id} does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )
        except UserGroup.DoesNotExist:
            return Response(
                {'error': f'UserGroup {user_group_id} does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Role.DoesNotExist:
            return Response(
                {'error': f'Role {role_id} does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.exception(f'Error in aggregated_permissions: {e}')
            return Response(
                {'error': f'Error occurred in aggregated_permissions: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], url_path='check-permission')
    def check_permission(self, request):
        """
        检查用户对特定对象是否有权限，并返回权限来源列表

        Query Parameters:
            - user_id: 用户ID（必填）
            - app_label: 应用标签（必填）
            - model: 模型名称（必填）
            - object_id: 对象ID（必填）
            - scope_type: 权限类型（可选，如指定则检查是否有该类型权限）

        返回格式:
        {
            "has_permission": true,
            "results": [
                {
                    "owner_type": "user",
                    "owner_id": "111",
                    "owner_name": "test",
                    "scope_id": "xxx"
                },
                ...
            ]
        }
        """
        user_id = request.query_params.get('user_id')
        app_label = request.query_params.get('app_label')
        model = request.query_params.get('model')
        object_id = request.query_params.get('object_id')

        if not all([user_id, app_label, model, object_id]):
            return Response(
                {'error': 'Please provide user_id, app_label, model, and object_id parameters'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = UserInfo.objects.prefetch_related(
                'groups', 'groups__roles', 'roles'
            ).get(id=user_id)

            scopes_with_sources = self._collect_scopes_for_user(user)
            permissions_list = self._aggregate_permissions_to_list(scopes_with_sources)

            # 筛选匹配的权限
            matched_permissions = [
                p for p in permissions_list
                if p['app_label'] == app_label
                and p['model'] == model
                and p['target'] == object_id
            ]

            if not matched_permissions:
                return Response({
                    'has_permission': False,
                    'message': 'User does not have permission for the object'
                })

            # 提取权限来源和类型
            results = [
                {
                    'owner_type': p['owner_type'],
                    'owner_id': p['owner_id'],
                    'owner_name': p['owner_name'],
                    'scope_id': p['scope_id'],
                }
                for p in matched_permissions
            ]

            return Response({
                'has_permission': True,
                'results': results
            })

        except UserInfo.DoesNotExist:
            return Response(
                {'error': f'User {user_id} does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.exception(f'Error in check_permission: {e}')
            return Response(
                {'error': f'Error in check_permission: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
