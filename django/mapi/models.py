from django.db import models
from django.utils import timezone
import uuid


class UserInfo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=32, null=False, unique=True)
    password = models.CharField(max_length=256, null=False)
    password_salt = models.CharField(max_length=32, null=False, default='')
    real_name = models.CharField(max_length=50, verbose_name="真实姓名", null=True, blank=True, default="")
    # token = models.CharField(max_length=128,null=True,blank=True)
    status = models.BooleanField(verbose_name="状态", default=True)
    built_in = models.BooleanField(verbose_name="内置用户", default=False)
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
    group_name = models.CharField(max_length=32, null=False, unique=True)
    built_in = models.BooleanField(verbose_name="内置用户组", default=False)
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
    role = models.CharField(max_length=32, unique=True, verbose_name="角色")
    role_name = models.CharField(max_length=32, unique=True, verbose_name="角色名称")
    built_in = models.BooleanField(verbose_name="内置角色", default=False)
    update_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.role

    class Meta:
        db_table = "tb_role"
        verbose_name = "角色"
        verbose_name_plural = verbose_name
        app_label = 'mapi'


class Portal(models.Model):
    """
    门户
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(verbose_name='名称', max_length=32, null=False)
    url = models.CharField(max_length=256, verbose_name="链接地址", null=False, default="")
    status = models.BooleanField(verbose_name="状态", default=True)
    username = models.CharField(verbose_name='用户名', max_length=32, null=True, blank=True, default="")
    password = models.CharField(verbose_name='密码', max_length=32, null=True, blank=True, default="")
    target = models.BooleanField(verbose_name="跳转方式", default=True)
    describe = models.CharField(verbose_name='描述', max_length=256, null=True, blank=True, default="")

    # 添加排序字段
    sort_order = models.IntegerField(verbose_name="排序", default=0)

    # 添加共享类型字段
    SHARING_CHOICES = [
        ('private', '私人'),
        ('public', '公共'),
    ]
    sharing_type = models.CharField(verbose_name='共享类型', max_length=10, choices=SHARING_CHOICES, default='public')

    # 所有门户都有创建者，公共门户对所有用户可见
    owner = models.ForeignKey('Userinfo', on_delete=models.CASCADE, verbose_name="创建者")

    # 门户可以属于多个分组（多对多关系）
    groups = models.ManyToManyField('Pgroup', verbose_name="分组", related_name='portals', blank=True)

    update_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        # 私有门户在用户内唯一，公共门户全局唯一
        unique_together = (('name', 'sharing_type', 'owner'), ('name', 'sharing_type'))
        constraints = [
            models.UniqueConstraint(
                fields=['name'],
                condition=models.Q(sharing_type='public'),
                name='unique_public_portal_name'
            ),
            models.UniqueConstraint(
                fields=['name', 'owner'],
                condition=models.Q(sharing_type='private'),
                name='unique_private_portal_name_per_user'
            )
        ]
        db_table = "tb_portal"
        verbose_name = "门户表"
        verbose_name_plural = verbose_name
        app_label = 'mapi'


class Pgroup(models.Model):
    """ 
    门户分组
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.CharField(verbose_name='分组名称', max_length=32, null=False)

    # 添加共享类型字段
    SHARING_CHOICES = [
        ('private', '私人'),
        ('public', '公共'),
    ]
    sharing_type = models.CharField(verbose_name='共享类型', max_length=10, choices=SHARING_CHOICES, default='public')

    # 所有分组都有创建者，公共分组对所有用户可见
    owner = models.ForeignKey('Userinfo', on_delete=models.CASCADE, verbose_name="创建者")

    # 添加排序字段
    sort_order = models.IntegerField(verbose_name="排序", default=0)
    update_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        # 私有分组在用户内唯一，公共分组全局唯一
        unique_together = (('group', 'sharing_type', 'owner'), ('group', 'sharing_type'))
        constraints = [
            models.UniqueConstraint(
                fields=['group'],
                condition=models.Q(sharing_type='public'),
                name='unique_public_group_name'
            ),
            models.UniqueConstraint(
                fields=['group', 'owner'],
                condition=models.Q(sharing_type='private'),
                name='unique_private_group_name_per_user'
            )
        ]
        db_table = "tb_pgroup"
        verbose_name = "门户分组表"
        verbose_name_plural = verbose_name
        app_label = 'mapi'


class UserPgroupSortOrder(models.Model):
    """
    用户分组排序偏好设置
    每个用户可以独立设置自己看到的分组排序
    """
    user = models.ForeignKey('Userinfo', on_delete=models.CASCADE, verbose_name="用户")
    pgroup = models.ForeignKey('Pgroup', on_delete=models.CASCADE, verbose_name="门户分组")
    sort_order = models.IntegerField(verbose_name="排序", default=0)

    # 可以添加创建和更新时间
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'pgroup')
        db_table = "tb_user_pgroup_sort"
        verbose_name = "用户门户分组排序"
        verbose_name_plural = verbose_name
        app_label = 'mapi'


class UserPortalSortOrder(models.Model):
    """
    用户门户排序偏好设置
    每个用户可以独立设置自己看到的门户排序
    """
    user = models.ForeignKey('Userinfo', on_delete=models.CASCADE, verbose_name="用户")
    portal = models.ForeignKey('Portal', on_delete=models.CASCADE, verbose_name="门户")
    sort_order = models.IntegerField(verbose_name="排序", default=0)

    # 可以按分组保存排序
    group = models.ForeignKey('Pgroup', on_delete=models.CASCADE, verbose_name="门户分组", null=True, blank=True)

    # 可以添加创建和更新时间
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'portal')
        db_table = "tb_user_portal_sort"
        verbose_name = "用户门户排序"
        verbose_name_plural = verbose_name
        app_label = 'mapi'


class PortalFavorites(models.Model):
    """
    门户收藏夹
    用户可以收藏自己喜欢的门户
    """
    user = models.ForeignKey('Userinfo', on_delete=models.CASCADE, verbose_name="用户")
    portal = models.ForeignKey('Portal', on_delete=models.CASCADE, verbose_name="门户")

    # 收藏时间
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'portal')  # 确保用户不能重复收藏同一个门户
        db_table = "tb_portal_favorites"
        verbose_name = "门户收藏"
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
