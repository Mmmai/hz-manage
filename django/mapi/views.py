import tempfile
import json

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from rest_framework.filters import SearchFilter
from rest_framework import filters, status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from node_mg.utils.config_manager import ConfigManager
from cmdb.utils import password_handler

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
    authentication_classes = [] # 取消全局认证
    def post(self,request,*args,**kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        # 查找用户
        user_obj = UserInfo.objects.filter(username=username).first()
        if not user_obj:
            return Response({'code':401,'error':'用户名不存在!'})
        # 检查用户是否已过期（admin等内置用户除外）
        if user_obj.is_expired():
            return Response({'code':401,'error':'用户账户已过期!'})
            
        # 检查用户状态
        if not user_obj.status:
            return Response({'code':401,'error':'用户已被禁用!'})            
        try:
            # 使用用户存储的盐值处理输入的密码
            salted_password = f'{user_obj.password_salt}:{password}'
            # 使用SM4加密加盐后的密码
            encrypted_password = password_handler.encrypt_to_sm4(salted_password)
            # 比较加密后的密码
            if user_obj.password != encrypted_password:
                return Response({'code':401,'error':'用户密码错误!'})
        except Exception as e:
            logger.error(f"Password verification failed: {str(e)}")
            return Response({'code':401,'error':'密码认证失败!'})
        # 获取用户组id
        userGroupList = [i['id'] for i in user_obj.groups.all().values('id')]
        #
        userGroupRoleList = []
        for group in userGroupList:
            group_obj = UserGroup.objects.get(id=group)
            for group_role in group_obj.roles.all():
                userGroupRoleList.append(group_role.id)
        # 获取用户权限
        permissionObjects = Permission.get_user_permissions(user_obj) 
        allPermissionList = [ f"{permissionObj.menu.name}:{permissionObj.button.action}" for permissionObj in permissionObjects]
        #print(roleList)
        payload = {
            'user_id':str(user_obj.pk),#自定义用户ID
            'username':user_obj.username,#自定义用户名
            'password': user_obj.password,  # 添加密码字段用于验证token有效性
            # 'exp':datetime.datetime.utcnow()+datetime.timedelta(minutes=1),# 设置超时时间，1min
        }
        timeout = request.data.get('timeout',3)
        jwt_token = create_token(payload=payload,timeout=timeout)
        return Response({'code':200,'token':jwt_token,"userinfo":{'user_id':str(user_obj.pk),'username':user_obj.username,},"permission":allPermissionList})




class getSecret(APIView):
    def get(self,request,*args,**kwargs):
        # 获取头部token

        return Response({"secret":settings.SECRET_KEY})
    def post(self,request,*args,**kwargs):
        # 获取头部token
        token = request.META.get('HTTP_TOKEN')
        return Response({"secret":settings.SECRET_KEY})

class getMenu(APIView):
    """动态路由"""
    def __init__(self):
        self.get_menu_tree = self.get_menu_tree
    
    def post(self, request, *args, **kwargs):
        # 获取当前用户
        user_obj = request.user
        
        # 根据当前用户获取其所有权限
        user_permissions = Permission.get_user_permissions(user_obj)
        
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
# 获取角色授权页面的tree


class getPermissionToRole(APIView):
    def __init__(self):
        self.get_menu_tree = self.get_menu_tree

    def post(self, request, *args, **kwargs):
        menuobj = Menu.objects.all().order_by('sort')
        menuList = self.get_menu_tree(menuobj)
        # print(menuList)
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
            # print(info)
            # 如果是目录，但是没有子目录，则跳过
            # if menu.is_menu == False and len(info['children']) == 0:
            #     continue
            if menu.is_menu:
                # 添加按钮到对应菜单下
                info["children"] = [{"id": str(i.id), "label": i.name, "button": i.action, "tree_type": "button"}
                                    for i in Button.objects.filter(menu=menu).all().order_by('action')]
            tree.append(info)
        return tree
# 获取当前用户的权限列表


class getUserButton(APIView):
    def post(self, request, *args, **kwargs):
        # owner = request.query_params.get('owner')
        # orderRes =  orderMethod.objects.filter(owner=owner).first()
        role_ids = request.data.get('role')
        # 拿permission表中所有权限,菜单name:按钮action,例如：home:edit
        allPermissionList = []
        for role_id in role_ids:
            for p_obj in Permission.objects.filter(role=role_id).all():
                menu_name = p_obj.menu.name
                # button_name = Button.objects.get(id=p_obj.button).action
                button_name = p_obj.button.action
                allPermissionList.append(f"{menu_name}:{button_name}")
        # print(allPermissionList)
        return Response({'code':200,"results":allPermissionList})



class UserInfoViewSet(ModelViewSet):
    queryset = UserInfo.objects.all()
    # 认证
    authentication_classes = [JWTQueryParamsAuthentication, ]
    serializer_class = UserInfoModelSerializer
    # pagination_class = defaultPageNumberPagination
    # filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)  # 指定后端
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
            for button_id in rolePermission:
                button_obj = Button.objects.get(id=button_id)
                Permission.objects.update_or_create(role=instance, menu=button_obj.menu, button=button_obj)
                logger.info(f"为角色<{instance.role}>添加<{button_obj.action}>权限!")
                # 如果有其他按钮权限，查看的权限应该同步添加，就算用户没有勾选！
                if button_obj.action != "view":
                    pass
                else:
                    view_button_obj = Button.objects.get(action="view", menu=button_obj.menu)
                    view_per_obj, created = Permission.objects.get_or_create(role=instance, menu=button_obj.menu, button=view_button_obj)
                    if created:
                        logger.info(f"为角色<{instance.role}>添加<{view_button_obj.action}>权限!")
                    else:
                        logger.info(f"为角色<{instance.role}>已拥有<{view_button_obj.action}>权限!")
        
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
            # instance.permission.all()
            # print(instance)
            # 判断原有的，若相同，则不处理
            currentPermissionList = [str(i) for i in Permission.objects.filter(
                role=instance).values_list("button", flat=True)]
            if sorted(rolePermission) == sorted(currentPermissionList):
                pass
            else:
                # 先清空原有的，再添加新的
                instance.permission.all().delete()
                logger.info(f"清空角色<{instance.role}>权限!")
                # 添加新的
                for button_id in rolePermission:
                    button_obj = Button.objects.get(id=button_id)
                    Permission.objects.create(role=instance, menu=button_obj.menu, button=button_obj)
                    logger.info(f"为角色<{instance.role}>添加<${button_obj.action}>权限!")
                    # 如果有其他按钮权限，查看的权限应该同步添加，就算用户没有勾选！
                    if button_obj.action == "view":
                        pass
                    else:
                        view_button_obj = Button.objects.get(action="view", menu=button_obj.menu)
                        view_per_obj, created = Permission.objects.get_or_create(
                            role=instance, menu=button_obj.menu, button=view_button_obj)
                        if created:
                            logger.info(f"为角色<{instance.role}>添加<${view_button_obj.action}>权限!")
                        else:
                            logger.info(f"为角色<{instance.role}>已拥有<${view_button_obj.action}>权限!")
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
        
        added_permissions = []
        existing_permissions = []
        
        for button_id in button_ids:
            try:
                button_obj = Button.objects.get(id=button_id)
                # 检查权限是否已存在
                permission, created = Permission.objects.get_or_create(
                    role=role,
                    menu=button_obj.menu,
                    button=button_obj
                )
                
                if created:
                    added_permissions.append(str(button_id))
                    logger.info(f"为角色<{role.role}>添加<{button_obj.action}>权限!")
                    
                    # 如果不是查看权限，确保查看权限也存在
                    if button_obj.action != "view":
                        view_button_obj = Button.objects.get(action="view", menu=button_obj.menu)
                        view_per_obj, view_created = Permission.objects.get_or_create(
                            role=role,
                            menu=button_obj.menu,
                            button=view_button_obj
                        )
                        if view_created:
                            logger.info(f"为角色<{role.role}>添加<{view_button_obj.action}>权限!")
                else:
                    existing_permissions.append(str(button_id))
            except Button.DoesNotExist:
                return Response({'error': f'按钮权限ID {button_id} 不存在'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'error': f'添加权限时出错: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
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
        
        removed_permissions = []
        
        for button_id in button_ids:
            try:
                button_obj = Button.objects.get(id=button_id)
                
                # 如果移除的是"查看"权限，则同步移除该菜单下的所有权限
                if button_obj.action == 'view':
                    # 先获取该菜单下的所有权限用于返回
                    menu_permissions = Permission.objects.filter(
                        role=role, 
                        menu=button_obj.menu
                    )
                    for perm in menu_permissions:
                        if perm.button:
                            removed_permissions.append(str(perm.button.id))
                    
                    # 删除该菜单下的所有权限
                    deleted_count, _ = Permission.objects.filter(
                        role=role,
                        menu=button_obj.menu
                    ).delete()
                    
                    logger.info(f"从角色<{role.role}>删除<{button_obj.menu.name}>菜单下的所有权限!")
                else:
                    # 删除指定权限
                    deleted_count, _ = Permission.objects.filter(
                        role=role,
                        menu=button_obj.menu,
                        button=button_obj
                    ).delete()
                    
                    if deleted_count > 0:
                        removed_permissions.append(str(button_id))
                        logger.info(f"从角色<{role.role}>删除<{button_obj.action}>权限!")
            except Button.DoesNotExist:
                return Response({'error': f'按钮权限ID {button_id} 不存在'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'error': f'删除权限时出错: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # 去重
        removed_permissions = list(set(removed_permissions))
        
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


class MenuViewSet(ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuModelSerializer
    @action(detail=False, methods=['get'], url_path='get_menu_tree')
    def get_menu_tree(self, request):
        menuobj = Menu.objects.all().order_by('sort')
        menuList = self._get_menu_tree(menuobj)
        # print(menuList)
        return Response({'code':200,"results":menuList})
    def _get_menu_tree(self,menu_list,parent=None):
        tree = []
        for menu in menu_list.filter(parentid=parent):
            if menu.is_menu:
                # 添加按钮到对应菜单下
                info = {"id":menu.id,"label":menu.label,"tree_type":"menu"}
            else:
                info = {"id":menu.id,"label":menu.label,"tree_type":"directory"}
            info['children'] = self._get_menu_tree(menu_list,menu)
            # print(info)
                # 如果是目录，但是没有子目录，则跳过
            # if menu.is_menu == False and len(info['children']) == 0:
            #     continue
            if menu.is_menu:
                # 添加按钮到对应菜单下
                info["children"] = [ {"id":str(i.id),"label":i.name,"button":i.action,"tree_type":"button"} for i in Button.objects.filter(menu=menu).all().order_by('action')]  
            tree.append(info)
        return tree    


class ButtonViewSet(ModelViewSet):
    queryset = Button.objects.all()
    serializer_class = ButtonModelSerializer
    filterset_class = buttonFilter

class PermissionViewSet(ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class =  PermissionModelSerializer   
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
                permissions = Permission.get_user_permissions(user)
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
                print(e)
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

class PortalViewSet(ModelViewSet):
    queryset = Portal.objects.all()
    # serializer_class = PortalModelSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return getPortalModelSerializer
        else:
            return PortalModelSerializer
    # pagination_class = defaultPageNumberPagination

    def list(self, request, *args, **kwargs):
        # queryset = self.filter_queryset(self.get_queryset())
        # serializer_class = getPortalModelSerializer

        # owner = request.query_params.get('owner', None)
        # if owner is not None:
        #     queryset = Portal.objects.filter(owner=owner)
        # else:
        #     queryset = self.get_queryset()
        queryset = self.get_queryset()
        page = self.paginate_queryset(self.get_queryset())
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['delete'], detail=False)
    def multiple_delete(self, request, *args, **kwargs):
        # pks = request.query_params.get('pks', None)
        pks = request.data.get('pks', None)
        print(request.data)
        if not pks:
            return Response(status=status.HTTP_404_NOT_FOUND)
        for pk in pks:
            get_object_or_404(Portal, id=int(pk)).delete()

        return Response(data='delete success', status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=False)
    def export_template(self, request, *args, **kwargs):
        # request.data.body('pks', None)
        # 获取Pg字段和列表
        model_fields = Portal._meta.fields
        colList = [["名称", "链接地址", "状态", "分组", "用户名", "密码", "描述"]]
        # for i in model_fields:
        #     # print(type(i))
        #     # print(i.verbose_name)
        #     if i.name in ["id","update_time","create_time"]:
        #         continue
        #     colList.append(i.verbose_name)
        excel_handler = exportHandler()
        wb = excel_handler.get_template(colList=colList)
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        # 设置文件的名称，让浏览器提示用户保存文件
        response['Content-Disposition'] = 'attachment; filename="portal_template.xlsx"'
        wb.save(response)
        return response
        # return Response(data='delete success', status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False)
    def export_portal(self, request, *args, **kwargs):
        # request.data.body('pks', None)
        # 获取Pg字段和列表
        model_fields = Portal._meta.fields

        colList = [["名称", "链接地址", "状态", "分组", "用户名", "密码", "描述"]]

        # for i in model_fields:
        #     # print(type(i))
        #     # print(i.verbose_name)
        #     if i.name in ["id","update_time","create_time"]:
        #         continue
        #     colList.append(i.verbose_name)
        portalObj = Portal.objects.all()
        for i in portalObj:
            # pgroupObj = Pgroup.objects.get(id=str(i.group))
            colList.append([i.name, i.url, i.status, i.group.group, i.username, i.password, i.describe])
        excel_handler = exportHandler()
        wb = excel_handler.get_portal(colList=colList)
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        # 设置文件的名称，让浏览器提示用户保存文件
        response['Content-Disposition'] = 'attachment; filename="portal_data.xlsx"'
        wb.save(response)
        return response
        # return Response(data='delete success', status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False)
    def import_portal(self, request, *args, **kwargs):
        portal_file = request.FILES.get('file')
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp:
            for chunk in portal_file.chunks():
                temp.write(chunk)
            temp_path = temp.name
        excel_handler = exportHandler()
        allRow = excel_handler.load_data(temp_path)
        # print(allRow)
        for row in allRow:
            name, url, p_status, group, username, password, describe = row
            pgroupObj, is_create = Pgroup.objects.get_or_create(group=group)
            Portal.objects.update_or_create(name=name,
                                            defaults={"url": url, "group": pgroupObj, "status": p_status, "username": username, "password": password, "describe": describe})

        return Response(data={"count": len(allRow)}, status=status.HTTP_200_OK)


class PgroupViewSet(ModelViewSet):
    queryset = Pgroup.objects.all()
    serializer_class = PgroupModelSerializer
    # pagination_class = defaultPageNumberPagination

    def list(self, request, *args, **kwargs):
        # queryset = self.filter_queryset(self.get_queryset())
        # owner = request.query_params.get('owner', None)
        # if owner is not None:
        #     queryset = Pgroup.objects.filter(owner=owner)
        # else:
        #     queryset = self.get_queryset()
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['delete'], detail=False)
    def multiple_delete(self, request, *args, **kwargs):
        # pks = request.query_params.get('pks', None)

        pks = request.data.get('pks', None)
        print(request.data)
        if not pks:
            return Response(status=status.HTTP_404_NOT_FOUND)
        for pk in pks:
            get_object_or_404(Pgroup, id=int(pk)).delete()

        return Response(data='delete success', status=status.HTTP_204_NO_CONTENT)


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
    # filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
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
