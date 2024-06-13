from django.urls import path,re_path

from . import consumers

websocket_urlpatterns = [
	path('ws/ticketapp/inbox/', consumers.MessageListConsumer.as_asgi()),
    re_path(r'ws/ticketapp/', consumers.RoomConsumer.as_asgi()),
    #re_path(r'ws/chat/', consumers.RoomConsumer.as_asgi()),
    path("ws/", consumers.UserConsumer.as_asgi()),
]
    
