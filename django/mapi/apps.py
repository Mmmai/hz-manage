from django.apps import AppConfig
from django.db.models.signals import post_migrate
from .init_data import INIT_MENU

# 初始化数据
def init_script(sender, **kwargs):
    from mapi.models import UserInfo,Role,Menu
    menuInitList = INIT_MENU
    # 创建目录
    initMenu = Menu.objects.all()
    if len(initMenu) == 0:
        for i in menuInitList:
            if i['parentid_id'] == '':
                Menu.objects.create(**i)
            else:
                parent_name = i['parentid_id']
                parentid_id = Menu.objects.get(name=parent_name).id
                i['parentid_id'] = parentid_id
                Menu.objects.create(**i)
    # 初始化用户和角色
    initList = UserInfo.objects.all()
    if len(initList) == 0:
        #创建对象
        Role.objects.create(role="管理员")
        Role.objects.create(role="普通用户")
        #创建用户
        role_obj = Role.objects.get(role="管理员")
        role_id = role_obj.id
        user_obj = UserInfo.objects.create(username="admin",password="thinker")
        user_obj.roles.add(role_id)
        role_obj = Role.objects.get(role="管理员")
        menuList = [ i.id for i in Menu.objects.all() ]
        role_obj.menu.set(Menu.objects.all())
        role_obj.save()
        print("初始化完成,用户名密码为: admin/thinker")

    # 授权菜单给系统管理员
    # admin_role_id = role_obj.id
    #获取菜单id
    # 初始化菜单数据


class MapiConfig(AppConfig):
    name = 'mapi'
    def ready(self):
        pass
        post_migrate.connect(init_script, sender=self)    