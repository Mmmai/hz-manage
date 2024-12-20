from .crypto import PasswordHandler

# 创建单例
password_handler = PasswordHandler()

__all__ = ['password_handler']