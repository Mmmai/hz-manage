from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from rest_framework import filters,status
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from .sers import *
from rest_framework.views import APIView
from rest_framework.response import Response
# from .models import UserInfo,Role,Menu,Portal,Pgroup,Datasource,LogModule
from .models import (
  UserInfo,UserGroup,Role,Menu,Portal,Pgroup,Datasource,
  sysConfigParams
  )
from .filters import (
    roleFilter,
    sysConfigParamsFilter   
)
from .utils.jwt_create_token import create_token
from rest_framework.pagination import PageNumberPagination
from .extensions.jwt_authenticate import JWTQueryParamsAuthentication
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
import json
from django.conf import settings
from mapi.extensions.pagination import StandardResultsSetPagination
class LoginView(APIView):
    """用户登录"""
    authentication_classes = [] # 取消全局认证

    def post(self,request,*args,**kwargs):
        user = request.data.get('username')
        pwd = request.data.get('password')
        user_obj = UserInfo.objects.filter(username=user,password=pwd).first()
        if not user_obj:
            return Response({'code':401,'error':'用户名或密码错误'})
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
        #print(roleList)
        payload = {
            'user_id':str(user_obj.pk),#自定义用户ID
            'username':user_obj.username,#自定义用户名
            # 'exp':datetime.datetime.utcnow()+datetime.timedelta(minutes=1),# 设置超时时间，1min
        }
        jwt_token = create_token(payload=payload)
        return Response({'code':200,'token':jwt_token,"role":roleList,"userinfo":payload})




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

class sysConfig(APIView):
    def get(self,request,*args,**kwargs):
        # owner = request.query_params.get('owner')
        # orderRes =  orderMethod.objects.filter(owner=owner).first()
        import gmssl.func as gmssl_func
        from gmssl import sm4
        import binascii

        key = "Xmd4AlROeXgPv8JDkdgYptWvY4ntVBlC"
        data = "test"
        sm4_crypt = sm4.CryptSM4() # 创建SM4加密对象
        # sm4_crypt.set_key(key.encode("utf8"), sm4.SM4_ENCRYPT) # 设置密钥
        # ciphertext = sm4_crypt.crypt_ecb(gmssl_func.bytes_to_list(data.encode("utf8")))# 加密数据
        # encrypted_data = gmssl_func.list_to_bytes(ciphertext)
        # print(type(ciphertext))
        # print(type(encrypted_data))
        # print(f"加密后的数据: {encrypted_data}")
        aaa = "745bcdcc51e0c7a13b63b4dd86b632c4"
        sm4_crypt = sm4.CryptSM4()
        sm4_crypt.set_key(key.encode("utf8"), mode=sm4.SM4_DECRYPT)
        print(binascii.unhexlify(aaa))
        cipher_bytes = binascii.unhexlify(aaa)
        padded_text = sm4_crypt.crypt_ecb(cipher_bytes)
        print(padded_text)
        padding = padded_text[-1]
        plain_text = padded_text[:-padding]
        print(type(plain_text))
        print(f"解密后的数据: {plain_text.decode('utf-8')}")
        
        return JsonResponse({"1":3})

# def user(request):
class getMenu(APIView):
    def __init__(self):
        self.get_menu_tree = self.get_menu_tree
    def get(self,request,*args,**kwargs):
        # print(request.query_params)
        # print(request.GET.getlist('role'))
        # role = request.GET.getlist('role')
        role = request.query_params.get('role')
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

            roleList = []
            for r in menu.role_set.all().values():
                roleList.append(r["id"])
            info = menu.__dict__.copy()
            info.pop('_state')
            info["meta"] = {"role":roleList,"icon":menu.icon,"title":menu.label}
            if info["is_iframe"]:
                info["meta"]["iframePath"] = info["iframe_url"]
                info["meta"]["is_iframe"] = info["is_iframe"]

            info['children'] = self.get_menu_tree(menu_list,role,menu)
            # print(info)

            if role != None:
                # currentRoleList = [ i for i in role.split(',')]
                nlist = list(set(role).inter_section(set(roleList)))
                if len(nlist) == 0:
                    if menu.is_menu == True:
                        continue
                if menu.is_menu == False and len(info['children']) == 0:
                    continue
            tree.append(info)
        return tree



#   # data = {'1':2,'3':4}
#   return JsonResponse(data)

# class UserViewSet(ModelViewSet):
#   queryset = userlist.objects.all()
#   serializer_class = UserModelSerializer

#分页类
# class defaultPageNumberPagination(PageNumberPagination):
#     pige_size = 10
#     max_page_size = 50
#     page_size_query_param = 'size'

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


    # 批量删除
    @action(methods=['delete'], detail=False)
    def multiple_delete(self, request, *args, **kwargs):
        # pks = request.query_params.get('pks', None)
        pks = request.data.get('pks',None)
        if not pks:
            return Response(status=status.HTTP_404_NOT_FOUND)
        for pk in pks:
            get_object_or_404(UserInfo, id=int(pk)).delete()

        return Response(data='delete success',status=status.HTTP_204_NO_CONTENT)
class UserGroupViewSet(ModelViewSet):
    queryset = UserGroup.objects.all()
    serializer_class =  UserGroupModelSerializer
    # pagination_class = StandardResultsSetPagination
    # filterset_class = roleFilter
    order_fields = ["id"]

class RoleViewSet(ModelViewSet):
    queryset = Role.objects.all()
    serializer_class =  RoleModelSerializer
    # pagination_class = StandardResultsSetPagination
    filterset_class = roleFilter
    order_fields = ["id"]


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
