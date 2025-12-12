import logging
from django.db.models.signals import post_migrate, post_save,post_delete
from django.dispatch import receiver
from mapi.public_services import PublicRoleService,PublicUserService,PublicRbcaService
from .models import Menu, Button, Permission
from .init_data import INIT_MENU
from .tools import clear_password_permission_cache
logger = logging.getLogger(__name__)


# def _init_menus(self, Menu, Button):
#         """初始化菜单"""
#         # 检查是否已存在菜单，如果有超过80%的菜单则认为已初始化
#         existing_menus_count = Menu.objects.count()
#         total_menus_count = len(INIT_MENU)
        
#         if existing_menus_count >= total_menus_count * 0.8 and existing_menus_count > 0:
#             logger.info("菜单数据已存在，跳过菜单初始化")
#             return
            
#         menuInitList = INIT_MENU
#         # 创建目录
#         for i in menuInitList:
#             buttons = i.pop("buttons", None)
#             current_menu_data = i.copy()  # 复制一份避免修改原数据
            
#             if current_menu_data['parentid_id'] == '':
#                 current_menu_data['parentid_id'] = None
#                 instance, created = Menu.objects.get_or_create(
#                     name=current_menu_data['name'],
#                     defaults=current_menu_data
#                 )
#                 if created:
#                     logger.info(f"创建新菜单目录: {instance.label}")
#                 else:
#                     logger.debug(f"菜单目录已存在: {instance.label}")
#             else:
#                 parent_name = current_menu_data['parentid_id']
#                 try:
#                     parent_menu = Menu.objects.get(name=parent_name)
#                     current_menu_data['parentid_id'] = parent_menu.id
#                     instance, created = Menu.objects.get_or_create(
#                         name=current_menu_data['name'],
#                         defaults=current_menu_data
#                     )
#                     if created:
#                         logger.info(f"创建新菜单: {instance.label}")
                        
#                         # 添加按钮
#                         if buttons:
#                             for button in buttons:
#                                 button_instance, button_created = Button.objects.get_or_create(
#                                     name=button["name"],
#                                     action=button["action"],
#                                     menu=instance
#                                 )
#                                 if button_created:
#                                     logger.info(f"为菜单<{instance.label}>添加<{button_instance.name}>按钮")
#                     else:
#                         logger.debug(f"菜单已存在: {instance.label}")
                        
#                         # 检查并添加缺失的按钮
#                         if buttons:
#                             for button in buttons:
#                                 button_instance, button_created = Button.objects.get_or_create(
#                                     name=button["name"],
#                                     action=button["action"],
#                                     menu=instance
#                                 )
#                                 if button_created:
#                                     logger.info(f"为菜单<{instance.label}>添加缺失的<{button_instance.name}>按钮")
#                 except Menu.DoesNotExist:
#                     logger.warning(f"父级菜单 {parent_name} 不存在，无法创建子菜单 {current_menu_data.get('label', '')}")
                    
#         logger.info("菜单初始化完成")

@receiver(post_migrate)
def init_menu(sender, **kwargs):
    if sender.name != 'permissions':
        return

    """初始化菜单"""
    # 检查是否已存在菜单，如果有超过80%的菜单则认为已初始化
    existing_menus_count = Menu.objects.count()
    total_menus_count = len(INIT_MENU)
    
    if existing_menus_count >= total_menus_count * 0.8 and existing_menus_count > 0:
        logger.info("菜单数据已存在，跳过菜单初始化")
        return
        
    menuInitList = INIT_MENU
    # 创建目录
    for i in menuInitList:
        buttons = i.pop("buttons", None)
        current_menu_data = i.copy()  # 复制一份避免修改原数据
        
        if current_menu_data['parentid_id'] == '':
            current_menu_data['parentid_id'] = None
            instance, created = Menu.objects.get_or_create(
                name=current_menu_data['name'],
                defaults=current_menu_data
            )
            if created:
                logger.info(f"创建新菜单目录: {instance.label}")
            else:
                logger.debug(f"菜单目录已存在: {instance.label}")
        else:
            parent_name = current_menu_data['parentid_id']
            try:
                parent_menu = Menu.objects.get(name=parent_name)
                current_menu_data['parentid_id'] = parent_menu.id
                instance, created = Menu.objects.get_or_create(
                    name=current_menu_data['name'],
                    defaults=current_menu_data
                )
                if created:
                    logger.info(f"创建新菜单: {instance.label}")
                    
                    # 添加按钮
                    if buttons:
                        for button in buttons:
                            button_instance, button_created = Button.objects.get_or_create(
                                name=button["name"],
                                action=button["action"],
                                menu=instance
                            )
                            if button_created:
                                logger.info(f"为菜单<{instance.label}>添加<{button_instance.name}>按钮")
                else:
                    logger.debug(f"菜单已存在: {instance.label}")
                    
                    # 检查并添加缺失的按钮
                    if buttons:
                        for button in buttons:
                            button_instance, button_created = Button.objects.get_or_create(
                                name=button["name"],
                                action=button["action"],
                                menu=instance
                            )
                            if button_created:
                                logger.info(f"为菜单<{instance.label}>添加缺失的<{button_instance.name}>按钮")
            except Menu.DoesNotExist:
                logger.warning(f"父级菜单 {parent_name} 不存在，无法创建子菜单 {current_menu_data.get('label', '')}")
                
    logger.info("菜单初始化完成")


@receiver(post_save, sender=Menu)
def auto_create_default_button(sender, instance, created, **kwargs):
    if created:
        if not instance.is_menu:
            return

        if instance.is_iframe:
            buttons = [Button(name='查看', action='view', menu=instance),]
        else:
            buttons = [
                Button(name='查看', action='view', menu=instance),
                Button(name='添加', action='add', menu=instance),
                Button(name='删除', action='delete', menu=instance),
                Button(name='修改', action='edit', menu=instance)
            ]
        for button in buttons:
            button.save()
            logger.info(
                f"Automatically created default button <{button.name}:{button.action}> for menu <{instance.label}>.")


@receiver(post_save, sender=Button)
def auto_add_to_sysadmin(sender, instance, created, **kwargs):
    if created:
        role_obj = PublicRoleService.get_sysadmin()
        Permission.objects.create(menu=instance.menu, button=instance, role=role_obj)
        logger.info(f"Automatically granted <{instance.menu.label}:{instance.name}> permission to sysadmin role.")

@receiver([post_save, post_delete], sender=Permission)
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
        all_users = PublicUserService.get_users()
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
            all_users = PublicRbcaService.get_role_users(role.id)
            # PublicRbcaService.get_role_users返回None表示角色不存在
            if all_users is None:
                # 角色已被删除，不需要处理
                logger.info("Role has been deleted, skipping cache clearance")
                return
            for user in all_users:
                affected_users.add(user.username)
        except Exception as e:
            # 其他异常情况记录日志
            logger.error(f"Error getting role users: {e}")
            return
    elif instance.user_group:
        # 关联到用户组的权限，影响该组的所有用户
        try:
            users_in_group = PublicRbcaService.get_group_users(instance.user_group.id)
            if users_in_group is None:
                # 用户组已被删除，不需要处理
                logger.info("UserGroup has been deleted, skipping cache clearance")
                return
            for user in users_in_group:
                affected_users.add(user.username)
        except Exception as e:
            # 其他异常情况记录日志
            logger.error(f"Error getting role users: {e}")
            return
    
    # 清除受影响用户的密码权限缓存
    for username in affected_users:
        try:
            clear_password_permission_cache(username)
            logger.info(f"Cleared password permission cache for user: {username} due to permission change")
        except Exception as e:
            logger.error(f"Failed to clear password permission cache for user {username}: {e}")
