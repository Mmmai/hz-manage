
from cryptography.fernet import Fernet
from gmssl.sm4 import CryptSM4, SM4_ENCRYPT, SM4_DECRYPT
import traceback
from django.conf import settings
import base64
import logging
from typing import Optional
from threading import Lock

from cryptography.utils import CryptographyDeprecationWarning
warnings.filterwarnings(action='ignore',message='Python 3.6 is no longer supported')

logger = logging.getLogger(__name__)


class PasswordHandler:
    _instance = None
    _lock = Lock()
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # 初始化时不立即加载密钥
        pass

    def load_keys(self):
        """加载加密密钥"""
        if self._initialized:
            return

        try:
            with self._lock:  # 加锁防止多线程重复加载
                if not self._initialized:
                    from mapi.models import sysConfigParams
                    secret_key = sysConfigParams.objects.get(param_name="secret_key").param_value
                    self.fernet_key = base64.urlsafe_b64encode(secret_key.encode()[:32].ljust(32, b'\0'))
                    self.fernet = Fernet(self.fernet_key)
                    self.sm4_key = secret_key.encode('utf-8')
                    self._init_sm4()
                    self._initialized = True
                    logger.info("Secret key loaded successfully.")
        except Exception as e:
            logger.error(f"Secret key loading failed: {str(e)}")
            raise

    def reload_keys(self):
        """重新加载加密密钥"""
        self._initialized = False
        self.load_keys()

    def _init_sm4(self):
        """初始化 SM4 加解密器"""
        self.sm4_key = self.sm4_key[:16].ljust(16, b'\0')
        self.sm4_encryptor = CryptSM4()
        self.sm4_encryptor.set_key(self.sm4_key, SM4_ENCRYPT)

        self.sm4_decryptor = CryptSM4()
        self.sm4_decryptor.set_key(self.sm4_key, SM4_DECRYPT)

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

    def encrypt_to_sm4(self, value: str) -> str:
        """静态方法：使用 SM4 加密"""
        try:
            # 使用 SM4 加密
            sm4_encrypted = self.sm4_encryptor.crypt_ecb(
                value.encode('utf-8')
            )
            return sm4_encrypted.hex()
        except Exception as e:
            raise ValueError(f"SM4 encryption failed: {str(e)}")

    def decrypt_sm4(self, value: str) -> str:
        """静态方法：使用 SM4 解密"""
        try:
            if not value:
                return None
            # 使用 SM4 解密
            plain_text = self.sm4_decryptor.crypt_ecb(
                bytes.fromhex(value)
            )
            return plain_text.decode('utf-8')
        except Exception as e:
            raise ValueError(f"SM4 decryption failed: {str(e)}")

    def decrypt_to_plain(self, stored_value: str) -> str:
        """静态方法：完全解密获取明文密码"""
        try:
            if not stored_value:
                return ""
            # 先解密 Fernet
            logger.debug(f"Decrypting: {stored_value}")
            sm4_hex = self.decrypt(stored_value)
            logger.debug(f"SM4 hex: {sm4_hex}")
            # 再解密 SM4
            plain_text = self.sm4_decryptor.crypt_ecb(
                bytes.fromhex(sm4_hex)
            )
            return plain_text.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Full decryption failed: {str(e)}")

    def re_encrypt(self, pass_dict: dict) -> dict:
        """重新加密密码字典"""
        if not isinstance(pass_dict, dict):
            raise ValueError("Invalid password dictionary.")

        new_password = {}
        try:
            for meta_id, encrypted in pass_dict.items():
                if encrypted:
                    plain = self.decrypt_to_plain(encrypted)
                    new_password[meta_id] = plain
                else:
                    new_password[meta_id] = ""
            self.reload_keys()
            for meta_id, plain in new_password.items():
                if plain:
                    encrypted_sm4 = self.encrypt_to_sm4(plain)
                    # logger.info(f'Re-encrypting plain -> sm4: {plain} -> {encrypted_sm4}')
                    new_password[meta_id] = self.encrypt(encrypted_sm4)
                    # logger.info(f'Re-encrypted by fernet: {new_password[meta_id]}')
            return new_password
        except Exception as e:
            raise ValueError(f"Re-encryption failed: {str(e)}")


if __name__ == "__main__":
    handler = PasswordHandler()
    handler.load_keys()
    plain = 'ttt11111132'
    encrypted = handler.encrypt_to_sm4(plain)
    print("Encrypted:", encrypted)

    # 模拟前端加密后的 hex 字符串
    sm4_encrypted_hex = "5ea8b5e5ce9872b9f52432f49e29d005"

    # Fernet 二次加密存储
    stored = handler.encrypt(sm4_encrypted_hex)
    print("Stored value:", stored)

    # 完整解密流程
    try:
        plain = handler.decrypt_to_plain(stored)
        print("Decrypted:", plain)
    except Exception as e:
        print(f"Decryption failed: {traceback.format_exc()}")
