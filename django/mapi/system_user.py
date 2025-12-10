from mapi.models import UserInfo


class SystemUser(UserInfo):
    """
    模拟系统用户，用于系统自动化操作时通过 require_valid_user 校验。

    使用方式:
        from mapi.system_user import SYSTEM_USER
    """

    def __init__(self, username: str = 'system'):
        self.username = username
        self.password = '_'

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        # 系统用户不保存数据库
        pass

    def delete(self, *args, **kwargs):
        # 系统用户不删除
        pass
    class Meta:
        app_label = 'mapi'
        managed = False
        abstract = False

# 预置的系统用户单例
SYSTEM_USER = SystemUser('system')
