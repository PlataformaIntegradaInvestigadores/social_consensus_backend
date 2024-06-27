""" # consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class GroupConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = self.scope['url_route']['kwargs']['group_name']
        self.group_group_name = f"group_{self.group_name}"

        await self.channel_layer.group_add(
            self.group_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        topic = text_data_json['topic']

        await self.channel_layer.group_send(
            self.group_group_name,
            {
                'type': 'group_message',
                'topic': topic
            }
        )

    async def group_message(self, event):
        topic = event['topic']

        await self.send(text_data=json.dumps({
            'topic': topic
        }))
 """