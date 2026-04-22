import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from chat.models import Conversation, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.group_name = f'chat_{self.conversation_id}'
        self.user = self.scope['user']

        if not self.user.is_authenticated:
            await self.close(code=4001)
            return

        if not await self.is_participant():
            await self.close(code=4003)
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return

        data = json.loads(text_data)
        event_type = data.get('type')

        if event_type == 'message':
            message = await self.create_message(data.get('content', ''))
            if not message:
                await self.send_json({'type': 'error', 'detail': 'Message content cannot be empty.'})
                return

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat.message',
                    'message': message,
                },
            )
            return

        if event_type == 'typing':
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat.typing',
                    'user_id': self.user.id,
                    'is_typing': bool(data.get('is_typing', True)),
                },
            )
            return

        if event_type == 'read':
            updated = await self.mark_read()
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat.read',
                    'user_id': self.user.id,
                    'updated': updated,
                },
            )

    async def chat_message(self, event):
        await self.send_json({'type': 'message', **event['message']})

    async def chat_typing(self, event):
        await self.send_json({
            'type': 'typing',
            'user_id': event['user_id'],
            'is_typing': event['is_typing'],
        })

    async def chat_read(self, event):
        await self.send_json({
            'type': 'read',
            'user_id': event['user_id'],
            'updated': event['updated'],
        })

    async def send_json(self, data):
        await self.send(text_data=json.dumps(data))

    @database_sync_to_async
    def is_participant(self):
        return Conversation.objects.filter(
            id=self.conversation_id,
            participants=self.user,
        ).exists()

    @database_sync_to_async
    def create_message(self, content):
        if not content or not content.strip():
            return None

        conversation = Conversation.objects.get(id=self.conversation_id)
        message = Message.objects.create(
            conversation=conversation,
            sender=self.user,
            content=content,
        )
        conversation.save(update_fields=('updated_at',))
        return {
            'id': message.id,
            'conversation': conversation.id,
            'sender': {
                'id': self.user.id,
                'username': self.user.username,
            },
            'content': message.content,
            'created_at': message.created_at.isoformat(),
            'is_read': message.is_read,
        }

    @database_sync_to_async
    def mark_read(self):
        return Message.objects.filter(
            conversation_id=self.conversation_id,
            is_read=False,
        ).exclude(sender=self.user).update(is_read=True)
