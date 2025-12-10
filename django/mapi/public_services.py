from .models import Role


class PublicRoleService:
    @staticmethod
    def get_sysadmin():
        return Role.objects.get(role='sysadmin')
