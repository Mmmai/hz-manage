import tempfile
import json

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework import filters, status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend

from node_mg.utils.config_manager import ConfigManager
from cmdb.utils import password_handler
from access.public_services import PublicPermissionService

from .utils.jwt_create_token import create_token
from .extensions.jwt_authenticate import JWTQueryParamsAuthentication
from .sers import *
from .models import *
from .filters import *
from .export import exportHandler

import logging
logger = logging.getLogger(__name__)


class LoginView(APIView):
    """用户登录"""
    authentication_classes = []  # 取消全局认证

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        # 查找用户
        user_obj = UserInfo.objects.filter(username=username).first()
        if not user_obj:
            return Response({'code': 401, 'error': '用户名不存在!'})
        # 检查用户是否已过期（admin等内置用户除外）
        if user_obj.is_expired():
            return Response({'code': 401, 'error': '用户账户已过期!'})

        # 检查用户状态
        if not user_obj.status:
            return Response({'code': 401, 'error': '用户已被禁用!'})
        try:
            # 使用用户存储的盐值处理输入的密码
            salted_password = f'{user_obj.password_salt}:{password}'
            # 使用SM4加密加盐后的密码
            encrypted_password = password_handler.encrypt_to_sm4(salted_password)
            # 比较加密后的密码
            if user_obj.password != encrypted_password:
                return Response({'code': 401, 'error': '用户密码错误!'})
        except Exception as e:
            logger.error(f"Password verification failed: {str(e)}")
            return Response({'code': 401, 'error': '密码认证失败!'})
        # 获取用户组id
        userGroupList = [i['id'] for i in user_obj.groups.all().values('id')]
        #
        userGroupRoleList = []
        for group in userGroupList:
            group_obj = UserGroup.objects.get(id=group)
            for group_role in group_obj.roles.all():
                userGroupRoleList.append(group_role.id)
        # 获取用户权限
        permissionObjects = PublicPermissionService.get_user_permissions(user_obj)
        allPermissionList = [
            f"{permissionObj.menu.name}:{permissionObj.button.action}" for permissionObj in permissionObjects]
        # print(roleList)
        payload = {
            'user_id': str(user_obj.pk),  # 自定义用户ID
            'username': user_obj.username,  # 自定义用户名
            'password': user_obj.password,  # 添加密码字段用于验证token有效性
            # 'exp':datetime.datetime.utcnow()+datetime.timedelta(minutes=1),# 设置超时时间，1min
        }
        # 超时时间，默认3days
        timeout = request.data.get('timeout', 3)
        jwt_token = create_token(payload=payload, timeout=timeout)
        return Response({
            'code': 200,
            'token': jwt_token,
            "userinfo": {
                'user_id': str(user_obj.pk),
                'username': user_obj.username
            },
            "permission": allPermissionList
        })


class getSecret(APIView):
    def get(self, request, *args, **kwargs):
        # 获取头部token

        return Response({"secret": settings.SECRET_KEY})

    def post(self, request, *args, **kwargs):
        # 获取头部token
        token = request.META.get('HTTP_TOKEN')
        return Response({"secret": settings.SECRET_KEY})


class UserInfoViewSet(ModelViewSet):
    queryset = UserInfo.objects.all()
    # 认证
    authentication_classes = [JWTQueryParamsAuthentication, ]
    serializer_class = UserInfoModelSerializer
    # pagination_class = defaultPageNumberPagination
    # filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)  # 指定后端
    # 视图中设置了 search_fields 属性时，才会应用 SearchFilter 类
    # search_fields只支持文本类型字段，例如 CharField 或 TextField
    search_fields = ('$username',)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # 执行删除前验证
        serializer = self.get_serializer()
        try:
            serializer.validate_for_delete(instance)
        except serializers.ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # 批量删除
    @action(methods=['delete'], detail=False)
    def multiple_delete(self, request, *args, **kwargs):
        # pks = request.query_params.get('pks', None)
        pks = request.data.get('pks', None)
        if not pks:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # 对每个要删除的对象执行验证
        serializer = self.get_serializer()
        for pk in pks:
            try:
                instance = UserInfo.objects.get(id=pk)
                serializer.validate_for_delete(instance)
            except UserInfo.DoesNotExist:
                return Response({'error': f'用户不存在: {pk}'}, status=status.HTTP_400_BAD_REQUEST)
            except serializers.ValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

       # for pk in pks:
            # get_object_or_404(UserInfo, id=pk).delete()

        if 'admin' in UserInfo.objects.filter(id__in=pks).values_list('username', flat=True):
            raise PermissionDenied('admin 用户为系统管理员，不允许删除')

        UserInfo.objects.filter(id__in=pks).delete()
        return Response(data='delete success', status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        if instance.username == 'admin':
            raise PermissionDenied('admin 用户为系统管理员，不允许删除')
        super().perform_destroy(instance)

    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.username == 'admin':
            # 禁止修改 username、is_active
            forbidden_fields = {'username', 'is_active'}
            if any(f in self.request.data for f in forbidden_fields):
                raise PermissionDenied('admin 用户的核心属性不可更改')
            # 防止移除 sysadmin 角色
            if 'roles' in self.request.data:
                new_role_ids = set(self.request.data['roles'])
                sysadmin_role = Role.objects.filter(role='sysadmin').first()
                if sysadmin_role and str(sysadmin_role.id) not in new_role_ids:
                    raise PermissionDenied('不允许移除 admin 用户的 sysadmin 角色')
        super().perform_update(serializer)


class UserGroupViewSet(ModelViewSet):
    queryset = UserGroup.objects.all()
    serializer_class = UserGroupModelSerializer
    # pagination_class = StandardResultsSetPagination
    # filterset_class = roleFilter
    order_fields = ["id"]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # 执行删除前验证
        serializer = self.get_serializer()
        try:
            serializer.validate_for_delete(instance)
        except serializers.ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RoleViewSet(ModelViewSet):

    queryset = Role.objects.all()
    serializer_class = RoleModelSerializer
    # pagination_class = StandardResultsSetPagination
    filterset_class = roleFilter
    order_fields = ["id"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        # 处理角色权限
        instance = Role.objects.get(id=serializer.data['id'])
        rolePermission = request.data.get('rolePermission', None)
        if rolePermission:
            # 添加新的权限
            PublicPermissionService.update_role_permissions(instance, rolePermission)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # 执行删除前验证
        serializer = self.get_serializer()
        try:
            serializer.validate_for_delete(instance)
        except serializers.ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        # 更新perrmison字段内容
        rolePermission = request.data.get('rolePermission', None)
        if not rolePermission:
            pass
        else:
            PublicPermissionService.update_role_permissions(instance, rolePermission)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='add_permissions')
    def add_permissions(self, request, pk=None):
        """
        为角色添加权限
        """
        role = self.get_object()
        button_ids = request.data.get('button_ids', [])

        if not button_ids:
            return Response({'error': '权限ID列表不能为空'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            added_permissions, existing_permissions = \
                PublicPermissionService.add_permissions_to_role(request, role, button_ids)
        except Exception as e:
            return Response({'error': f'添加权限时发生错误: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            'detail': '权限添加成功',
            'added_permissions': added_permissions,
            'existing_permissions': existing_permissions
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='remove_permissions')
    def remove_permissions(self, request, pk=None):
        """
        从角色中删除权限
        """
        role = self.get_object()
        button_ids = request.data.get('button_ids', [])

        if not button_ids:
            return Response({'error': '权限ID列表不能为空'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            removed_permissions = PublicPermissionService.remove_permissions_from_role(request, role, button_ids)
        except Exception as e:
            return Response({'error': f'删除权限时发生错误: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            'detail': '权限删除成功',
            'removed_permissions': removed_permissions
        }, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        if instance.role == 'sysadmin':
            logger.warning(f'尝试删除系统内置角色 sysadmin, 操作被拒绝')
            raise PermissionDenied('sysadmin 角色为系统内置角色，不允许删除')
        super().perform_destroy(instance)

    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.role == 'sysadmin':
            # 允许修改 name/description，但禁止修改核心字段 role
            if 'role' in self.request.data or 'permissions' in self.request.data:
                raise PermissionDenied('sysadmin 角色的权限配置不可更改')
        super().perform_update(serializer)


class PortalViewSet(ModelViewSet):
    queryset = Portal.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'url', 'describe', 'groups__group']  # 更新搜索字段

    def get_serializer_class(self):
        if self.action == 'list':
            return getPortalModelSerializer
        else:
            return PortalModelSerializer

    def get_queryset(self):
        """
        默认查询所有公共门户和当前用户创建的私人门户，
        同时门户必须属于公共分组或用户自己的私人分组
        """
        user = self.request.user
        return Portal.objects.filter(
            models.Q(
                models.Q(sharing_type='public') |
                models.Q(sharing_type='private', owner=user)
            ) & (
                models.Q(groups__sharing_type='public') |
                models.Q(groups__sharing_type='private', groups__owner=user)
            )
        ).distinct()

    def list(self, request, *args, **kwargs):
        # 获取当前用户
        user = request.user

        # 获取查询参数
        sharing_type = request.query_params.get('sharing_type', None)
        owner = request.query_params.get('owner', None)
        group_id = request.query_params.get('group', None)  # 按分组过滤

        # 获取排序参数
        ordering = request.query_params.get('ordering', None)
        group_ordering = request.query_params.get('group_ordering', None)  # 分组内排序

        # 默认查询符合条件的门户
        queryset = self.get_queryset()
        # 应用过滤器
        queryset = self.filter_queryset(queryset)

        # 如果指定了共享类型，则按指定类型过滤
        if sharing_type:
            queryset = queryset.filter(sharing_type=sharing_type)

        # 如果指定了所有者，则按所有者过滤
        if owner:
            queryset = queryset.filter(owner=owner)

        # 如果指定了分组，则按分组过滤
        if group_id:
            # 确保用户有权访问该分组
            try:
                group = Pgroup.objects.get(id=group_id)
                if group.sharing_type == 'private' and group.owner != user:
                    # 用户试图访问他人私有分组
                    queryset = queryset.none()
                else:
                    queryset = queryset.filter(groups=group_id)
            except Pgroup.DoesNotExist:
                queryset = queryset.none()

        # 处理排序
        if group_ordering:
            # 分组内排序优先
            ordering_fields = group_ordering.split(',')
            allowed_fields = ['sort_order', 'name', 'create_time', 'update_time']
            validated_ordering = []
            for field in ordering_fields:
                field = field.strip()
                if field.startswith('-'):
                    field_name = field[1:]
                    prefix = '-'
                else:
                    field_name = field
                    prefix = ''

                if field_name in allowed_fields:
                    validated_ordering.append(prefix + field_name)

            if validated_ordering:
                queryset = queryset.order_by(*validated_ordering)
            else:
                # 应用用户自定义排序
                user_sort_prefs = UserPortalSortOrder.objects.filter(user=request.user)
                if user_sort_prefs.exists():
                    user_sort_dict = {str(pref.portal_id): pref.sort_order for pref in user_sort_prefs}

                    def sort_key(portal):
                        return user_sort_dict.get(str(portal.id), portal.sort_order)
                    queryset = sorted(queryset, key=sort_key)
                else:
                    queryset = queryset.order_by('sort_order')
        elif ordering:
            ordering_fields = ordering.split(',')
            allowed_fields = ['sort_order', 'name', 'create_time', 'update_time', 'groups']
            validated_ordering = []
            for field in ordering_fields:
                field = field.strip()
                if field.startswith('-'):
                    field_name = field[1:]
                    prefix = '-'
                else:
                    field_name = field
                    prefix = ''

                if field_name in allowed_fields:
                    validated_ordering.append(prefix + field_name)

            if validated_ordering:
                queryset = queryset.order_by(*validated_ordering)
            else:
                # 应用用户自定义排序
                user_sort_prefs = UserPortalSortOrder.objects.filter(user=request.user)
                if user_sort_prefs.exists():
                    user_sort_dict = {str(pref.portal_id): pref.sort_order for pref in user_sort_prefs}

                    def sort_key(portal):
                        return user_sort_dict.get(str(portal.id), portal.sort_order)
                    queryset = sorted(queryset, key=sort_key)
                else:
                    queryset = queryset.order_by('groups', 'sort_order')
        else:
            # 应用用户自定义排序
            user_sort_prefs = UserPortalSortOrder.objects.filter(user=request.user)
            if user_sort_prefs.exists():
                user_sort_dict = {str(pref.portal_id): pref.sort_order for pref in user_sort_prefs}

                def sort_key(portal):
                    return user_sort_dict.get(str(portal.id), portal.sort_order)
                queryset = sorted(queryset, key=sort_key)
            else:
                queryset = queryset.order_by('groups', 'sort_order')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 验证用户是否有权使用指定的分组
        groups = serializer.validated_data.get('groups', [])
        for group in groups:
            if group.sharing_type == 'private' and group.owner != request.user:
                return Response(
                    {'error': f'您没有权限将门户添加到分组 {group.group}'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # 检查公共分组不能添加私有门户
            if group.sharing_type == 'public' and serializer.validated_data.get('sharing_type') == 'private':
                return Response(
                    {'error': f'不能将私有门户添加到公共分组 {group.group} 中'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # 设置门户创建者为当前用户
        serializer.validated_data['owner'] = request.user

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # 检查权限：只有门户创建者可以更新门户
        if instance.owner != request.user:
            return Response(
                {'error': '您没有权限修改此门户'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # 如果要更改分组，验证用户是否有权使用新分组
        new_groups = serializer.validated_data.get('groups', instance.groups.all())
        for group in new_groups:
            if group.sharing_type == 'private' and group.owner != request.user:
                return Response(
                    {'error': f'您没有权限将门户移至分组 {group.group}'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # 检查公共分组不能添加私有门户
            if group.sharing_type == 'public' and serializer.validated_data.get('sharing_type') == 'private':
                return Response(
                    {'error': f'不能将私有门户添加到公共分组 {group.group} 中'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    @action(methods=['delete'], detail=False)
    def multiple_delete(self, request, *args, **kwargs):
        pks = request.data.get('pks', None)
        if not pks:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # 检查权限：用户只能删除自己创建的门户
        portals = Portal.objects.filter(id__in=pks)
        for portal in portals:
            if portal.owner != request.user:
                return Response(
                    {'error': f'您没有权限删除门户 {portal.name}'},
                    status=status.HTTP_403_FORBIDDEN
                )

        for pk in pks:
            get_object_or_404(Portal, id=int(pk)).delete()

        return Response(data='delete success', status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=False)
    def update_user_sort_order(self, request, *args, **kwargs):
        """
        更新当前用户的门户排序偏好
        支持两种模式：
        1. 全局排序：更新所有门户的排序
        2. 分组内排序：只更新指定分组内的门户排序

        请求参数格式：
        {
            "ordering": [
                {"id": "uuid1", "sort_order": 1},
                {"id": "uuid2", "sort_order": 2},
                {"id": "uuid3", "sort_order": 3}
            ],
            "group_id": "可选，指定分组ID"
        }
        """
        ordering_data = request.data.get('ordering', [])
        group_id = request.data.get('group_id', None)

        if not ordering_data:
            return Response(
                {'error': '排序数据不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            updated_count = 0
            for item in ordering_data:
                portal_id = item.get('id')
                sort_value = item.get('sort_order')

                if not portal_id or sort_value is None:
                    continue

                # 检查用户是否有权限更新该门户
                try:
                    portal = Portal.objects.get(id=portal_id)
                    # 验证用户是否有权访问该门户
                    if not (portal.sharing_type == 'public' or portal.owner == request.user):
                        continue  # 跳过无权限的门户

                    # 如果指定了分组ID，验证门户是否属于该分组
                    if group_id:
                        try:
                            group = Pgroup.objects.get(id=group_id)
                            if not portal.groups.filter(id=group_id).exists():
                                continue  # 跳过不属于指定分组的门户
                        except Pgroup.DoesNotExist:
                            continue  # 跳过不存在的分组

                    # 更新或创建用户排序偏好
                    defaults = {'sort_order': sort_value}
                    if group_id:
                        group = Pgroup.objects.get(id=group_id)
                        defaults['group'] = group

                    UserPortalSortOrder.objects.update_or_create(
                        user=request.user,
                        portal=portal,
                        defaults=defaults
                    )
                    updated_count += 1
                except Portal.DoesNotExist:
                    continue  # 跳过不存在的门户
                except Pgroup.DoesNotExist:
                    continue  # 跳过不存在的分组

            return Response({
                'detail': f'成功更新 {updated_count} 个门户的用户排序偏好',
                'updated_count': updated_count
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'更新排序时发生错误: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(methods=['post'], detail=True)
    def add_to_favorites(self, request, pk=None):
        """
        将门户添加到当前用户的收藏夹
        """
        portal = self.get_object()

        # 检查用户是否有权限访问该门户
        if not (portal.sharing_type == 'public' or portal.owner == request.user):
            return Response(
                {'error': '您没有权限收藏此门户'},
                status=status.HTTP_403_FORBIDDEN
            )

        # 创建收藏记录
        favorite, created = PortalFavorites.objects.get_or_create(
            user=request.user,
            portal=portal
        )

        if created:
            return Response(
                {'detail': '门户已添加到收藏夹'},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'detail': '门户已在收藏夹中'},
                status=status.HTTP_200_OK
            )

    @action(methods=['delete'], detail=True)
    def remove_from_favorites(self, request, pk=None):
        """
        从当前用户的收藏夹中移除门户
        """
        portal = self.get_object()

        try:
            favorite = PortalFavorites.objects.get(
                user=request.user,
                portal=portal
            )
            favorite.delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )
        except PortalFavorites.DoesNotExist:
            return Response(
                {'error': '门户不在您的收藏夹中'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(methods=['get'], detail=False)
    def favorites(self, request):
        """
        获取当前用户的收藏门户列表
        """
        favorites = PortalFavorites.objects.filter(user=request.user).select_related('portal')

        # 获取收藏的门户对象
        portals = [fav.portal for fav in favorites]

        # 应用门户查询集的过滤逻辑
        user = request.user
        accessible_portals = []
        for portal in portals:
            # 检查门户是否仍然可访问
            if (portal.sharing_type == 'public' or portal.owner == user) and \
               (portal.groups.filter(sharing_type='public').exists() or
                    portal.groups.filter(sharing_type='private', owner=user).exists()):
                accessible_portals.append(portal)

        # 应用排序
        user_sort_prefs = UserPortalSortOrder.objects.filter(
            user=request.user,
            portal__in=accessible_portals
        )

        if user_sort_prefs.exists():
            user_sort_dict = {str(pref.portal_id): pref.sort_order for pref in user_sort_prefs}

            def sort_key(portal):
                return user_sort_dict.get(str(portal.id), portal.sort_order)
            accessible_portals = sorted(accessible_portals, key=sort_key)
        else:
            # 默认按收藏时间排序
            portal_favorite_map = {fav.portal_id: fav.create_time for fav in favorites}
            accessible_portals.sort(key=lambda p: portal_favorite_map.get(p.id, p.create_time))

        page = self.paginate_queryset(accessible_portals)
        if page is not None:
            serializer = getPortalModelSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = getPortalModelSerializer(accessible_portals, many=True, context={'request': request})
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def is_favorite(self, request):
        """
        检查指定门户是否在当前用户的收藏夹中
        查询参数:
        - portal_id: 门户ID
        """
        portal_id = request.query_params.get('portal_id', None)
        if not portal_id:
            return Response(
                {'error': '请提供portal_id参数'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            Portal.objects.get(id=portal_id)  # 验证门户存在
            is_favorited = PortalFavorites.objects.filter(
                user=request.user,
                portal_id=portal_id
            ).exists()

            return Response({
                'portal_id': portal_id,
                'is_favorite': is_favorited
            })
        except Portal.DoesNotExist:
            return Response(
                {'error': '门户不存在'},
                status=status.HTTP_404_NOT_FOUND
            )


class PgroupViewSet(ModelViewSet):
    queryset = Pgroup.objects.all()
    serializer_class = PgroupModelSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['group']  # 支持搜索的字段

    def get_queryset(self):
        """
        默认查询所有公共分组和当前用户创建的私人分组
        """
        user = self.request.user
        return Pgroup.objects.filter(
            models.Q(sharing_type='public') |
            models.Q(sharing_type='private', owner=user)
        )

    def list(self, request, *args, **kwargs):
        # 获取查询参数
        sharing_type = request.query_params.get('sharing_type', None)
        owner = request.query_params.get('owner', None)

        queryset = self.get_queryset()

        # 如果指定了共享类型，则按指定类型过滤
        if sharing_type:
            queryset = queryset.filter(sharing_type=sharing_type)

        # 如果指定了所有者，则按所有者过滤
        if owner:
            queryset = queryset.filter(owner=owner)

        # 应用过滤器
        queryset = self.filter_queryset(queryset)

        # 应用排序
        # 首先尝试用户自定义排序，如果没有则使用默认排序
        user_sort_prefs = UserPgroupSortOrder.objects.filter(user=request.user)
        if user_sort_prefs.exists():
            # 如果用户有自定义排序，则使用用户排序
            user_sort_dict = {str(pref.pgroup_id): pref.sort_order for pref in user_sort_prefs}

            def sort_key(group):
                return user_sort_dict.get(str(group.id), group.sort_order)

            queryset = sorted(queryset, key=sort_key)
        else:
            # 默认按照sort_order字段排序
            queryset = queryset.order_by('sort_order')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 设置分组创建者为当前用户
        serializer.validated_data['owner'] = request.user

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # 检查权限：只有分组创建者可以更新分组
        if instance.owner != request.user:
            return Response(
                {'error': '您没有权限修改此分组'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # 检查权限：只有分组创建者可以删除分组
        if instance.owner != request.user:
            return Response(
                {'error': '您没有权限删除此分组'},
                status=status.HTTP_403_FORBIDDEN
            )

        # 检查分组是否被门户使用
        if instance.portals.exists():
            return Response(
                {'error': '该分组下仍有门户，无法删除'},
                status=status.HTTP_400_BAD_REQUEST
            )

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['delete'], detail=False)
    def multiple_delete(self, request, *args, **kwargs):
        pks = request.data.get('pks', None)
        if not pks:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # 检查权限：用户只能删除自己创建的分组
        groups = Pgroup.objects.filter(id__in=pks)
        for group in groups:
            if group.owner != request.user:
                return Response(
                    {'error': f'您没有权限删除分组 {group.group}'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # 检查分组是否被门户使用
            if group.portals.exists():
                return Response(
                    {'error': f'分组 {group.group} 下仍有门户，无法删除'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        for pk in pks:
            get_object_or_404(Pgroup, id=int(pk)).delete()

        return Response(data='delete success', status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=False)
    def update_user_sort_order(self, request, *args, **kwargs):
        """
        更新当前用户的分组排序偏好
        请求参数格式：
        {
            "ordering": [
                {"id": "uuid1", "sort_order": 1},
                {"id": "uuid2", "sort_order": 2},
                {"id": "uuid3", "sort_order": 3}
            ]
        }
        """
        ordering_data = request.data.get('ordering', [])

        if not ordering_data:
            return Response(
                {'error': '排序数据不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            updated_count = 0
            for item in ordering_data:
                group_id = item.get('id')
                sort_value = item.get('sort_order')

                if not group_id or sort_value is None:
                    continue

                # 检查分组是否存在且用户有权访问
                try:
                    group = Pgroup.objects.get(id=group_id)
                    # 验证用户是否有权访问该分组
                    if not (group.sharing_type == 'public' or group.owner == request.user):
                        continue  # 跳过无权限的分组

                    # 更新或创建用户排序偏好
                    UserPgroupSortOrder.objects.update_or_create(
                        user=request.user,
                        pgroup=group,
                        defaults={'sort_order': sort_value}
                    )
                    updated_count += 1
                except Pgroup.DoesNotExist:
                    continue  # 跳过不存在的分组

            return Response({
                'detail': f'成功更新 {updated_count} 个分组的用户排序偏好',
                'updated_count': updated_count
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'更新排序时发生错误: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PortalFavoritesViewSet(ModelViewSet):
    """
    门户收藏夹视图集
    """
    serializer_class = PortalFavoritesSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    def get_queryset(self):
        # 只返回当前用户的收藏
        return PortalFavorites.objects.filter(user=self.request.user).select_related('portal')

    def list(self, request, *args, **kwargs):
        """
        获取当前用户的收藏列表
        """
        queryset = self.filter_queryset(self.get_queryset())

        # 默认按收藏时间倒序排列
        queryset = queryset.order_by('-create_time')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        添加门户到收藏夹
        """
        portal_id = request.data.get('portal')
        if not portal_id:
            return Response(
                {'error': '请提供门户ID'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            portal = Portal.objects.get(id=portal_id)
        except Portal.DoesNotExist:
            return Response(
                {'error': '门户不存在'},
                status=status.HTTP_404_NOT_FOUND
            )

        # 检查用户是否有权限访问该门户
        if not (portal.sharing_type == 'public' or portal.owner == request.user):
            return Response(
                {'error': '您没有权限收藏此门户'},
                status=status.HTTP_403_FORBIDDEN
            )

        # 检查是否已经在收藏夹中
        if PortalFavorites.objects.filter(user=request.user, portal=portal).exists():
            return Response(
                {'error': '门户已在收藏夹中'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 创建收藏记录
        favorite = PortalFavorites.objects.create(
            user=request.user,
            portal=portal
        )

        serializer = self.get_serializer(favorite)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """
        从收藏夹中移除门户
        """
        instance = self.get_object()
        # 额外验证确保用户只能删除自己的收藏
        if instance.user != request.user:
            return Response(
                {'error': '您没有权限执行此操作'},
                status=status.HTTP_403_FORBIDDEN
            )

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['delete'], detail=False)
    def batch_remove(self, request):
        """
        批量移除收藏
        请求参数:
        {
            "portal_ids": ["uuid1", "uuid2", "uuid3"]
        }
        """
        portal_ids = request.data.get('portal_ids', [])
        if not portal_ids:
            return Response(
                {'error': '请提供门户ID列表'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 删除指定的收藏记录
        deleted_count, _ = PortalFavorites.objects.filter(
            user=request.user,
            portal_id__in=portal_ids
        ).delete()

        return Response({
            'detail': f'成功移除 {deleted_count} 个收藏',
            'deleted_count': deleted_count
        })


class dataSourceViewSet(ModelViewSet):
    queryset = Datasource.objects.all()
    serializer_class = DatasourceModelSerializer

    def create(self, request, *args, **kwargs):
        reqJson = json.loads(request.body.decode("utf8"))
        isDefault = reqJson["isDefault"]

        source_name_exists = Datasource.objects.filter(source_name=reqJson["source_name"])
        if len(source_name_exists) != 0:
            return Response({"code": 201, "results": "failed", "reason": "%s has been create" % reqJson["source_name"]})

        getDefault = Datasource.objects.filter(isDefault=True).first()
        if getDefault and isDefault == True:
            print(123)
            pkId = getDefault.id

            getDefault.isDefault = False
            getDefault.save()
            Datasource.objects.create(**reqJson)
            return Response({"code": 200, "results": "success"})
        else:
            Datasource.objects.create(**reqJson)
            return Response({"code": 200, "results": "success"})

        # if isDefault:
        #     getDefault = Datasource.objects.filter(isDefault=True)
        #     print(getDefault)
        #     if len(getDefault) == 0:
        #         try:
        #             Datasource.objects.create(**reqJson)

        #         except Exception as e:
        #             return Response({"code":201,"results":"failed","reason":str(e)})
        #         else:
        #             return Response({"code":200,"results":"success"})

        # else:
        #     try:
        #         Datasource.objects.create(**reqJson)

        #     except Exception as e:
        #         return Response({"code":201,"results":"failed","reason":str(e)})
        #     else:
        #         return Response({"code":200,"results":"success"})

    def update(self, request, pk):
        # updateSource = Datasource.objects.filter(id=pk).first()
        reqJson = json.loads(request.body.decode("utf8"))
        getDefault = Datasource.objects.filter(isDefault=True).first()

        if reqJson["isDefault"] and getDefault:
            if getDefault.id != pk:
                getDefault.isDefault = False
                getDefault.save()
        Datasource.objects.filter(id=pk).update(**reqJson)
        return Response({"code": 200, "results": "success"})

# class LogModuleViewSet(ModelViewSet):
#   queryset = LogModule.objects.all()
#   serializer_class = LogModuleModelSerializer


class sysConfigViewSet(ModelViewSet):
    queryset = sysConfigParams.objects.all()
    serializer_class = SysConfigSerializer
    pagination_class = None
    # filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filterset_class = sysConfigParamsFilter
    ordering_fields = ['param_name', 'param_value',]
    search_fields = ('param_name', 'param_value',)

    def list(self, request, *args, **kwargs):
        if (request.query_params.get('params') == "gm"):
            secretKey = sysConfigParams.objects.get(param_name="secret_key").param_value
            keyMode = sysConfigParams.objects.get(param_name="secret_mode").param_value
            return Response({"key": secretKey, "mode": keyMode})
        # 在这里可以对queryset进行进一步的筛选或处理
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['post'], detail=False)
    def update_zabbix_params(self, request, *args, **kwargs):
        params = json.loads(request.body)
        # print(params)
        params_to_update = sysConfigParams.objects.filter(param_name__in=params.keys())
        for param in params_to_update:
            param.param_value = params[param.param_name]
        # 更新
        try:
            sysConfigParams.objects.bulk_update(params_to_update, ["param_value"])
            # 触发配置文件加载
            sys_config = ConfigManager()
            # 强制刷新
            sys_config.reload()
            logger.info(f"刷新redis<{params}>")
        except Exception as e:
            return Response(data=e)
        return Response(data='update success')
