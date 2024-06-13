import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from channels.db import database_sync_to_async
from .models import ChatMessage
from django.db.models import Q, OuterRef, Subquery
from django.contrib.auth import get_user_model
User=get_user_model()




# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
        
		
#         self.room_group_name = 'chat'
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )
#         await self.accept()

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )

#     @database_sync_to_async
#     def create_message(self, message, username):
#         message_obj = ChatMessage.objects.create(
#             message=message,
#             username=username
#         )
#         return message_obj

#     async def receive(self, text_data):
        
#         data = json.loads(text_data)
#         message = data['message']
#         username = data['username']
        

#         # Create a new message object and save it to the database
#         message_obj = await self.create_message(message, username)

#         # Send the message to the group
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': message_obj.messsage,
#                 'username': message_obj.username,
#                 'date': str(message_obj.date)
#             }
#         )

#     async def chat_message(self, event):
#         message = event['message']
#         username = event['username']
#         date = event['date']

#         # Send the message to the websocket
#         await self.send(text_data=json.dumps({
#             'message': message,
#             'username': username,
#             'date': date
#         }))
        
		
import json

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework import mixins
from djangochannelsrestframework.observer.generics import (ObserverModelInstanceMixin, action)
from djangochannelsrestframework.observer import model_observer

from .models import Room, ChatMessage,Profile
# from django.contrib.auth.models import User
from .serializers import MessageSerializer, RoomSerializer, UserSerializer


class RoomConsumer(ObserverModelInstanceMixin, GenericAsyncAPIConsumer):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    lookup_field = "pk"
    print(lookup_field+'here---------------------')
    async def disconnect(self, code):
        print('here---------------------1')
        if hasattr(self, "room_subscribe"):
            await self.remove_user_from_room(self.room_subscribe)
            await self.notify_users()
        await super().disconnect(code)
       

    @action()
    async def join_room(self, pk, **kwargs):
        print('here---------------------2')
        print(pk)
       
        print(self.scope)
        print(self.scope['user'])
        self.room_subscribe = pk
        await self.add_user_to_room(pk)
        await self.notify_users()

    @action()
    async def leave_room(self, pk, **kwargs):
        await self.remove_user_from_room(pk)

    @action()
    async def create_message(self, message, **kwargs):
        serializer_class=MessageSerializer
        # reciever=UserSerializer
       
        print(self.room_subscribe)
        print('_________')
        
        # print(sender_profile = Profile.objects.get(user=self.sender))
        room: Room = await self.get_room(pk=self.room_subscribe)
        
        print(await self.current_users(room))
        # sender_profile = Profile.objects.get(user=self.sender)
        await database_sync_to_async(ChatMessage.objects.create)(
            room=room,
            user=self.scope["user"],
            sender=self.scope["user"],
            reciever=self.scope["user"],
            message=message

        )

    @action()
    async def subscribe_to_messages_in_room(self, pk, **kwargs):
        await self.message_activity.subscribe(room=pk)

    @model_observer(ChatMessage)
    async def message_activity(self, message, observer=None, **kwargs):
        await self.send_json(message)

    @message_activity.groups_for_signal
    def message_activity(self, instance: ChatMessage, **kwargs):
        yield f'room__{instance.room_id}'
        yield f'pk__{instance.pk}'

    @message_activity.groups_for_consumer
    def message_activity(self, room=None, **kwargs):
        if room is not None:
            yield f'room__{room}'

    @message_activity.serializer
    def message_activity(self, instance: ChatMessage, action, **kwargs):
        print(MessageSerializer(instance).data)
        return dict(data=MessageSerializer(instance).data, action=action.value, pk=instance.pk)

    async def notify_users(self):
        room: Room = await self.get_room(self.room_subscribe)
        for group in self.groups:
            await self.channel_layer.group_send(
                group,
                {
                    'type': 'update_users',
                    'users': await self.current_users(room)
                }
            )

    async def update_users(self, event: dict):
        await self.send(text_data=json.dumps({'users': event["users"]}))

    @database_sync_to_async
    def get_room(self, pk: int) -> Room:
        return Room.objects.get(pk=pk)

    @database_sync_to_async
    def current_users(self, room: Room):
        return [UserSerializer(user).data for user in room.current_users.all()]

    @database_sync_to_async
    def remove_user_from_room(self, room):
        user: User = self.scope["user"]
        user.current_rooms.remove(room)

    @database_sync_to_async
    def add_user_to_room(self, pk):
        print('here---------------------3')
        user: User = self.scope["user"]
        if not user.current_rooms.filter(pk=self.room_subscribe).exists():
            user.current_rooms.add(Room.objects.get(pk=pk))
    @database_sync_to_async        
    def sender_profile(self,sender):
        sender_profile = Profile.objects.get(user=self.sender)
        return sender_profile
    @action()
    async def create_task_message(self, message, performs,comment,**kwargs):
        serializer_class=MessageSerializer
        # reciever=UserSerializer
       
        print(self.room_subscribe)
        print('_________')
        
        # print(sender_profile = Profile.objects.get(user=self.sender))
        room: Room = await self.get_room(pk=self.room_subscribe)
        
        print(await self.current_users(room))
        # sender_profile = Profile.objects.get(user=self.sender)
        await database_sync_to_async(ChatMessage.objects.create)(
            author=self.scope['user'],
            performs=performs,
            task_info=message,
            message=comment,

        )
   
        

  

class UserConsumer(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        mixins.PatchModelMixin,
        mixins.UpdateModelMixin,
        mixins.CreateModelMixin,
        mixins.DeleteModelMixin,
        GenericAsyncAPIConsumer,
):

    queryset = User.objects.all()
    print(34344)
    serializer_class = UserSerializer
class MessageListConsumer(mixins.ListModelMixin,mixins.RetrieveModelMixin,
        mixins.PatchModelMixin,
        mixins.UpdateModelMixin,
        mixins.CreateModelMixin,
        mixins.DeleteModelMixin,
        GenericAsyncAPIConsumer,):
    queryset = ChatMessage.objects.all()
    serializer_class=MessageSerializer
   
