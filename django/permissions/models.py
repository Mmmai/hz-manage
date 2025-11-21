import uuid
from django.db import models
from django.db.models import Q, CheckConstraint
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class DataScope(models.Model):
    class ScopeType(models.TextChoices):
        ALL = 'all', '全部数据'
        FILTER = 'filter', '按条件过滤'
        SELF = 'self', '仅自身创建'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'mapi.UserInfo',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='data_scopes'
    )
    user_group = models.ForeignKey(
        'mapi.UserGroup',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='data_scopes'
    )
    role = models.ForeignKey(
        'mapi.Role',
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
