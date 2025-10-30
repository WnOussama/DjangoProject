import json
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
# from django.contrib.auth.models import User
from apps.app_users.models import User
from apps.app_chat.models import Message
from asgiref.sync import sync_to_async, async_to_sync
from channels.db import database_sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        user1 = self.scope['user'].username 
        user2 = self.room_name
        self.room_group_name = f"chat_{''.join(sorted([user1, user2]))}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender = self.scope['user']  
        receiver = await self.get_receiver_user() 

        await self.save_message(sender, receiver, message)

        # new: compute unread count for receiver and broadcast
        unread_total = await self.get_unread_count(receiver)
        sender_unread = await self.get_unread_from_sender(receiver, sender)
        await self.channel_layer.group_send(
            f"messages_{receiver.uid}",
            {
                "type": "send.message_count",
                "value": json.dumps({
                    "count": unread_total,
                    "sender": sender.username,
                    "sender_unread": sender_unread,
                }),
            }
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'sender': sender.username,
                'receiver': receiver.username,
                'message': message
            }
        )
        

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        receiver = event['receiver']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'sender': sender,
            'receiver': receiver,
            'message': message
        }))

    @sync_to_async
    def save_message(self, sender, receiver, message):
        Message.objects.create(sender=sender, receiver=receiver, content=message)

    @sync_to_async
    def get_receiver_user(self):
        return User.objects.get(username=self.room_name)

    @sync_to_async
    def get_unread_count(self, user):
        return Message.objects.filter(receiver=user, is_read=False).count()

    @sync_to_async
    def get_unread_from_sender(self, receiver, sender):
        return Message.objects.filter(receiver=receiver, sender=sender, is_read=False).count()


class NotificationConsumerTest(WebsocketConsumer):
    def connect(self):
        self.room_name = "notifications"
        self.room_group_name = "notifications_group"
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()
        self.send(text_data=json.dumps({
            'message': 'Connected to the Notification room.'
        }))

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        print(f"Received data: {text_data}")
        self.send(text_data=f"Received: {text_data}")

    def send_notification(self, event):
        value = event['value']
        print(f"Sending notification: {value}")
        self.send(text_data=value)
        
    def send_error(self, event):
        error_message = event['error']
        print(f"Sending error: {error_message}")
        self.send(text_data=json.dumps({
            'error': error_message
        }))



class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if user.is_anonymous:
            # reject unauthenticated
            await self.close()
            return

        self.group_name = f"notifications_{user.uid}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        self.send(text_data=json.dumps({
            'message': 'Connected to the Notification room.'
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # send.notification must match the "type" above
    async def send_notification(self, event):
        await self.send(text_data=event["value"])


class MessageCountConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if user.is_anonymous:
            await self.close()
            return

        self.group_name = f"messages_{user.uid}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # send initial unread count
        from apps.app_chat.models import Message
        count = await database_sync_to_async(Message.objects.filter(receiver=user, is_read=False).count)()
        await self.send(text_data=json.dumps({"count": count}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_message_count(self, event):
        await self.send(text_data=event["value"])