import logging
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from mapi.public_services import PublicRoleService
from .models import Menu, Button, Permission
from .init_data import INIT_MENU
logger = logging.getLogger(__name__)


@receiver(post_migrate)
def init_menu(sender, **kwargs):
    if sender.name != 'access':
        return

    initMenu = Menu.objects.all()
    if len(initMenu) != 0:
        return

    menuInitList = INIT_MENU
    for i in menuInitList:
        buttons = i.pop("buttons", None)
        if i['parentid_id'] == '':
            i['parentid_id'] = None
            instance, created = Menu.objects.get_or_create(**i)
            if created:
                logger.info(f"Created a new menu directory: {instance}")
            else:
                logger.warning(f"Menu directory already exists: {instance}")
        else:
            parent_name = i['parentid_id']
            parentid_id = Menu.objects.get(name=parent_name).id
            i['parentid_id'] = str(parentid_id)
            instance, created = Menu.objects.get_or_create(**i)
            if created and buttons:
                for button in buttons:
                    button_instance, button_created = Button.objects.get_or_create(
                        name=button["name"],
                        action=button["action"],
                        menu=instance
                    )
                    logger.debug(f"Button creation status - Created: {button_created}, Instance: {button_instance}")
    logger.info("Menu initialization completed.")


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
        try:
            role_obj = PublicRoleService.get_sysadmin()
            Permission.objects.create(menu=instance.menu, button=instance, role=role_obj)
            logger.info(f"Automatically granted <{instance.menu.label}:{instance.name}> permission to sysadmin role.")
        except Exception as e:
            pass
