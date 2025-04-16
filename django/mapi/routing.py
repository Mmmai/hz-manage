
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/test/', consumers.ws_test.as_asgi()),  # WebSocket 路由
]
