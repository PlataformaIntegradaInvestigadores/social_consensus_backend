import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.apps import apps

class GroupConsumer(AsyncWebsocketConsumer):

    active_connections = 0

    async def connect(self):
        self.group_id = self.scope['url_route']['kwargs']['group_id']
        self.group_name = f'group_{self.group_id}'

        GroupConsumer.active_connections += 1

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'group_message',
                'message': {
                    'type': 'connection_count',
                    'active_connections': GroupConsumer.active_connections
                }
            }
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

        GroupConsumer.active_connections -= 1

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'group_message',
                'message': {
                    'type': 'connection_count',
                    'active_connections': GroupConsumer.active_connections
                }
            }
        )

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
