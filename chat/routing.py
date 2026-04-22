from django.urls import path

from chat.consumers import ChatConsumer


websocket_urlpatterns = [
    path('ws/chat/<int:conversation_id>/', ChatConsumer.as_asgi()),
]
