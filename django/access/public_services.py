
"""
对外权限接口模块
提供对外修改权限相关的服务接口，供其他应用调用。
"""
import logging
from .models import *
from .services import *

logger = logging.getLogger(__name__)


class PublicPermissionService:
    """对外权限接口"""

    @staticmethod
    def get_user_permissions(user):
        """
        获取用户的所有权限，包括通过角色、用户组和直接授权的权限
        """
        return PermissionService.get_user_permissions(user)

    @staticmethod
    def add_home_permission_to_role(instance):
        """自动为新创建的角色添加首页查看权限"""
        menu_obj = Menu.objects.get(name="home")
        buttonObj = Button.objects.get(menu=menu_obj, action="view")
        Permission.objects.create(menu=menu_obj, role=instance, button=buttonObj)
        logger.info(f"Automatically granted <{menu_obj.label}> permission to role <{instance.role}>.")

    @staticmethod
    def create_role_permissions(instance, rolePermission):
        """为新创建的角色添加权限"""
        for button_id in rolePermission:
            button_obj = Button.objects.get(id=button_id)
            Permission.objects.update_or_create(role=instance, menu=button_obj.menu, button=button_obj)
            logger.info(f"为角色<{instance.role}>添加<{button_obj.action}>权限!")
            # 如果有其他按钮权限，查看的权限应该同步添加，就算用户没有勾选！
            if button_obj.action != "view":
                pass
            else:
                view_button_obj = Button.objects.get(action="view", menu=button_obj.menu)
                view_per_obj, created = Permission.objects.get_or_create(
                    role=instance, menu=button_obj.menu, button=view_button_obj)
                if created:
                    logger.info(f"为角色<{instance.role}>添加<{view_button_obj.action}>权限!")
                else:
                    logger.info(f"为角色<{instance.role}>已拥有<{view_button_obj.action}>权限!")

    @staticmethod
    def update_role_permissions(instance, rolePermission):
        """更新角色权限"""
        currentPermissionList = [
            str(i)
            for i in Permission.objects.filter(role=instance).values_list("button", flat=True)
        ]
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

    @staticmethod
    def add_permissions_to_role(request, role, button_ids):
        """为角色添加权限"""
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
                logger.warning(f"按钮ID<{button_id}>不存在，跳过添加权限操作。")
            except Exception as e:
                logger.error(f"添加角色<{role.role}>权限时出错: {str(e)}")
                raise e
        return added_permissions, existing_permissions

    @staticmethod
    def remove_permissions_from_role(request, role, button_ids):
        """为角色移除权限"""

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
                logger.warning(f"按钮ID<{button_id}>不存在，跳过删除权限操作。")
            except Exception as e:
                logger.error(f"删除角色<{role.role}>权限时出错: {str(e)}")
                raise e
        return list(set(removed_permissions))


class PublicButtonService:

    @staticmethod
    def get_init_buttons():
        """获取初始化按钮列表"""
        return Button.objects.all()
