from cryptography.fernet import Fernet
from gmssl.sm4 import CryptSM4, SM4_ENCRYPT, SM4_DECRYPT
import traceback
from django.conf import settings
import base64
import logging
from typing import Optional
from mapi.models import sysConfigParams
logger = logging.getLogger(__name__)

class PasswordHandler:
    def __init__(self):
        # print(123)
        # try:
        key = base64.urlsafe_b64encode(settings.SM4_KEY.encode()[:32].ljust(32, b'\0'))
        self.fernet = Fernet(key)
        self.sm4_key = settings.SM4_KEY.encode('utf-8')
        self._init_sm4()
        # except Exception as e:
        #     print(e)



    def _init_sm4(self):
        """初始化 SM4 加解密器"""
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
        
    
        
    def decrypt_to_plain(self, stored_value: str) -> str:
        """静态方法：完全解密获取明文密码"""
        try:
            if not stored_value:
                return ""
            # 先解密 Fernet
            logger.info(f"Decrypting: {stored_value}")
            sm4_hex = self.decrypt(stored_value)
            logger.info(f"SM4 hex: {sm4_hex}")
            # 再解密 SM4
            plain_text = self.sm4_decryptor.crypt_ecb(
                bytes.fromhex(sm4_hex)
            )
            return plain_text.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Full decryption failed: {str(e)}")


if __name__ == "__main__":
    handler = PasswordHandler()
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