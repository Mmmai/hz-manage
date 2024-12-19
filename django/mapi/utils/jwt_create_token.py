# ./utils/jwt_create_token.py
# 创建jwt的token
import jwt,datetime
from django.conf import settings

def create_token(payload,timeout=5):
    salt = settings.SECRET_KEY
    # 构造Header，默认如下
    headers = {
        'typ': 'jwt',
        'alg': 'HS256'
    }
    #设置超时
    # payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(minutes=timeout)
    jwt_token = jwt.encode(headers=headers, payload=payload, key=salt, algorithm='HS256')
    return jwt_token
