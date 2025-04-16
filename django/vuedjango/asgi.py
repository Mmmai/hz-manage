"""
ASGI config for vuedjango project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

# vuedjango_name/asgi.py

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import mapi.routing  # 引入 WebSocket 路由

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vuedjango.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # 处理传统 HTTP 请求
    "websocket":   # 处理 WebSocket 请求
        URLRouter(
            mapi.routing.websocket_urlpatterns  # 配置 WebSocket 路由
        )
    ,
})


