from django.apps import AppConfig
from django.db.models.signals import post_migrate
from .init_data import INIT_MENU,INIT_CONFIG
from .utils.comm import get_uuid
from django.db.utils import OperationalError
import os


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
    def init_script(self,sender,**kwargs):
        from mapi.models import UserInfo,UserGroup,Role,Menu,sysConfigParams,Button

        # 初始化用户、用户组和角色
        initList = UserInfo.objects.all()
        if len(initList) == 0:
            #创建对象
            role_admin_obj = Role.objects.create(role="sysadmin",role_name="管理员")
            role_common_obj = Role.objects.create(role="viewer",role_name="普通用户")
            # role_admin_obj = Role.objects.get(role="管理员")
            #创建用户组
            group_admin_obj = UserGroup.objects.create(group_name="系统管理组")
            group_admin_obj.roles.add(role_admin_obj.id)
            group_admin_obj.save()
            # 创建默认的普通用户组
            group_common_obj = UserGroup.objects.create(group_name="普通用户组")
            group_common_obj.roles.add(role_common_obj.id)
            group_common_obj.save()
            # 创建用户
            user_obj = UserInfo.objects.create(username="admin",password="thinker")
            user_obj.groups.add(group_admin_obj.id)
            user_obj.roles.add(role_admin_obj.id)
            # menuList = [ i.id for i in Menu.objects.all() ]
            # role_admin_obj.menu.set(Menu.objects.all())
            # role_admin_obj.save()
            print("初始化完成,用户名密码为: admin/thinker")
        menuInitList = INIT_MENU
        # 创建目录
        initMenu = Menu.objects.all()
        if len(initMenu) == 0:
        # print(123)
            for i in menuInitList:
                buttons = i.pop("buttons",None)
                if i['parentid_id'] == '':
                    # Menu.objects.create(**i)
                    i['parentid_id'] = None
                    instance, created = Menu.objects.get_or_create(**i)
                    if created:
                         print(f"Created a new menu diretory: {instance}")
                    else:
                         print(f"Menu diretory already exists: {instance}")            
                else:
                    parent_name = i['parentid_id']
                    parentid_id = Menu.objects.get(name=parent_name).id
                    i['parentid_id'] = str(parentid_id)
                    # print(i)
                    instance, created = Menu.objects.get_or_create(**i)
                    if created:
                        print(f"Created a new menu: {instance}")
                        if buttons:
                            # print(123)
                            for button in buttons:
                                button_instance,button_created  = Button.objects.get_or_create(name=button["name"],action=button["action"],menu=instance)
                                if button_created:
                                    print(f"菜单<{instance.label}>添加<${button_instance.name}>按钮!")

                    else:
                        print(f"Menu already exists: {instance}")         
        # 授权菜单给系统管理员
        # admin_role_id = role_admin_obj.id
        #获取菜单id
        # 初始化菜单数据
        # 生成密钥
        initSysConfig = sysConfigParams.objects.all()
        if len(initSysConfig) == 0:
            sysconfigs = []
            for param in INIT_CONFIG:
                sysconfigs.append(sysConfigParams(verbose_name=param["verbose_name"],param_name=param["param_name"],
                                                  param_value=param["param_value"],param_type=param["param_type"],
                                                  description=param["description"]))
            sysConfigParams.objects.bulk_create(sysconfigs,ignore_conflicts=True)