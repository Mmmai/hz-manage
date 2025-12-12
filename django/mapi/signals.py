import re
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from access.public_services import PublicPermissionService, PublicButtonService
from .models import Role, sysConfigParams
from .messages import zabbix_config_updated

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Role)
def auto_add_home_to_role(sender, instance, created, **kwargs):
    if created:
        if instance.role == "sysadmin":
            return
        PublicPermissionService.add_home_permission_to_role(instance)


@receiver(post_save, sender=Role)
def init_sysadmin_permissions(sender, instance, created, **kwargs):
    if created and instance.role == "sysadmin":
        buttons = PublicButtonService.get_init_buttons()
        button_ids = [str(button.id) for button in buttons]
        PublicPermissionService.add_permissions_to_role(None, instance, button_ids)
        logger.info(f"Initialized all permissions for sysadmin role <{instance.role}>.")


@receiver(post_save, sender=sysConfigParams)
def monitor_sys_config_change(sender, instance, created, **kwargs):
    # zabbix配置发生变化时通知node_mg立即刷新配置
    if re.match("^zabbix", instance.param_name):
        zabbix_config_updated.send()
        logger.debug(f'Zabbix configuration parameter "{instance.param_name}" has changed, sent update signal.')
