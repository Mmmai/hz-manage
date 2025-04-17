# -*- coding: utf-8 -*-
# Auther : 风雪
# Date : 2023/9/10 13:32
# File : sm4加密.py


from gmssl import sm4, func

# 密钥（16字节）

def sm4_crypt(data_byte,key_byte):
    # 创建SM4对象
    crypt_sm4 = sm4.CryptSM4()
    # 设置密钥
    crypt_sm4.set_key(key_byte, sm4.SM4_ENCRYPT)
    # 加密数据
    encrypted_data = crypt_sm4.crypt_ecb(data_byte)
    return encrypted_data


def sm4_decrypt(encrypted_data,key_byte):
    # 创建一个新的SM4对象用于解密
    decrypt_sm4 = sm4.CryptSM4()
    # 设置密钥
    decrypt_sm4.set_key(key_byte, sm4.SM4_DECRYPT)
    # 解密数据

    decrypted_data = decrypt_sm4.crypt_ecb(encrypted_data)
    return decrypted_data

if __name__ == '__main__':
    # 明文数据（确保是16的倍数）
    data = 'ttt111111322222'
    
    key = '77eabfc6c32511ef'
    key_byte=key.encode("utf-8")
    print(key_byte)
    data_byte=data.encode("utf-8")
    
    encrypted_data_byte=sm4_crypt(data_byte=data_byte,key_byte=key_byte)
    decrypted_data_byte=sm4_decrypt(bytes.fromhex("edb2111f91bc940d49166adb0fe493edd262d563faa2ac15e01af44a02c17b99"),key_byte)
    print(bytes.fromhex("451849b3ecc1ce5a1d943ce6aceedbaa"))
    print("加密后的数据：", encrypted_data_byte) # b'\xdf\xa4\xcfb\x9e\x97K\x1a\x10\xaee@gBn\x07G\xd6\xf9\xb0\xcbD\x97\x86\x84\xaa\x05&\x98\x01oq'
    print("解密后的数据：", decrypted_data_byte.decode("utf-8")) # Hello, SM4 encryption!
    import uuid
    print(str(uuid.uuid1()).replace("-","")[0:16])

