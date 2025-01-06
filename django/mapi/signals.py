from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Menu,Permission,Role,Button


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
            buttons = [Button(name='查看', action='view',menu=instance),]
        # role_obj = Role.objects.get(role="sysadmin")
        # 定义需要添加的按钮
        else:
            buttons = [
                Button(name='查看', action='view',menu=instance),
                Button(name='添加', action='add',menu=instance),
                Button(name='删除', action='delete',menu=instance),
                Button(name='修改', action='edit',menu=instance)
            ]
        for button in buttons:
            button.save()
            # Permission.objects.create(menu=instance, button=button,role=role_obj)
            print(f"创建按钮<{instance.label}:{button.name}>!")
@receiver(post_save, sender=Button)
def atuo_add_to_sysadmin(sender, instance, created, **kwargs):
    if created:
        # 当 MyModel 的实例被创建时执行此代码
        # print(f"New instance of MyModel created: {instance}")
        role_obj = Role.objects.get(role="sysadmin")
        Permission.objects.create(menu=instance.menu, button=instance,role=role_obj)
        print(f"将<{instance.menu.label}:{instance.name}>授予管理员权限!")