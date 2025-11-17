from django.shortcuts import render
from rest_framework.filters import SearchFilter

from django.http import HttpResponse,JsonResponse
from rest_framework import filters,status
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.renderers import JSONRenderer
from .sers import *
import tempfile
from rest_framework.views import APIView
from rest_framework.response import Response
# from .models import UserInfo,Role,Menu,Portal,Pgroup,Datasource,LogModule
from .models import (
  UserInfo,UserGroup,Role,Menu,Button,Permission,Portal,Pgroup,Datasource,
  sysConfigParams
  )
from .filters import (
    roleFilter,
    sysConfigParamsFilter,
    buttonFilter   
)
from .utils.jwt_create_token import create_token
from rest_framework.pagination import PageNumberPagination
from .extensions.jwt_authenticate import JWTQueryParamsAuthentication
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
import json
from django.conf import settings
from mapi.extensions.pagination import StandardResultsSetPagination
from .export import exportHandler
from node_mg.utils.config_manager import ConfigManager
from cmdb.utils import password_handler

import logging
logger = logging.getLogger(__name__)
def getRolePermissionList(role_ids):
    allPermissionList = []
    for role_id in role_ids:
        for p_obj in Permission.objects.filter(role=role_id).all():
            menu_name = p_obj.menu.name
            # button_name = Button.objects.get(id=p_obj.button).action
            button_name = p_obj.button.action
            allPermissionList.append(f"{menu_name}:{button_name}")
    return allPermissionList
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
        userGroupList = [ i['id'] for i in user_obj.groups.all().values('id') ]
        # 
        userGroupRoleList = []
        for group in userGroupList:
            group_obj = UserGroup.objects.get(id=group)
            for group_role in group_obj.roles.all():
                userGroupRoleList.append(group_role.id)
        # 判断用户的role
        userRoleList = [ i['id'] for i in user_obj.roles.all().values('id') ]
        roleList = list(set(userGroupRoleList + userRoleList))
        permissionList = getRolePermissionList(role_ids=roleList)
        #print(roleList)
        payload = {
            'user_id':str(user_obj.pk),#自定义用户ID
            'username':user_obj.username,#自定义用户名
            'password': user_obj.password,  # 添加密码字段用于验证token有效性
            # 'exp':datetime.datetime.utcnow()+datetime.timedelta(minutes=1),# 设置超时时间，1min
        }
        timeout = request.data.get('timeout',7)
        jwt_token = create_token(payload=payload,timeout=timeout)
        return Response({'code':200,'token':jwt_token,"role":roleList,"userinfo":{'user_id':str(user_obj.pk),'username':user_obj.username,},"permission":permissionList})




class getSecret(APIView):
    # def post(self,request,*args,**kwargs):
    #     owner = request.data.get('owner')
    #     orderRes = request.data.get('orderRes')
    #     orderObj = orderMethod.objects.filter(owner=owner).first()
    #     orderObj.update(orderList={"orderList":orderRes})
    #     return Response({'code':200,'results':'success'})

    def get(self,request,*args,**kwargs):
        # owner = request.query_params.get('owner')
        # orderRes =  orderMethod.objects.filter(owner=owner).first()
        secretKey = settings.SECRET_KEY
        return Response({"secret":secretKey})
# Create your views here.
# def test(request):
#   data = {'1':2,'3':4}
#   return JsonResponse(data)



# def user(request):
class getMenu(APIView):
    def __init__(self):
        self.get_menu_tree = self.get_menu_tree
    def post(self,request,*args,**kwargs):
        # print(request.query_params)
        # print(request.GET.getlist('role'))
        # role = request.GET.getlist('role')
        # print(request.GET.get('role[]'))
        role = request.data.get('role')
        menuobj = Menu.objects.all().order_by('sort')
        # # print(menuobj)
        # for i in menuobj.all():
        #     print(i.__dict__.copy())
        menuList = self.get_menu_tree(menuobj,role)
        # print(menuList)
        return Response({'code':200,"results":menuList})

    def get_menu_tree(self,menu_list,role,parent=None):
        tree = []
        for menu in menu_list.filter(parentid=parent):
            # if not menu.status:
            #     continue
            
            roleList = []
            # for r in menu.role_set.all().values():
            #     roleList.append(str(r["id"]))
            # 获取角色列表

            roleList = list(set([ str(i.role.id) for i in Permission.objects.filter(menu=menu).all()]))
            # print(roleList)
            # print(123)
            # print(role)
            # if len(list(set(roleList) & set(role))) == 0:
            #     continue
            button_queryset = menu.buttons.all().order_by("action")
            button_serializer = ButtonModelSerializer(button_queryset, many=True)
            serialized_data = JSONRenderer().render(button_serializer.data)
            info = menu.__dict__.copy()
            info.pop('_state')
            parentid = info.pop('parentid_id')
            info["parentid"] = parentid
            info["meta"] = {"role":roleList,"icon":menu.icon,"title":menu.label,"isKeepAlive":menu.keepalive}
            info["buttons"] = json.loads(serialized_data.decode('utf8'))
            # info["button"] 
            if info["is_iframe"]:
                info["meta"]["iframePath"] = info["iframe_url"]
                info["meta"]["is_iframe"] = info["is_iframe"]
            # if info["is_menu"]:
            #     # print(info["label"])
            #     info["meta"]["permission"] = []
                        # 构建菜单全路径
            path_labels = []
            current = menu
            while current:
                path_labels.insert(0, {'name':current.label,'icon': current.icon})
                current = current.parentid
            # menu_path = "/".join(path_labels)
            
            # 添加meta信息，包含菜单全路径
            info["meta"].update({"menuPath": path_labels}) 
            info['children'] = self.get_menu_tree(menu_list,role,menu)
            # print(info)

            if role != None:
                # currentRoleList = [ i for i in role.split(',')]
                if len(list(set(roleList) & set(role))) == 0:
                    if menu.is_menu == True:
                        continue
                if menu.is_menu == False and len(info['children']) == 0:
                    continue
            tree.append(info)
        return tree
# 获取角色授权页面的tree
class getPermissionToRole(APIView):
    def __init__(self):
        self.get_menu_tree = self.get_menu_tree
    def post(self,request,*args,**kwargs):
        menuobj = Menu.objects.all().order_by('sort')
        menuList = self.get_menu_tree(menuobj)
        # print(menuList)
        return Response({'code':200,"results":menuList})

    def get_menu_tree(self,menu_list,parent=None):
        tree = []
        for menu in menu_list.filter(parentid=parent):
            if menu.is_menu:
                # 添加按钮到对应菜单下
                info = {"id":menu.id,"label":menu.label,"tree_type":"menu"}
            else:
                info = {"id":menu.id,"label":menu.label,"tree_type":"directory"}
            info['children'] = self.get_menu_tree(menu_list,menu)
            # print(info)
                # 如果是目录，但是没有子目录，则跳过
            # if menu.is_menu == False and len(info['children']) == 0:
            #     continue
            if menu.is_menu:
                # 添加按钮到对应菜单下
                info["children"] = [ {"id":str(i.id),"label":i.name,"button":i.action,"tree_type":"button"} for i in Button.objects.filter(menu=menu).all().order_by('action')]  
            tree.append(info)
        return tree
# 获取当前用户的权限列表
class getUserButton(APIView):
    def post(self,request,*args,**kwargs):
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
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter)  # 指定后端
    # 视图中设置了 search_fields 属性时，才会应用 SearchFilter 类
    # search_fields只支持文本类型字段，例如 CharField 或 TextField
    search_fields = ('$username',)

    def list(self, request, *args, **kwargs):
        # request.query_params = request.data
        # page = request.data['page']
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
        pks = request.data.get('pks',None)
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
        UserInfo.objects.filter(id__in=pks).delete()
        return Response(data='delete success',status=status.HTTP_204_NO_CONTENT)
class UserGroupViewSet(ModelViewSet):
    queryset = UserGroup.objects.all()
    serializer_class =  UserGroupModelSerializer
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
    serializer_class =  RoleModelSerializer
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
                if button_obj.action == "view":
                    pass
                    add =     'd'
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
        rolePermission = request.data.get('rolePermission',None)
        if not rolePermission:
            pass
        else:
            # return
            # print(rolePermission)
            # instance.permission.all()
            # print(instance)
            # 判断原有的，若相同，则不处理
            currentPermissionList = [ str(i) for i in  Permission.objects.filter(role=instance).values_list("button",flat=True)]
            if sorted(rolePermission) == sorted(currentPermissionList):
                pass
            else:
                # print(123)
                # 先清空原有的，再添加新的
                instance.permission.all().delete()
                logger.info(f"清空角色<{instance.role}>权限!")
                # 添加新的
                for button_id in rolePermission:
                    button_obj = Button.objects.get(id=button_id)
                    Permission.objects.create(role=instance,menu=button_obj.menu,button=button_obj)
                    logger.info(f"为角色<{instance.role}>添加<${button_obj.action}>权限!")
                    # 如果有其他按钮权限，查看的权限应该同步添加，就算用户没有勾选！
                    if button_obj.action == "view":
                        pass
                    else:
                        view_button_obj = Button.objects.get(action="view",menu=button_obj.menu)
                        view_per_obj, created = Permission.objects.get_or_create(role=instance,menu=button_obj.menu,button=view_button_obj)
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

class MenuViewSet(ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuModelSerializer
  # def get_serializer(self, *args, **kwargs):
  #     serializer_class = self.get_serializer_class()
  #     kwargs.setdefault('context', self.get_serializer_context())
  #     if isinstance(self.request.data, list):
  #         return serializer_class(many=True, *args, **kwargs)
  #     else:
  #         return serializer_class(*args, **kwargs)

class ButtonViewSet(ModelViewSet):
    queryset = Button.objects.all()
    serializer_class = ButtonModelSerializer
    filterset_class = buttonFilter

# class PermissionViewSet(ModelViewSet):
#   queryset = Menu.objects.all()
#   serializer_class =  PermissionModelSerializer


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
        colList = [["名称","链接地址","状态","分组","用户名","密码","描述"]]
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

        colList = [["名称","链接地址","状态","分组","用户名","密码","描述"]]

        # for i in model_fields:
        #     # print(type(i))
        #     # print(i.verbose_name)
        #     if i.name in ["id","update_time","create_time"]:
        #         continue
        #     colList.append(i.verbose_name)
        portalObj = Portal.objects.all()
        for i in portalObj:
            # pgroupObj = Pgroup.objects.get(id=str(i.group))
            colList.append([i.name,i.url,i.status,i.group.group,i.username,i.password,i.describe])
        excel_handler = exportHandler()
        wb = excel_handler.get_portal(colList=colList)
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        # 设置文件的名称，让浏览器提示用户保存文件
        response['Content-Disposition'] = 'attachment; filename="portal_data.xlsx"'
        wb.save(response)
        return response
        # return Response(data='delete success', status=status.HTTP_200_OK)
    @action(methods=['post'], detail=False)
    def import_portal(self,request, *args, **kwargs):
        portal_file = request.FILES.get('file')
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp:
            for chunk in portal_file.chunks():
                temp.write(chunk)
            temp_path = temp.name
        excel_handler = exportHandler()
        allRow = excel_handler.load_data(temp_path)
        # print(allRow)
        for row in allRow:
            name,url,p_status,group,username,password,describe = row
            pgroupObj,is_create = Pgroup.objects.get_or_create(group=group)
            Portal.objects.update_or_create(name=name,
                                           defaults={"url":url,"group":pgroupObj,"status":p_status,"username":username,"password":password,"describe":describe})


        return Response(data={"count":len(allRow)}, status=status.HTTP_200_OK)
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
            return Response({"code":201,"results":"failed","reason":"%s has been create" %reqJson["source_name"]})

        getDefault = Datasource.objects.filter(isDefault=True).first()
        if getDefault and isDefault == True:
            print(123)
            pkId = getDefault.id
            
            getDefault.isDefault = False
            getDefault.save()
            Datasource.objects.create(**reqJson)
            return Response({"code":200,"results":"success"})
        else:
            Datasource.objects.create(**reqJson)
            return Response({"code":200,"results":"success"})


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

    def update(self,request,pk):
        # updateSource = Datasource.objects.filter(id=pk).first()
        reqJson = json.loads(request.body.decode("utf8"))
        getDefault = Datasource.objects.filter(isDefault=True).first()

        if reqJson["isDefault"] and getDefault:
            if getDefault.id != pk:
                getDefault.isDefault = False
                getDefault.save()
        Datasource.objects.filter(id=pk).update(**reqJson)
        return Response({"code":200,"results":"success"})
    
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
    search_fields =  ('param_name', 'param_value',)
    def list(self, request, *args, **kwargs):
        if(request.query_params.get('params') == "gm"):
            secretKey = sysConfigParams.objects.get(param_name="secret_key").param_value
            keyMode = sysConfigParams.objects.get(param_name="secret_mode").param_value
            return Response({"key":secretKey,"mode":keyMode})
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
            sysConfigParams.objects.bulk_update(params_to_update,["param_value"])
            #触发配置文件加载
            sys_config = ConfigManager()
            #强制刷新
            sys_config.reload()
            logger.info(f"刷新redis<{params}>")
        except Exception as e:
            return Response(data=e)
        return Response(data='update success')