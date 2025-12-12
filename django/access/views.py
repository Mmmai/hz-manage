import json
import logging

from collections import defaultdict
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from django.db.models import Q
from .public_services import PublicPermissionService
from mapi.models import UserInfo, UserGroup, Role
from .tools import clear_data_scope_cache
from .models import *
from .serializers import *
from .filters import ButtonFilter
from .services import *

logger = logging.getLogger(__name__)


class getMenu(APIView):
    """动态路由"""

    def __init__(self):
        self.get_menu_tree = self.get_menu_tree

    def post(self, request, *args, **kwargs):
        # 获取当前用户
        user_obj = request.user

        # 根据当前用户获取其所有权限
        user_permissions = PermissionService.get_user_permissions(user_obj)

        # 获取用户有权访问的菜单IDs
        accessible_menu_ids = set(user_permissions.values_list('menu', flat=True).distinct())

        # 获取所有菜单
        all_menus = Menu.objects.all().order_by('sort')

        menuList = self.get_menu_tree(all_menus, accessible_menu_ids, parent=None)
        return Response({'code': 200, "results": menuList})

    def get_menu_tree(self, all_menus, accessible_menu_ids, parent=None):
        tree = []
        # 筛选出当前层级的所有菜单项
        for menu in all_menus.filter(parentid=parent):
            # 构造基本菜单信息
            info = menu.__dict__.copy()
            info.pop('_state')
            parentid = info.pop('parentid_id')
            info["parentid"] = parentid

            # 获取具有此菜单权限的角色列表
            roleList = list(set([
                str(permission.role.id)
                for permission in Permission.objects.filter(menu=menu, role__isnull=False)
            ]))

            # 序列化按钮数据
            button_queryset = menu.buttons.all().order_by("action")
            button_serializer = ButtonModelSerializer(button_queryset, many=True)
            serialized_data = JSONRenderer().render(button_serializer.data)

            info["meta"] = {
                "role": roleList,
                "icon": menu.icon,
                "title": menu.label,
                "isKeepAlive": menu.keepalive,
                "hasInfo": menu.has_info
            }
            info["buttons"] = json.loads(serialized_data.decode('utf8'))

            if info["is_iframe"]:
                info["meta"]["iframePath"] = info["iframe_url"]
                info["meta"]["is_iframe"] = info["is_iframe"]

            # 构建菜单全路径
            path_labels = []
            current = menu
            while current:
                path_labels.insert(0, {'name': current.label, 'icon': current.icon})
                current = current.parentid

            # 添加meta信息，包含菜单全路径
            info["meta"].update({"menuPath": path_labels})

            # 递归处理子菜单
            children = self.get_menu_tree(all_menus, accessible_menu_ids, menu)
            info['children'] = children

            # 判断当前菜单是否应该显示给用户：
            # 1. 如果是叶子菜单（菜单项），必须有权限才能显示
            # 2. 如果是目录，只要包含有权限的子菜单就可以显示
            # 3. 如果是叶子菜单但没有子菜单且用户无权限，则不显示
            if menu.is_menu:  # 是菜单项
                if menu.id in accessible_menu_ids:
                    tree.append(info)
            else:  # 是目录
                # 目录只要有子项就显示，不管是否有直接权限
                if children or menu.id in accessible_menu_ids:
                    tree.append(info)

        return tree


class getPermissionToRole(APIView):
    def __init__(self):
        self.get_menu_tree = self.get_menu_tree

    def post(self, request, *args, **kwargs):
        menuobj = Menu.objects.all().order_by('sort')
        menuList = self.get_menu_tree(menuobj)
        return Response({'code': 200, "results": menuList})

    def get_menu_tree(self, menu_list, parent=None):
        tree = []
        for menu in menu_list.filter(parentid=parent):
            if menu.is_menu:
                # 添加按钮到对应菜单下
                info = {"id": menu.id, "label": menu.label, "tree_type": "menu"}
            else:
                info = {"id": menu.id, "label": menu.label, "tree_type": "directory"}
            info['children'] = self.get_menu_tree(menu_list, menu)

            if menu.is_menu:
                # 添加按钮到对应菜单下
                info["children"] = [{"id": str(i.id), "label": i.name, "button": i.action, "tree_type": "button"}
                                    for i in Button.objects.filter(menu=menu).all().order_by('action')]
            tree.append(info)
        return tree


class getUserButton(APIView):

    def post(self, request, *args, **kwargs):

        role_ids = request.data.get('role')
        # 拿permission表中所有权限,菜单name:按钮action,例如：home:edit
        allPermissionList = []
        for role_id in role_ids:
            for p_obj in Permission.objects.filter(role=role_id).all():
                menu_name = p_obj.menu.name
                button_name = p_obj.button.action
                allPermissionList.append(f"{menu_name}:{button_name}")
        return Response({'code': 200, "results": allPermissionList})


class MenuViewSet(ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuModelSerializer

    @action(detail=False, methods=['get'], url_path='get_menu_tree')
    def get_menu_tree(self, request):
        menuobj = Menu.objects.all().order_by('sort')
        menuList = self._get_menu_tree(menuobj)
        return Response({'code': 200, "results": menuList})

    def _get_menu_tree(self, menu_list, parent=None):
        tree = []
        for menu in menu_list.filter(parentid=parent):
            if menu.is_menu:
                # 添加按钮到对应菜单下
                info = {"id": menu.id, "label": menu.label, "tree_type": "menu"}
            else:
                info = {"id": menu.id, "label": menu.label, "tree_type": "directory"}
            info['children'] = self._get_menu_tree(menu_list, menu)
            if menu.is_menu:
                # 添加按钮到对应菜单下
                info["children"] = [{"id": str(i.id), "label": i.name, "button": i.action, "tree_type": "button"}
                                    for i in Button.objects.filter(menu=menu).all().order_by('action')]
            tree.append(info)
        return tree


class ButtonViewSet(ModelViewSet):
    queryset = Button.objects.all()
    serializer_class = ButtonModelSerializer
    filterset_class = ButtonFilter


class PermissionViewSet(ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionModelSerializer
    # 根据用户、用户组、角色获取权限列表

    @action(detail=False, methods=['get'], url_path='get_permission')
    def get_permission(self, request):
        # 获取查询参数
        user_id = request.query_params.get('user', None)
        user_group_id = request.query_params.get('user_group', None)
        role_id = request.query_params.get('role', None)

        # 根据传入的参数过滤权限
        if user_id:
            # 获取指定用户的所有权限（包括通过角色和用户组继承的权限）
            try:
                user = UserInfo.objects.get(id=user_id)
                permissions = PermissionService.get_user_permissions(user)
                # 为每个权限添加来源信息
                permission_details = []
                for perm in permissions:
                    source_type = "unknown"
                    source_name = "未知"
                    if perm.user == user:
                        source_type = "user"
                        source_name = user.username
                    elif perm.role_id:
                        source_type = "role"
                        source_name = perm.role.role
                    elif perm.user_group_id:
                        source_type = "user_group"
                        source_name = perm.user_group.group_name

                    permission_details.append({
                        'button_id': str(perm.button_id),
                        'source_type': source_type,
                        'source_name': source_name,
                        'permission_id': str(perm.id)
                    })

            except UserInfo.DoesNotExist:
                return Response({'error': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                logger.error(f"Error retrieving permissions for user {user_id}: {str(e)}")
                return Response({'error': '获取用户权限时发生错误'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        elif user_group_id:
            # 获取指定用户组的权限
            try:
                user_group = UserGroup.objects.get(id=user_group_id)
                # 获取直接分配给用户组的权限
                direct_permissions = Permission.objects.filter(user_group=user_group)

                # 获取通过用户组角色分配的权限
                group_roles = user_group.roles.all()
                role_permissions = Permission.objects.filter(role__in=group_roles)
                # 合并权限并去重
                permissions = (direct_permissions | role_permissions).distinct()
                # 为每个权限添加来源信息
                permission_details = []
                for perm in permissions:
                    source_type = "unknown"
                    source_name = "未知"
                    if perm.user_group == user_group:
                        source_type = "user_group"
                        source_name = user_group.group_name
                    elif perm.role_id and perm.role_id in [role.id for role in group_roles]:
                        source_type = "role"
                        source_name = perm.role.role

                    permission_details.append({
                        'button_id': str(perm.button_id),
                        'source_type': source_type,
                        'source_name': source_name,
                        'permission_id': str(perm.id)
                    })

            except UserGroup.DoesNotExist:
                return Response({'error': '用户组不存在'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'error': '获取用户组权限时发生错误'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        elif role_id:
            # 获取指定角色的权限
            try:
                permissions = Permission.objects.filter(role_id=role_id)

                # 为每个权限添加来源信息
                permission_details = []
                role = Role.objects.get(id=role_id)
                for perm in permissions:
                    permission_details.append({
                        'button_id': str(perm.button_id),
                        'source_type': 'role',
                        'source_name': role.role,
                        'permission_id': str(perm.id)
                    })

            except Role.DoesNotExist:
                return Response({'error': '角色不存在'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'error': '获取角色权限时发生错误'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            # 如果没有指定任何参数，返回错误
            return Response({'error': '请提供user、user_group或role中的一个参数'},
                            status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'code': 200,
            'results': permission_details
        })
    # 根据传入的对象，添加权限

    @action(detail=False, methods=['post'], url_path='add_permissions')
    def add_permissions(self, request):
        """
        为用户、用户组或角色添加权限

        参数:
            request: HTTP请求对象，应包含以下参数中的至少一个:
                - user: 用户ID
                - user_group: 用户组ID
                - role: 角色ID
                - button_ids: 按钮ID列表

        返回:
            Response: 包含操作结果的响应
        """
        user_id = request.data.get('user', None)
        user_group_id = request.data.get('user_group', None)
        role_id = request.data.get('role', None)
        button_ids = request.data.get('button_ids', [])

        # 参数有效性检查
        target_count = sum(x is not None for x in [user_id, user_group_id, role_id])
        if target_count != 1:
            return Response({
                'error': '必须且只能提供user、user_group或role中的一个参数'
            }, status=status.HTTP_400_BAD_REQUEST)
        if not button_ids:
            return Response({
                'error': 'button_ids参数不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 验证关联对象是否存在
        try:
            buttons = Button.objects.filter(id__in=button_ids)
            if buttons.count() != len(button_ids):
                return Response({
                    'error': '某些按钮ID不存在'
                }, status=status.HTTP_400_BAD_REQUEST)

            # 确定权限主体
            user = UserInfo.objects.get(id=user_id) if user_id else None
            user_group = UserGroup.objects.get(id=user_group_id) if user_group_id else None
            role = Role.objects.get(id=role_id) if role_id else None
        except UserInfo.DoesNotExist:
            return Response({
                'error': '指定的用户不存在'
            }, status=status.HTTP_400_BAD_REQUEST)
        except UserGroup.DoesNotExist:
            return Response({
                'error': '指定的用户组不存在'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Role.DoesNotExist:
            return Response({
                'error': '指定的角色不存在'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': f'验证参数时发生错误: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 添加权限
        try:
            added_permissions = []
            existing_permissions = []

            for button in buttons:
                # 创建或获取权限记录
                permission, created = Permission.objects.get_or_create(
                    user=user,
                    user_group=user_group,
                    role=role,
                    button=button,
                    menu=button.menu
                )

                if created:
                    added_permissions.append(str(button.id))
                    # 记录日志
                    if user:
                        logger.info(f"为用户<{user.username}>添加<{button.menu.name}-{button.name}>权限")
                    elif user_group:
                        logger.info(f"为用户组<{user_group.group_name}>添加<{button.menu.name}-{button.name}>权限")
                    elif role:
                        logger.info(f"为角色<{role.role}>添加<{button.menu.name}-{button.name}>权限")
                    # 如果不是查看权限，确保查看权限也存在
                    if button.action != "view":
                        view_button_obj = Button.objects.get(action="view", menu=button.menu)
                        view_per_obj, view_created = Permission.objects.get_or_create(
                            user=user,
                            user_group=user_group,
                            role=role,
                            menu=button.menu,
                            button=view_button_obj
                        )
                        if view_created:
                            logger.info(f"同时添加<{view_button_obj.action}>权限!")
                else:
                    existing_permissions.append(str(button.id))

            return Response({
                'detail': '权限添加成功',
                'added_permissions': added_permissions,
                'existing_permissions': existing_permissions
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'error': f'添加权限时发生错误: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=['post'], detail=False)
    def remove_permissions(self, request):
        """
        从用户、用户组或角色中删除权限

        参数:
            request: HTTP请求对象，应包含以下参数中的至少一个:
                - user: 用户ID
                - user_group: 用户组ID
                - role: 角色ID
                - button_ids: 按钮ID列表

        返回:
            Response: 包含操作结果的响应
        """
        user_id = request.data.get('user', None)
        user_group_id = request.data.get('user_group', None)
        role_id = request.data.get('role', None)
        button_ids = request.data.get('button_ids', [])

        # 参数有效性检查
        target_count = sum(x is not None for x in [user_id, user_group_id, role_id])
        if target_count != 1:
            return Response({
                'error': '必须且只能提供user、user_group或role中的一个参数'
            }, status=status.HTTP_400_BAD_REQUEST)

        if not button_ids:
            return Response({
                'error': 'button_ids参数不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 验证关联对象是否存在
        try:
            buttons = Button.objects.filter(id__in=button_ids)
            if buttons.count() != len(button_ids):
                return Response({
                    'error': '某些按钮ID不存在'
                }, status=status.HTTP_400_BAD_REQUEST)

            # 确定权限主体
            user = UserInfo.objects.get(id=user_id) if user_id else None
            user_group = UserGroup.objects.get(id=user_group_id) if user_group_id else None
            role = Role.objects.get(id=role_id) if role_id else None
        except UserInfo.DoesNotExist:
            return Response({
                'error': '指定的用户不存在'
            }, status=status.HTTP_400_BAD_REQUEST)
        except UserGroup.DoesNotExist:
            return Response({
                'error': '指定的用户组不存在'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Role.DoesNotExist:
            return Response({
                'error': '指定的角色不存在'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': f'验证参数时发生错误: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 删除权限
        try:
            removed_permissions = []

            # 构建查询条件
            filter_kwargs = {
                'button__in': buttons
            }
            if user:
                filter_kwargs['user'] = user
            elif user_group:
                filter_kwargs['user_group'] = user_group
            elif role:
                filter_kwargs['role'] = role

            # 查找并删除权限
            permissions_to_remove = Permission.objects.filter(**filter_kwargs)

            for perm in permissions_to_remove:
                button_id = str(perm.button.id)
                removed_permissions.append(button_id)
                # 记录日志
                if user:
                    logger.info(f"从用户<{user.username}>移除<{perm.menu.name}-{perm.button.name}>权限")
                elif user_group:
                    logger.info(f"从用户组<{user_group.group_name}>移除<{perm.menu.name}-{perm.button.name}>权限")
                elif role:
                    logger.info(f"从角色<{role.role}>移除<{perm.menu.name}-{perm.button.name}>权限")
                # 当移除查看权限时，应该移除其他权限
                if perm.button.action == 'view':
                    # 根据menu删除
                    permissions_to_remove.filter(button__menu=perm.button.menu).delete()
                    logger.info(f"移除菜单<{perm.button.menu.name}>所有权限")
            permissions_to_remove.delete()

            return Response({
                'detail': '权限删除成功',
                'removed_permissions': removed_permissions
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'error': f'删除权限时发生错误: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
