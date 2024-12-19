from cryptography.fernet import Fernet
from django.conf import settings
import base64
import hashlib
from typing import Optional

class PasswordHandler:
    def __init__(self):
        key = base64.urlsafe_b64encode(settings.SECRET_KEY.encode()[:32].ljust(32, b'\0'))
        self.fernet = Fernet(key)

    def encrypt(self, password: str) -> str:
        if not password:
            return ""
        try:
            return self.fernet.encrypt(password.encode()).decode()
        except Exception as e:
            raise ValueError(f"Encrypt failed: {str(e)}")

    def decrypt(self, token: str) -> str:
        if not token:
            return ""
        try:
            return self.fernet.decrypt(token.encode()).decode()
        except Exception as e:
            raise ValueError(f"Decrypt failed: {str(e)}")


