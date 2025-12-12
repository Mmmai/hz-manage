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
            import sys
            # if any(keyword in sys.argv for keyword in ['makemigrations', 'migrate', 'test', 'shell']):
            #     return
            post_migrate.connect(self.init_script, sender=self)
            # init_script()

        except OperationalError:
            pass
        except Exception as e:
            raise
    # 初始化数据

    def init_script(self, sender, **kwargs):
        if sender.name != 'mapi':
            return
        from mapi.models import UserInfo, UserGroup, Role, sysConfigParams
        from access.models import DataScope
        from cmdb.utils import password_handler
        # 初始化配置数据
        # 生成密钥
        initSysConfig = sysConfigParams.objects.all()
        if len(initSysConfig) == 0:
            sysconfigs = []
            for param in INIT_CONFIG:
                sysconfigs.append(
                    sysConfigParams(
                        verbose_name=param["verbose_name"],
                        param_name=param["param_name"],
                        param_value=param["param_value"],
                        param_type=param["param_type"],
                        description=param["description"]
                    )
                )
            sysConfigParams.objects.bulk_create(sysconfigs, ignore_conflicts=True)
        # 更新版本号
        app_dict = {
            "verbose_name": "系统版本",
            "param_name": "app_version",
            "param_value": os.environ.get('APP_VERSION', None),
            "param_type": "string",
            "description": "系统版本号，会根据启动的环境更新"
        }
        sysConfigParams.objects.update_or_create(param_name="app_version", defaults=app_dict)

        # 初始化用户、用户组和角色
        initList = UserInfo.objects.all()
        if len(initList) == 0:
            # 创建对象
            role_admin_obj = Role.objects.create(role="sysadmin", role_name="管理员", built_in=True)
            # 为管理员添加数据权限
            DataScope.objects.create(role=role_admin_obj, scope_type="all", description="管理员初始化数据权限")
            # role_admin_obj = Role.objects.get(role="管理员")
            # 创建用户组
            group_admin_obj = UserGroup.objects.create(group_name="系统管理组", built_in=True)
            group_admin_obj.roles.add(role_admin_obj.id)
            group_admin_obj.save()
            # 创建用户
            salt = secrets.token_hex(16)
            password_handler.load_keys()
            user_obj = UserInfo.objects.create(username="admin", password=password_handler.encrypt_to_sm4(
                f"{salt}:thinker"), password_salt=salt, built_in=True)
            user_obj.groups.add(group_admin_obj.id)
            user_obj.roles.add(role_admin_obj.id)
            logger.info("初始化完成,用户名密码为: admin/thinker")

            # 创建默认的普通用户组和普通用户角色
            role_common_obj = Role.objects.create(role="viewer", role_name="普通用户", built_in=True)
            group_common_obj = UserGroup.objects.create(group_name="普通用户组", built_in=True)
            group_common_obj.roles.add(role_common_obj.id)
            group_common_obj.save()
