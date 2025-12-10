import re
import logging
from django.db.models.signals import post_save, post_delete,m2m_changed
from django.dispatch import receiver
from .models import UserInfo, UserGroup, Role, Menu, sysConfigParams, Button, Permission
from .messages import zabbix_config_updated
from node_mg.utils.config_manager import ConfigManager
from permissions.tools import clear_data_scope_cache,clear_password_permission_cache

logger = logging.getLogger(__name__)
@receiver(post_save, sender=Role)
def auto_add_home_to_role(sender, instance, created, **kwargs):
    if created:
        if instance.role == "sysadmin":
            return
        # 当 MyModel 的实例被创建时执行此代码
        # print(f"New instance of MyModel created: {instance}")
        menu_obj = Menu.objects.get(name="home")
        buttonObj = Button.objects.get(menu=menu_obj,action="view")
        Permission.objects.create(menu=menu_obj, role=instance,button=buttonObj)
        logger.info(f"将<{menu_obj.label}>授予角色<{instance.role}>权限!")
@receiver(post_save, sender=Menu)
def atuo_create_default_botton(sender, instance, created, **kwargs):
    if created:
        # 当 MyModel 的实例被创建时执行此代码
        # print(f"New instance of MyModel created: {instance}")
        if not instance.is_menu:
            return
        if instance.is_iframe:
            # 单独添加菜单权限
            # return
            buttons = [Button(name='查看', action='view', menu=instance),]
        # role_obj = Role.objects.get(role="sysadmin")
        # 定义需要添加的按钮
        else:
            buttons = [
                Button(name='查看', action='view', menu=instance),
                Button(name='添加', action='add', menu=instance),
                Button(name='删除', action='delete', menu=instance),
                Button(name='修改', action='edit', menu=instance)
            ]
        for button in buttons:
            button.save()
            # Permission.objects.create(menu=instance, button=button,role=role_obj)
            logger.info(f"创建按钮<{instance.label}:{button.name}>!")


@receiver(post_save, sender=Button)
def atuo_add_to_sysadmin(sender, instance, created, **kwargs):
    if created:
        # 当 MyModel 的实例被创建时执行此代码
        # print(f"New instance of MyModel created: {instance}")
        role_obj = Role.objects.get(role="sysadmin")
        Permission.objects.create(menu=instance.menu, button=instance, role=role_obj)
        logger.info(f"将<{instance.menu.label}:{instance.name}>授予管理员权限!")
@receiver(post_save, sender=sysConfigParams)
def monitor_sys_config_change(sender, instance, created, **kwargs):
    # zabbix配置发生变化时通知node_mg立即刷新配置
    if re.match("^zabbix", instance.param_name):
        zabbix_config_updated.send()
        logger.debug(f'Zabbix configuration parameter "{instance.param_name}" has changed, sent update signal.')

def clear_user_cache_for_m2m_change(sender, instance, action, reverse, model, pk_set, **kwargs):
    """
    当用户、用户组、角色之间的多对多关系发生变化时，
    清除相关用户的权限缓存
    """
    # 只处理添加、删除和清空操作
    if action not in ["post_add", "post_remove", "post_clear"]:
        return

    # 如果是反向关系，我们需要找到正向的对象
    if reverse:
        # instance 是关系中的另一端对象
        # 需要找出与之关联的 UserInfo/UserGroup 实例
        if isinstance(instance, UserInfo):
            # 直接就是用户对象
            affected_users = [instance]
        elif isinstance(instance, (UserGroup, Role)):
            # 需要找出所有关联的用户
            if isinstance(instance, UserGroup):
                affected_users = list(instance.users.all())
            else:
                # Role 对象，找出所有关联的用户
                # 1. 直接关联角色的用户
                direct_users = list(instance.userinfo_set.all())
                # 2. 通过用户组关联角色的用户
                group_users = list(UserInfo.objects.filter(groups__roles=instance))
                # 合并并去重
                affected_users = list(set(direct_users + group_users))
        else:
            return
    else:
        # 正向关系，instance 是包含多对多字段的对象
        if isinstance(instance, UserInfo):
            # 用户关联了用户组或角色
            affected_users = [instance]
        elif isinstance(instance, UserGroup):
            # 用户组关联了角色，需要更新用户组中的所有用户
            affected_users = list(instance.users.all())
        else:
            return

    # 清除受影响用户的数据范围缓存
    for user in affected_users:
        try:
            clear_data_scope_cache(user.username)
            clear_password_permission_cache(user.username)
            logger.info(f"Cleared data scope cache for user: {user.username}")
        except Exception as e:
            logger.error(f"Failed to clear data scope cache for user {user.username}: {e}")


# 注册信号处理器监听 UserInfo 的多对多字段变化
m2m_changed.connect(
    clear_user_cache_for_m2m_change,
    sender=UserInfo.roles.through
)

m2m_changed.connect(
    clear_user_cache_for_m2m_change,
    sender=UserInfo.groups.through
)

# 注册信号处理器监听 UserGroup 的多对多字段变化
m2m_changed.connect(
    clear_user_cache_for_m2m_change,
    sender=UserGroup.roles.through
)

def clear_cache_on_permission_change(sender, instance, created=None, **kwargs):
    """
    当权限发生变化时，清除相关用户的密码权限缓存
    特别关注showPassword权限的变更
    """
    # 收集可能受此权限变更影响的所有用户
    affected_users = set()
    
    # 如果是新创建的权限且与showPassword相关，则需要清除所有用户的缓存
    # 因为我们无法预测谁可能会获得这个权限
    if created and instance.button and instance.button.action == 'showPassword':
        # 新增了showPassword权限，清除所有用户的密码权限缓存
        all_users = UserInfo.objects.all()
        for user in all_users:
            try:
                clear_password_permission_cache(user.username)
                logger.info(f"Cleared password permission cache for user: {user.username} due to new showPassword permission")
            except Exception as e:
                logger.error(f"Failed to clear password permission cache for user {user.username}: {e}")
        return
    
    # 确定权限变更影响的具体用户
    if instance.user:
        # 直接关联到用户的权限
        affected_users.add(instance.user.username)
    elif instance.role_id:
        # 关联到角色的权限，影响所有拥有该角色的用户
        try:
            # 尝试获取角色对象
            role = instance.role
            # 直接关联该角色的用户
            direct_users = role.userinfo_set.all()
            # 通过用户组关联该角色的用户
            group_users = UserInfo.objects.filter(groups__roles=role)
            for user in (direct_users | group_users).distinct():
                affected_users.add(user.username)
        except Role.DoesNotExist:
            # 角色已被删除，不需要处理
            logger.info("Role has been deleted, skipping cache clearance")
            return
    elif instance.user_group:
        # 关联到用户组的权限，影响该组的所有用户
        try:
            users_in_group = instance.user_group.users.all()
            for user in users_in_group:
                affected_users.add(user.username)
        except UserGroup.DoesNotExist:
            # 用户组已被删除，不需要处理
            logger.info("UserGroup has been deleted, skipping cache clearance")
            return
    
    # 清除受影响用户的密码权限缓存
    for username in affected_users:
        try:
            clear_password_permission_cache(username)
            logger.info(f"Cleared password permission cache for user: {username} due to permission change")
        except Exception as e:
            logger.error(f"Failed to clear password permission cache for user {username}: {e}")
# 注册信号处理器监听 Permission 模型变化
post_save.connect(clear_cache_on_permission_change, sender=Permission)
post_delete.connect(clear_cache_on_permission_change, sender=Permission)