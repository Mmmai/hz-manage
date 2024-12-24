from django.db import models
from datetime import timezone

class UserInfo(models.Model):
    username = models.CharField(max_length=32,null=False,unique=True)
    password = models.CharField(max_length=32,null=False)
    real_name = models.CharField(max_length=50, verbose_name="真实姓名",null=True,blank=True,default="")
    # token = models.CharField(max_length=128,null=True,blank=True)
    status = models.BooleanField(verbose_name="状态",default=True)
    update_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)
    roles = models.ManyToManyField(to='Role',verbose_name='角色')

    def __str__(self):
      return self.username
    class Meta:
      db_table = "tb_userinfo"
      verbose_name = "用户表"
      verbose_name_plural = verbose_name
      app_label = 'mapi'

class Role(models.Model):
    """
    角色：绑定权限
    """
    role = models.CharField(max_length=32, unique=True,verbose_name = "角色")

    menu = models.ManyToManyField("Menu",blank=True,null=True)
    # 定义角色和权限的多对多关系

    def __str__(self):
        return self.role

    class Meta:
        db_table = "tb_role"
        verbose_name = "角色"
        verbose_name_plural = verbose_name
        app_label = 'mapi'


class Menu(models.Model):
    """
    菜单
    """
    label = models.CharField(max_length=32, unique=True,verbose_name='菜单')
    icon = models.CharField(max_length=64, verbose_name='菜单图标', null=True, blank=True)
    name = models.CharField(max_length=32, unique=True,verbose_name='菜单编码',null=False)
    # parentid = models.IntegerField(null=True, blank=True,verbose_name='父菜单ID')
    parentid = models.ForeignKey("Menu", null=True, blank=True, on_delete=models.CASCADE)
    status = models.BooleanField(verbose_name="状态",default=True)
    path = models.CharField(max_length=32,null=True, blank=True)
    is_menu = models.BooleanField(verbose_name="是否菜单",default=True)
    sort = models.IntegerField(null=True,blank=True,default=0)
    has_info = models.BooleanField(verbose_name="是否有详细页面",default=False)
    info_view_name = models.CharField(max_length=128,verbose_name='详细页面路由',null=True,blank=True)
    is_iframe = models.BooleanField(verbose_name="是否内嵌",default=False)
    iframe_url = models.CharField(max_length=256, verbose_name='链接地址',null=True,blank=True)
    description = models.CharField(max_length=256,null=True,blank=True)

    # 定义菜单间的自引用关系
    # 权限url 在 菜单下；菜单可以有父级菜单；还要支持用户创建菜单，因此需要定义parent字段（parent_id）
    # blank=True 意味着在后台管理中填写可以为空，根菜单没有父级菜单

    # def __str__(self):
    #     return self.menu_name

    class Meta:
        db_table = "tb_menu"
        verbose_name = "菜单"
        verbose_name_plural = verbose_name
        app_label = 'mapi'

# class Permission(models.Model):
#     """
#     权限
#     """
#     title = models.CharField(max_length=32, unique=True, verbose_name="权限")
#     url = models.CharField(max_length=128, unique=True)
#     icon = models.CharField(max_length=10, verbose_name='权限图标', null=True, blank=True)
#     menu = models.ForeignKey("Menu", null=True, blank=True, on_delete=models.CASCADE)
#
#     def __str__(self):
#         # 显示带菜单前缀的权限
#         return '{menu}---{permission}'.format(menu=self.menu, permission=self.title)
#
#     class Meta:
#         db_table = "tb_permission"
#         verbose_name = "权限"
#         verbose_name_plural = verbose_name
class Portal(models.Model):
    name = models.CharField(verbose_name='名称',max_length=32,null=False,unique=True)
    describe = models.CharField(verbose_name='描述',max_length=256,null=True,blank=True,default="")
    username = models.CharField(verbose_name='用户名',max_length=32,null=True,blank=True,default="")
    password = models.CharField(verbose_name='密码',max_length=32,null=True,blank=True,default="")
    url = models.CharField(max_length=256, verbose_name="链接地址",null=False,default="")
    # token = models.CharField(max_length=128,null=True,blank=True)

    status = models.BooleanField(verbose_name="状态",default=True)
    update_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)
    target = models.BooleanField(verbose_name="跳转方式",default=True)
    group = models.ForeignKey('Pgroup',on_delete=models.CASCADE,verbose_name="分组",db_column='group')
    # owner = models.ForeignKey('Userinfo',on_delete=models.CASCADE,db_column='owner')
    sort = models.IntegerField(null=True,blank=True,default=0,verbose_name="排序")


    class Meta:
        unique_together = (('name'),)
        db_table = "tb_portal"
        verbose_name = "门户表"
        verbose_name_plural = verbose_name
        app_label = 'mapi'

class Pgroup(models.Model):
    """
    门户的用户组
    """
    group = models.CharField(max_length=32, unique=True,verbose_name = "角色")
    # owner = models.ForeignKey('Userinfo',on_delete=models.CASCADE)
    # 定义角色和权限的多对多关系

    class Meta:
        # unique_together = (('group','owner'),)
        unique_together = (('group',),)
        db_table = "tb_pgroup"
        verbose_name = "门户分组"
        verbose_name_plural = verbose_name
        app_label = 'mapi'
class Datasource(models.Model):
    source_name = models.CharField(max_length=32, unique=True,verbose_name = "数据源名称")
    source_type = models.CharField(max_length=32,null=False,default="loki",verbose_name = "类型")
    username = models.CharField(verbose_name='用户名',max_length=32,null=True,blank=True,default="")
    password = models.CharField(verbose_name='密码',max_length=32,null=True,blank=True,default="")
    url = models.CharField(max_length=256, verbose_name="api地址",null=False,default="")
    # token = models.CharField(max_length=128,null=True,blank=True)
    isUsed = models.BooleanField(verbose_name="是否启用",default=True)
    state = models.BooleanField(verbose_name="接口状态",default=True)
    update_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)
    isAuth = models.BooleanField(verbose_name="是否开启认证",default=False)
    isDefault = models.BooleanField(verbose_name="默认",default=True)
    class Meta:
        db_table = "tb_datasource"
        verbose_name = "数据源"
        app_label = 'mapi'
# class LogModule(models.Model):
#     module_name = models.CharField(max_length=32, unique=True,verbose_name = "模块名称")
#     label_name = models.CharField(max_length=32,null=False,default="",verbose_name = "标签")
#     label_value = models.CharField(max_length=256,null=False,default="",verbose_name = "标签值")
#     label_match = models.CharField(max_length=32,null=False,default="",verbose_name = "匹配方式")
#     group = models.CharField(max_length=64, verbose_name="分组",null=True,blank=True)
#     # token = models.CharField(max_length=128,null=True,blank=True)
#     state = models.BooleanField(verbose_name="接口状态",default=True)
#     update_time = models.DateTimeField(auto_now=True)
#     create_time = models.DateTimeField(auto_now_add=True)
#     class Meta:
#         db_table = "tb_log_module"
#         verbose_name = "数据源"


# class orderMethod(models.Model):
#     owner = models.CharField(unique=True,verbose_name = "所属功能")
#     # group = models.ForeignKey('Pgroup',on_delete=models.CASCADE,verbose_name="分组",db_column='group')
#     # owner = models.ForeignKey('Userinfo',on_delete=models.CASCADE,db_column='owner')
#     orderList = models.JSONField()



#     class Meta:
#         # unique_together = (('name'),)
#         db_table = "tb_order_method"
#         verbose_name = "排序表"
#         # verbose_name_plural = verbose_name



class sysConfigParams(models.Model):
    """
    角色：绑定权限
    """
    param_name = models.CharField(max_length=256, unique=True,verbose_name = "参数名")
    param_value = models.CharField(max_length=256,null=True,blank=True,verbose_name = "参数值")
    # 定义角色和权限的多对多关系

    class Meta:
        db_table = "tb_sysconfig"
        verbose_name = "系统参数配置表"
        verbose_name_plural = verbose_name
        app_label = 'mapi'
