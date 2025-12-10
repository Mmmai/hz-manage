from django.apps import AppConfig
from django.db.models.signals import post_migrate
from .init_data import INIT_CONFIG
from .utils.comm import get_uuid
from django.db.utils import OperationalError
import secrets
import os

import logging
logger = logging.getLogger(__name__)

class MapiConfig(AppConfig):
    default_auto_field = 'django.db.models.AutoField'

    name = 'mapi'
    
    def ready(self):
        import mapi.signals
        try:
            post_migrate.connect(self.init_script, sender=self)   
        except OperationalError:
            pass
        except Exception as e:
            raise 
    
    # 初始化数据
    def init_script(self, sender, **kwargs):
        if sender.name != 'mapi':
            return
            
        from mapi.models import UserInfo, UserGroup, Role, Menu, sysConfigParams, Button, Permission
        from permissions.models import DataScope
        
        # 检查是否已经初始化过（通过特定标记）
        init_marker_param = "initialization_completed"
        
        # 检查初始化是否已完成
        if sysConfigParams.objects.filter(param_name=init_marker_param).exists():
            logger.info("系统已初始化完成，无需再次初始化")
            return
            
        try:
            # 初始化配置数据
            self._init_sys_configs(sysConfigParams)
            
            # 初始化系统管理员用户、用户组和角色
            self._init_users_and_roles(UserInfo, UserGroup, Role, DataScope)
            
            # 初始化菜单
            self._init_menus(Menu, Button)
            # 初始化普通用户
            self._init_common_user(UserInfo, UserGroup, Role)
            # 添加初始化完成标记
            sysConfigParams.objects.get_or_create(
                param_name=init_marker_param,
                defaults={
                    "verbose_name": "初始化完成标记",
                    "param_value": "true",
                    "param_type": "string",
                    "description": "标识系统初始化是否已完成"
                }
            )
            
            logger.info("系统初始化完成")
            
        except Exception as e:
            logger.error(f"系统初始化过程中发生错误: {e}")
            # 不添加完成标记，允许下次重新尝试初始化
            raise

    def _init_sys_configs(self, sysConfigParams):
        """初始化系统配置参数"""
        # 检查现有配置数量，如果已经有大部分配置则跳过
        existing_configs_count = sysConfigParams.objects.count()
        total_configs_count = len(INIT_CONFIG)
        
        # 如果已有配置超过80%，认为已初始化
        if existing_configs_count >= total_configs_count * 0.8 and existing_configs_count > 0:
            logger.info("系统配置参数已存在，跳过初始化")
        else:
            # 初始化配置数据
            # 生成密钥
            initSysConfig = sysConfigParams.objects.all()
            if len(initSysConfig) == 0:
                sysconfigs = []
                for param in INIT_CONFIG:
                    sysconfigs.append(sysConfigParams(
                        verbose_name=param["verbose_name"],
                        param_name=param["param_name"],
                        param_value=param["param_value"],
                        param_type=param["param_type"],
                        system=param.get("system", "common"),
                        description=param["description"]
                    ))
                sysConfigParams.objects.bulk_create(sysconfigs, ignore_conflicts=True)
                logger.info("系统配置参数初始化完成")
            else:
                logger.info("系统配置参数已存在，跳过初始化")
        
        # 更新版本号（总是执行）
        app_dict = {
            "verbose_name": "系统版本",
            "param_name": "app_version",
            "param_value": os.environ.get('APP_VERSION', None),
            "param_type": "string",
            "description": "系统版本号，会根据启动的环境更新"
        }
        sysConfigParams.objects.update_or_create(param_name="app_version", defaults=app_dict)

    def _init_users_and_roles(self, UserInfo, UserGroup, Role, DataScope):
        """初始化用户、用户组和角色"""
        # 检查是否已存在用户，如果存在则跳过用户初始化
        if UserInfo.objects.exists():
            logger.info("用户数据已存在，跳过用户初始化")
            return
            
        # 创建管理员角色
        role_admin_obj, role_created = Role.objects.get_or_create(
            role="sysadmin",
            defaults={
                "role_name": "管理员",
                "built_in": True
            }
        )
        
        if role_created:
            # 为管理员添加数据权限
            DataScope.objects.create(
                role=role_admin_obj,
                scope_type="all",
                description="管理员初始化数据权限"
            )
            logger.info("创建管理员角色")
        else:
            logger.info("管理员角色已存在")
            
        # 创建管理员用户组
        group_admin_obj, group_created = UserGroup.objects.get_or_create(
            group_name="系统管理组",
            defaults={"built_in": True}
        )
        
        if group_created:
            group_admin_obj.roles.add(role_admin_obj.id)
            group_admin_obj.save()
            logger.info("创建系统管理组")
        elif role_admin_obj not in group_admin_obj.roles.all():
            group_admin_obj.roles.add(role_admin_obj.id)
            group_admin_obj.save()
            logger.info("为系统管理组添加管理员角色")
        else:
            logger.info("系统管理组已存在且已关联管理员角色")
            
        # 创建管理员用户
        user_obj, user_created = UserInfo.objects.get_or_create(
            username="admin",
            defaults={
                "password_salt": secrets.token_hex(16),
                "built_in": True
            }
        )
        
        if user_created:
            from cmdb.utils import password_handler
            password_handler.load_keys()
            user_obj.password = password_handler.encrypt_to_sm4(f"{user_obj.password_salt}:thinker")
            user_obj.save()
            user_obj.groups.add(group_admin_obj.id)
            user_obj.roles.add(role_admin_obj.id)
            logger.info("初始化完成,用户名密码为: admin/thinker")
        else:
            logger.info("管理员用户已存在")
            

    def _init_common_user(self, UserInfo, UserGroup, Role):
        """初始化普通用户"""
        # 创建普通用户角色和组（即使管理员存在也可能不存在普通用户）
        role_common_obj, role_created = Role.objects.get_or_create(
            role="viewer",
            defaults={
                "role_name": "普通用户",
                "built_in": True
            }
        )
        
        if role_created:
            logger.info("创建普通用户角色")
            
        group_common_obj, group_created = UserGroup.objects.get_or_create(
            group_name="普通用户组",
            defaults={"built_in": True}
        )
        
        if group_created:
            group_common_obj.roles.add(role_common_obj.id)
            group_common_obj.save()
            logger.info("创建普通用户组")
        elif role_common_obj not in group_common_obj.roles.all():
            group_common_obj.roles.add(role_common_obj.id)
            group_common_obj.save()
            logger.info("为普通用户组添加普通用户角色")
        else:
            logger.info("普通用户组已存在且已关联普通用户角色")
    def _init_menus(self, Menu, Button):
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
