from mapi.models import UserInfo


class SystemUser:
    """
    模拟系统用户，用于系统自动化操作时通过 require_valid_user 校验。

    该类模拟 UserInfo 实例的关键属性，使其可以通过 isinstance(user, UserInfo) 检查。
    通过注册为 UserInfo 的虚拟子类实现类型兼容。

    使用方式:
        from mapi.system_user import SYSTEM_USER
    """

    def __init__(self, username: str = 'system'):
        self.username = username
        self.password = '_'

    def __str__(self):
        return self.username


# 将 SystemUser 注册为 UserInfo 的虚拟子类，使 isinstance 检查通过
UserInfo.register(SystemUser)

# 预置的系统用户单例
SYSTEM_USER = SystemUser('system')
