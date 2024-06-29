import json
import redis
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async, async_to_sync
from django.apps import apps
from django.conf import settings

class GroupConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_id = self.scope['url_route']['kwargs']['group_id']
        self.group_name = f'group_{self.group_id}'
        self.redis = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

        await self.increment_connection_count()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

        await self.decrement_connection_count()

    async def receive(self, text_data):
        data = json.loads(text_data)
        topic_name = data['topic_name']
        user_id = data['user_id']

        RecommendedTopic = apps.get_model('concensus', 'RecommendedTopic')
        TopicAddedUser = apps.get_model('concensus', 'TopicAddedUser')
        
        recommended_topic, created = await sync_to_async(RecommendedTopic.objects.get_or_create)(
            topic_name=topic_name, defaults={'group_id': self.group_id}
        )
        topic_added = await sync_to_async(TopicAddedUser.objects.create)(
            topic=recommended_topic, group_id=self.group_id, user_id=user_id
        )

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'group_message',
                'message': {
                    'id': topic_added.id,
                    'topic_name': topic_added.topic.topic_name,
                    'user_id': topic_added.user_id,
                    'group_id': topic_added.group_id,
                    'added_at': topic_added.added_at.isoformat()
                }
            }
        )

    async def group_message(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))

    @sync_to_async
    def increment_connection_count(self):
        """Incrementa el contador de conexiones activas en el grupo y notifica a los clientes."""
        connection_count = self.get_connection_count() + 1
        self.set_connection_count(connection_count)
        self.notify_connection_count(connection_count)

    @sync_to_async
    def decrement_connection_count(self):
        """Decrementa el contador de conexiones activas en el grupo y notifica a los clientes."""
        connection_count = self.get_connection_count() - 1
        if connection_count < 0:
            connection_count = 0
        self.set_connection_count(connection_count)
        self.notify_connection_count(connection_count)

    def get_connection_count(self):
        """Obtiene el número actual de conexiones activas desde Redis."""
        connection_count = self.redis.get(self.group_name)
        return int(connection_count) if connection_count else 0

    def set_connection_count(self, count):
        """Establece el número de conexiones activas en Redis."""
        self.redis.set(self.group_name, count)

    def notify_connection_count(self, count):
        """Notifica a los clientes el número actualizado de conexiones activas en el grupo."""
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'group_message',
                'message': {
                    'type': 'connection_count',
                    'active_connections': count
                }
            }
        )
