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
        token = request.META.get('HTTP_TOKEN')
        payload = None
        if not token:
            raise AuthenticationFailed({"code": 401, "error": "登录成功后才能访问"})
        # 切割
        # 解密payload，判断是否过期
        # 验证第三段的合法性
        salt = settings.SECRET_KEY
        try:
            # 从token中获取payload【校验合法性】
            payload = jwt.decode(jwt=token, key=salt, algorithms=["HS256"])
            # print(payload)
            user_id = payload.get("user_id")
            token_password = payload.get("password")  # 获取token中的密码
            if not user_id:
                error = "token中用户信息不存在"
                raise AuthenticationFailed({"code": 401, "error": error})
            user = UserInfo.objects.filter(id=user_id).first()
            if not user:
                error = "token中用户信息已查询不到,token已失效"
                raise AuthenticationFailed({"code": 401, "error": error})
                
            # 检查用户是否已过期
            if user.is_expired():
                error = "用户账户已过期"
                raise AuthenticationFailed({"code": 401, "error": error})
            # 检查密码是否匹配（用户修改密码后，token中的密码与数据库中的密码不一致）
            if token_password != user.password:
                error = "密码已更改，请重新获取token"
                raise AuthenticationFailed({"code": 401, "error": error})            
            # 检查用户状态
            if not user.status:
                error = "用户已被禁用"
                raise AuthenticationFailed({"code": 401, "error": error})
            if not user:
                error = "token中用户信息已查询不到,token已失效"
                raise AuthenticationFailed({"code": 401, "error": error})
            return (user, token)
        except jwt.exceptions.ExpiredSignatureError:
            error = "token已过期"
            raise AuthenticationFailed({"code": 401, "error": error})
        except jwt.exceptions.DecodeError:
            error = "token认证失败"
            raise AuthenticationFailed({"code": 401, "error": error})
        except jwt.exceptions.InvalidTokenError:
            error = "非法的token"
            raise AuthenticationFailed({"code": 401, "error": error})

