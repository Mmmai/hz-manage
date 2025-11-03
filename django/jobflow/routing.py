
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    # path('jobflow/ws/test/', consumers.ws_test.as_asgi()),  # WebSocket 路由
    path('jobflow/ws/ansible/', consumers.ws_ansible.as_asgi()),  

]
