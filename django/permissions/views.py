import logging

from collections import defaultdict
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.db.models import Q

from mapi.models import UserInfo, UserGroup, Role
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

    # ============ 权限聚合相关方法 ============

    def _get_permission_source_label(self, scope) -> dict:
        """获取权限来源的标签信息"""
        if scope.user_id:
            return {
                'type': 'user',
                'id': str(scope.user_id),
                'name': getattr(scope.user, 'username', str(scope.user_id)) if scope.user else str(scope.user_id)
            }
        elif scope.user_group_id:
            return {
                'type': 'user_group',
                'id': str(scope.user_group_id),
                'name': getattr(scope.user_group, 'group_name', str(scope.user_group_id)) if scope.user_group else str(scope.user_group_id)
            }
        elif scope.role_id:
            return {
                'type': 'role',
                'id': str(scope.role_id),
                'name': getattr(scope.role, 'role_name', str(scope.role_id)) if scope.role else str(scope.role_id)
            }
        return {'type': 'unknown', 'id': None, 'name': 'Unknown'}

    def _collect_scopes_for_user(self, user):
        """收集用户相关的所有 DataScope（直接权限 + 用户组权限 + 角色权限）"""

        scopes_with_sources = []

        user_scopes = DataScope.objects.filter(user=user).prefetch_related(
            'targets', 'targets__content_type', 'user'
        )
        for scope in user_scopes:
            scopes_with_sources.append({
                'scope': scope,
                'source': {
                    'type': 'user',
                    'id': str(user.id),
                    'name': user.username
                }
            })

        user_groups = user.groups.all()
        for group in user_groups:
            group_scopes = DataScope.objects.filter(user_group=group).prefetch_related(
                'targets', 'targets__content_type', 'user_group'
            )
            for scope in group_scopes:
                scopes_with_sources.append({
                    'scope': scope,
                    'source': {
                        'type': 'user_group',
                        'id': str(group.id),
                        'name': group.group_name
                    }
                })

            group_roles = group.roles.all()
            for role in group_roles:
                role_scopes = DataScope.objects.filter(role=role).prefetch_related(
                    'targets', 'targets__content_type', 'role'
                )
                for scope in role_scopes:
                    scopes_with_sources.append({
                        'scope': scope,
                        'source': {
                            'type': 'role',
                            'id': str(role.id),
                            'name': role.role_name,
                            'via': {
                                'type': 'user_group',
                                'id': str(group.id),
                                'name': group.group_name
                            }
                        }
                    })

        user_roles = user.roles.all()
        for role in user_roles:
            role_scopes = DataScope.objects.filter(role=role).prefetch_related(
                'targets', 'targets__content_type', 'role'
            )
            for scope in role_scopes:
                scopes_with_sources.append({
                    'scope': scope,
                    'source': {
                        'type': 'role',
                        'id': str(role.id),
                        'name': role.role_name,
                        'via': {
                            'type': 'user',
                            'id': str(user.id),
                            'name': user.username
                        }
                    }
                })

        return scopes_with_sources

    def _collect_scopes_for_user_group(self, user_group):
        """收集用户组相关的所有 DataScope（直接权限 + 角色权限）"""
        scopes_with_sources = []

        group_scopes = DataScope.objects.filter(user_group=user_group).prefetch_related(
            'targets', 'targets__content_type', 'user_group'
        )
        for scope in group_scopes:
            scopes_with_sources.append({
                'scope': scope,
                'source': {
                    'type': 'user_group',
                    'id': str(user_group.id),
                    'name': user_group.group_name
                }
            })

        group_roles = user_group.roles.all()
        for role in group_roles:
            role_scopes = DataScope.objects.filter(role=role).prefetch_related(
                'targets', 'targets__content_type', 'role'
            )
            for scope in role_scopes:
                scopes_with_sources.append({
                    'scope': scope,
                    'source': {
                        'type': 'role',
                        'id': str(role.id),
                        'name': role.role_name,
                        'via': {
                            'type': 'user_group',
                            'id': str(user_group.id),
                            'name': user_group.group_name
                        }
                    }
                })

        return scopes_with_sources

    def _collect_scopes_for_role(self, role):
        """收集角色相关的所有 DataScope"""
        scopes_with_sources = []

        role_scopes = DataScope.objects.filter(role=role).prefetch_related(
            'targets', 'targets__content_type', 'role'
        )
        for scope in role_scopes:
            scopes_with_sources.append({
                'scope': scope,
                'source': {
                    'type': 'role',
                    'id': str(role.id),
                    'name': role.role_name
                }
            })

        return scopes_with_sources

    def _aggregate_permissions_with_sources(self, scopes_with_sources: list) -> dict:
        """
        聚合权限并标注来源
        返回格式：
        {
            "app_label.model": {
                "object_id_1": {
                    "sources": [
                        {"type": "user", "id": "xxx", "name": "用户A"},
                        {"type": "role", "id": "xxx", "name": "角色A", "via": {...}}
                    ],
                    "scope_types": ["read", "write"]
                }
            }
        }
        """
        aggregated = defaultdict(lambda: defaultdict(lambda: {
            'sources': [],
            'scope_types': set()
        }))

        # 用于去重来源
        seen_sources = defaultdict(lambda: defaultdict(set))

        for item in scopes_with_sources:
            scope = item['scope']
            source = item['source']

            # 创建来源的唯一标识用于去重
            source_key = f"{source['type']}:{source['id']}"
            if 'via' in source:
                source_key += f":via:{source['via']['type']}:{source['via']['id']}"

            for target in scope.targets.all():
                target_key = self._build_target_key(target)
                object_id = str(target.object_id)

                # 检查是否已添加该来源
                if source_key not in seen_sources[target_key][object_id]:
                    seen_sources[target_key][object_id].add(source_key)
                    aggregated[target_key][object_id]['sources'].append(source)

                # 添加权限类型
                if scope.scope_type:
                    aggregated[target_key][object_id]['scope_types'].add(scope.scope_type)

        # 将 set 转换为 list 以便 JSON 序列化
        result = {}
        for target_key, objects in aggregated.items():
            result[target_key] = {}
            for object_id, data in objects.items():
                result[target_key][object_id] = {
                    'sources': data['sources'],
                    'scope_types': list(data['scope_types'])
                }

        return result

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
        return Response(formatted_data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # 清除预取缓存以获取最新数据
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        formatted_data = self._build_response_with_targets(instance)
        return Response(formatted_data)

    @action(detail=False, methods=['get'])
    def aggregated_permissions(self, request):
        """
        获取用户/用户组/角色的聚合权限，包含权限来源信息

        Query Parameters:
            - user_id: 用户ID
            - user_group_id: 用户组ID  
            - role_id: 角色ID

        返回格式:
        {
            "subject": {
                "type": "user",
                "id": "xxx",
                "name": "用户A"
            },
            "permissions": {
                "app_label.model": {
                    "object_id_1": {
                        "sources": [
                            {"type": "user", "id": "xxx", "name": "用户A"},
                            {"type": "user_group", "id": "xxx", "name": "用户组A"},
                            {"type": "role", "id": "xxx", "name": "角色A", "via": {"type": "user", ...}}
                        ],
                        "scope_types": ["read", "write"]
                    }
                }
            }
        }
        """
        user_id = request.query_params.get('user_id')
        user_group_id = request.query_params.get('user_group_id')
        role_id = request.query_params.get('role_id')

        # 验证参数：只能指定一个
        params_count = sum(1 for p in [user_id, user_group_id, role_id] if p)
        if params_count == 0:
            return Response(
                {'error': '请提供 user_id、user_group_id 或 role_id 参数'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if params_count > 1:
            return Response(
                {'error': '只能指定 user_id、user_group_id 或 role_id 中的一个'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            if user_id:
                user = UserInfo.objects.prefetch_related('groups', 'groups__roles', 'roles').get(id=user_id)
                scopes_with_sources = self._collect_scopes_for_user(user)
                subject = {
                    'type': 'user',
                    'id': str(user.id),
                    'name': user.username
                }
            elif user_group_id:
                user_group = UserGroup.objects.prefetch_related('roles').get(id=user_group_id)
                scopes_with_sources = self._collect_scopes_for_user_group(user_group)
                subject = {
                    'type': 'user_group',
                    'id': str(user_group.id),
                    'name': user_group.group_name
                }
            else:  # role_id
                role = Role.objects.get(id=role_id)
                scopes_with_sources = self._collect_scopes_for_role(role)
                subject = {
                    'type': 'role',
                    'id': str(role.id),
                    'name': role.role_name
                }

            permissions = self._aggregate_permissions_with_sources(scopes_with_sources)

            return Response({
                'subject': subject,
                'permissions': permissions
            })

        except (UserInfo.DoesNotExist if user_id else
                UserGroup.DoesNotExist if user_group_id else
                Role.DoesNotExist) as e:
            return Response(
                {'error': f'Cannot find specified subject: {str(e)}'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.exception(f'Error in aggregated_permissions: {e}')
            return Response(
                {'error': f'Error occurred while querying permissions: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], url_path='check-permission')
    def check_permission(self, request):
        """
        检查用户对特定对象是否有权限，并返回权限来源

        Query Parameters:
            - user_id: 用户ID（必填）
            - app_label: 应用标签（必填）
            - model: 模型名称（必填）
            - object_id: 对象ID（必填）
            - scope_type: 权限类型（可选）
        """
        user_id = request.query_params.get('user_id')
        app_label = request.query_params.get('app_label')
        model = request.query_params.get('model')
        object_id = request.query_params.get('object_id')
        scope_type = request.query_params.get('scope_type')

        if not all([user_id, app_label, model, object_id]):
            return Response(
                {'error': 'Please provide user_id, app_label, model, and object_id parameters'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = UserInfo.objects.prefetch_related('groups', 'groups__roles', 'roles').get(id=user_id)

            scopes_with_sources = self._collect_scopes_for_user(user)
            permissions = self._aggregate_permissions_with_sources(scopes_with_sources)

            target_key = f"{app_label}.{model}"

            if target_key in permissions and object_id in permissions[target_key]:
                permission_data = permissions[target_key][object_id]

                # 如果指定了 scope_type，检查是否包含
                if scope_type and scope_type not in permission_data['scope_types']:
                    return Response({
                        'has_permission': False,
                        'message': f'User does not have {scope_type} permission on the object'
                    })

                return Response({
                    'has_permission': True,
                    'sources': permission_data['sources'],
                    'scope_types': permission_data['scope_types']
                })
            else:
                return Response({
                    'has_permission': False,
                    'message': 'User does not have permission on the object'
                })

        except UserInfo.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.exception(f'Error in check_permission: {e}')
            return Response(
                {'error': f'Error occurred while checking permission: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
