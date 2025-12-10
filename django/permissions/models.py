import uuid
from django.db import models
from django.conf import settings
from django.db.models import Q, CheckConstraint
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Menu(models.Model):
    class MenuTypeChoices(models.IntegerChoices):
        DIRETORY = '0', '目录'
        MENU = '1', '菜单'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    label = models.CharField(max_length=32, unique=True, verbose_name='菜单')
    icon = models.CharField(max_length=64, verbose_name='菜单图标', null=True, blank=True)
    name = models.CharField(max_length=32, unique=True, verbose_name='菜单编码', null=False)
    parentid = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE)
    status = models.BooleanField(verbose_name="状态", default=True)
    path = models.CharField(max_length=32, null=True, blank=True)
    is_menu = models.BooleanField(verbose_name="是否菜单", default=True)
    sort = models.IntegerField(null=True, blank=True, default=0)
    has_info = models.BooleanField(verbose_name="是否有详细页面", default=False)
    info_view_name = models.CharField(max_length=128, verbose_name='详细页面路由', null=True, blank=True)
    is_iframe = models.BooleanField(verbose_name="是否内嵌", default=False)
    keepalive = models.BooleanField(verbose_name="缓存", default=False)
    iframe_url = models.CharField(max_length=256, verbose_name='链接地址', null=True, blank=True)
    description = models.CharField(max_length=256, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "tb_menu"
        verbose_name = "菜单"
        verbose_name_plural = verbose_name
        app_label = 'mapi'


class Button(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=32, verbose_name='按钮名称', null=False)
    action = models.CharField(max_length=32, verbose_name='按钮动作', null=False)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name="buttons")

    class Meta:
        db_table = "tb_button"
        verbose_name = "菜单按钮"
        verbose_name_plural = verbose_name


class Permission(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="permission",
        null=True,
        blank=True)
    user_group = models.ForeignKey(
        settings.AUTH_USER_GROUP_MODEL,
        on_delete=models.CASCADE,
        related_name="permission",
        null=True,
        blank=True)
    role = models.ForeignKey(
        settings.AUTH_ROLE_MODEL,
        on_delete=models.CASCADE,
        related_name="permission",
        null=True,
        blank=True)
    menu = models.ForeignKey('mapi.Menu', on_delete=models.CASCADE, related_name="permission")
    button = models.ForeignKey('mapi.Button', on_delete=models.CASCADE, related_name="permission")

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

    class Meta:
        db_table = "tb_permission"
        verbose_name = "权限"
        verbose_name_plural = verbose_name


class DataScope(models.Model):
    class ScopeType(models.TextChoices):
        ALL = 'all', '全部数据'
        FILTER = 'filter', '按条件过滤'
        SELF = 'self', '仅自身创建'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='data_scopes'
    )
    user_group = models.ForeignKey(
        settings.AUTH_USER_GROUP_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='data_scopes'
    )
    role = models.ForeignKey(
        settings.AUTH_ROLE_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='data_scopes'
    )
    app_label = models.CharField(max_length=100, null=True, blank=True)
    scope_type = models.CharField(max_length=20, choices=ScopeType.choices, default=ScopeType.SELF)
    description = models.CharField(max_length=255, blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tb_data_scope'
        app_label = 'permissions'
        ordering = ['-create_time']
        constraints = [
            CheckConstraint(
                check=(
                    (Q(role__isnull=False) & Q(user_group__isnull=True) & Q(user__isnull=True)) |
                    (Q(role__isnull=True) & Q(user_group__isnull=False) & Q(user__isnull=True)) |
                    (Q(role__isnull=True) & Q(user_group__isnull=True) & Q(user__isnull=False))
                ),
                name='either_role_or_user_is_set'
            )
        ]


class PermissionTarget(models.Model):
    """
    权限目标：一个 DataScope 规则可以包含多个具体的目标。
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scope = models.ForeignKey(DataScope, on_delete=models.CASCADE, related_name='targets')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=36)
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        db_table = 'tb_permission_target'
        app_label = 'permissions'
        unique_together = ('scope', 'content_type', 'object_id')
