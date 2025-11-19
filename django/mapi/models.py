from django.db import models
from django.utils import timezone
import uuid


class UserInfo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=32,null=False,unique=True)
    password = models.CharField(max_length=256,null=False)
    password_salt = models.CharField(max_length=32, null=False, default='')    
    real_name = models.CharField(max_length=50, verbose_name="真实姓名",null=True,blank=True,default="")
    # token = models.CharField(max_length=128,null=True,blank=True)
    status = models.BooleanField(verbose_name="状态",default=True)
    built_in = models.BooleanField(verbose_name="内置用户",default=False)
    expire_time = models.DateTimeField(verbose_name="到期时间", null=True, blank=True)
    update_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)
    roles = models.ManyToManyField(to='Role', verbose_name='角色')
    groups = models.ManyToManyField(to='UserGroup', verbose_name='用户组', related_name="users")

    def __str__(self):
      return self.username
    def is_expired(self):
        """
        检查用户是否已过期
        如果没有设置过期时间，则返回False
        否则比较当前时间和过期时间
        """
        if not self.expire_time:
            return False
        return timezone.now() > self.expire_time
    class Meta:
        db_table = "tb_userinfo"
        verbose_name = "用户表"
        verbose_name_plural = verbose_name
        app_label = 'mapi'


class UserGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group_name = models.CharField(max_length=32,null=False,unique=True)
    built_in = models.BooleanField(verbose_name="内置用户组",default=False)
    update_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)
    roles = models.ManyToManyField(to='Role', verbose_name='角色')

    def __str__(self):
        return self.group_name

    class Meta:
        db_table = "tb_user_group"
        verbose_name = "用户组表"
        verbose_name_plural = verbose_name
        app_label = 'mapi'


class Role(models.Model):
    """
    角色：绑定权限
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=32, unique=True,verbose_name = "角色")
    role_name = models.CharField(max_length=32, unique=True,verbose_name = "角色名称")
    built_in = models.BooleanField(verbose_name="内置角色",default=False)
    update_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)

    # menu = models.ManyToManyField("Menu")
    # 定义角色和权限的多对多关系

    def __str__(self):
        return self.role

    class Meta:
        db_table = "tb_role"
        verbose_name = "角色"
        verbose_name_plural = verbose_name
        app_label = 'mapi'


class Menu(models.Model):
    class MenuTypeChoices(models.IntegerChoices):
        DIRETORY = '0', '目录'
        MENU = '1', '菜单'
        # BUTTON = '2', '按钮'
    """
    菜单
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    label = models.CharField(max_length=32, unique=True, verbose_name='菜单')
    icon = models.CharField(max_length=64, verbose_name='菜单图标', null=True, blank=True)
    name = models.CharField(max_length=32, unique=True, verbose_name='菜单编码', null=False)
    # parentid = models.IntegerField(null=True, blank=True,verbose_name='父菜单ID')
    parentid = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE)
    status = models.BooleanField(verbose_name="状态", default=True)
    path = models.CharField(max_length=32, null=True, blank=True)
    is_menu = models.BooleanField(verbose_name="是否菜单", default=True)
    # menu_type = models.IntegerField(choices=MenuTypeChoices.choices,default=MenuTypeChoices.MENU)
    sort = models.IntegerField(null=True, blank=True, default=0)
    has_info = models.BooleanField(verbose_name="是否有详细页面", default=False)
    info_view_name = models.CharField(max_length=128, verbose_name='详细页面路由', null=True, blank=True)
    is_iframe = models.BooleanField(verbose_name="是否内嵌", default=False)
    keepalive = models.BooleanField(verbose_name="缓存", default=False)
    iframe_url = models.CharField(max_length=256, verbose_name='链接地址', null=True, blank=True)
    description = models.CharField(max_length=256, null=True, blank=True)
    # role = models.ManyToManyField("Role")

    # 定义菜单间的自引用关系
    # 权限url 在 菜单下；菜单可以有父级菜单；还要支持用户创建菜单，因此需要定义parent字段（parent_id）
    # blank=True 意味着在后台管理中填写可以为空，根菜单没有父级菜单

    def __str__(self):
        return self.name

    class Meta:
        db_table = "tb_menu"
        verbose_name = "菜单"
        verbose_name_plural = verbose_name
        app_label = 'mapi'


# class RoleAndMenu(models.Model):
#     menus = models.ForeignKey("Menu",on_delete=models.CASCADE)
#     roles = models.ForeignKey("Role",on_delete=models.CASCADE)

#     class Meta:
#         db_table = "tb_role_menu"
#         app_label = 'mapi'
# 按钮


class Button(models.Model):
    """
    权限
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=32, verbose_name='按钮名称', null=False)
    action = models.CharField(max_length=32, verbose_name='按钮动作', null=False)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name="buttons")

    # def __str__(self):
    #     # 显示带菜单前缀的权限
    #     return

    class Meta:
        db_table = "tb_button"
        verbose_name = "菜单按钮"
        verbose_name_plural = verbose_name


class Permission(models.Model):
    """
    权限
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="permission", null=True, blank=True)
    user = models.ForeignKey(UserInfo, on_delete=models.CASCADE, related_name="permission", null=True, blank=True)
    user_group = models.ForeignKey(UserGroup, on_delete=models.CASCADE, related_name="permission", null=True, blank=True)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name="permission")
    button = models.ForeignKey(Button, on_delete=models.CASCADE, related_name="permission")

    def __str__(self):
        if self.role:
            owner = self.role.role
        elif self.user:
            owner = self.user.username
        elif self.user_group:
            owner = self.user_group.group_name
        else:
            owner = "Unknown"
        return f"{owner} - {self.menu.name} - {self.button.name}"

    @classmethod
    def get_user_permissions(cls, user):
        """
        获取用户的所有权限，包括通过角色、用户组和直接授权的权限
        """
        # 通过用户直接角色获取权限
        role_permissions = cls.objects.filter(role__in=user.roles.all())
        
        # 通过用户组获取权限（包括用户组关联的角色权限）
        user_groups = user.groups.all()
        user_group_permissions = cls.objects.filter(user_group__in=user_groups)
        
        # 通过用户组关联的角色获取权限
        group_roles = []
        for group in user_groups:
            group_roles.extend(group.roles.all())
        group_role_permissions = cls.objects.filter(role__in=group_roles)
        
        # 通过直接用户授权获取权限
        user_permissions = cls.objects.filter(user=user)
        
        # 合并所有权限并去重
        permissions = (role_permissions | user_group_permissions | group_role_permissions | user_permissions).distinct()
        return permissions

    class Meta:
        db_table = "tb_permission"
        verbose_name = "权限"
        verbose_name_plural = verbose_name


class Portal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(verbose_name='名称', max_length=32, null=False, unique=True)
    url = models.CharField(max_length=256, verbose_name="链接地址", null=False, default="")
    # token = models.CharField(max_length=128,null=True,blank=True)
    status = models.BooleanField(verbose_name="状态", default=True)
    username = models.CharField(verbose_name='用户名', max_length=32, null=True, blank=True, default="")
    password = models.CharField(verbose_name='密码', max_length=32, null=True, blank=True, default="")
    target = models.BooleanField(verbose_name="跳转方式", default=True)
    group = models.ForeignKey('Pgroup', on_delete=models.CASCADE, verbose_name="分组", db_column='group')
    # owner = models.ForeignKey('Userinfo',on_delete=models.CASCADE,db_column='owner')
    describe = models.CharField(verbose_name='描述', max_length=256, null=True, blank=True, default="")
    sort = models.IntegerField(blank=True, null=True, db_index=True)
    update_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)

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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.CharField(max_length=32, unique=True, verbose_name="角色")
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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_name = models.CharField(max_length=32, unique=True, verbose_name="数据源名称")
    source_type = models.CharField(max_length=32, null=False, default="loki", verbose_name="类型")
    username = models.CharField(verbose_name='用户名', max_length=32, null=True, blank=True, default="")
    password = models.CharField(verbose_name='密码', max_length=32, null=True, blank=True, default="")
    url = models.CharField(max_length=256, verbose_name="api地址", null=False, default="")
    # token = models.CharField(max_length=128,null=True,blank=True)
    isUsed = models.BooleanField(verbose_name="是否启用", default=True)
    state = models.BooleanField(verbose_name="接口状态", default=True)
    update_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)
    isAuth = models.BooleanField(verbose_name="是否开启认证", default=False)
    isDefault = models.BooleanField(verbose_name="默认", default=True)

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
    class TypeChoices(models.TextChoices):
        STRING = 'string', '字符串'
        INTER = 'int', '整数'
        FLOAT = 'float', '小数'
        # JSON = 'fr', 'French'
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    verbose_name = models.CharField(max_length=254, null=True, blank=True, verbose_name="参数名称")
    # 配置所属系统s 参数
    system = models.CharField(max_length=254, default="common", verbose_name="系统")
    param_name = models.CharField(max_length=254, unique=True, verbose_name="参数代码")
    param_value = models.CharField(max_length=254, null=True, blank=True, verbose_name="参数值")
    param_type = models.CharField(max_length=50, choices=TypeChoices.choices, default=TypeChoices.STRING)
    description = models.TextField(blank=True, null=True, verbose_name="参数说明")

    class Meta:
        db_table = "tb_sysconfig"
        verbose_name = "系统参数配置表"
        # verbose_name_plural = verbose_name
        app_label = 'mapi'
