# ./extensions/jwt_authenticate.py
# jwt验证
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
import jwt
import logging
from ..models import UserInfo

logger = logging.getLogger(__name__)

class JWTQueryParamsAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # token的获取路径
        # token = request.query_params.get('token')
        token = request.META.get('HTTP_TOKEN')
        # print(token)
        payload = None
        if not token:
            raise AuthenticationFailed({"code": 401, "error": "登录成功后才能访问"})
        # 切割
        # 解密payload，判断是否过期
        # 验证第三段的合法性
        salt = settings.SECRET_KEY
        try:
            # 从token中获取payload【不校验合法性】
            # unverified_payload = jwt.decode(token, None, False)
            # print(unverified_payload)
            # 从token中获取payload【校验合法性】
            payload = jwt.decode(jwt=token, key=salt, algorithms=["HS256"])
            # print(payload)
            user_id = payload.get("user_id")
            if not user_id:
                error = "token中用户信息不存在"
                raise AuthenticationFailed({"code": 401, "error": error})
            user = UserInfo.objects.filter(id=user_id).first()
            if not user:
                error = "token中用户信息已查询不到,token已失效"
                raise AuthenticationFailed({"code": 401, "error": error})
            return (user, token)
        except jwt.exceptions.ExpiredSignatureError:
            error = "token已失效"
            raise AuthenticationFailed({"code": 401, "error": error})
        except jwt.exceptions.DecodeError:
            error = "token已认证失败"
            raise AuthenticationFailed({"code": 401, "error": error})
        except jwt.exceptions.InvalidTokenError:
            error = "非法的token"
            raise AuthenticationFailed({"code": 401, "error": error})
        """ 三种操作
        1. 抛出异常，后续不在执行
        2. return 一个元组(1,2)认证通过，
        在视图中调用request.user就是元组的第一个值；
        另外一个就是request.auth
        3.None 
        """
        return (playload,token)
