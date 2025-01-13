from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from rest_framework.exceptions import PermissionDenied

from apps.concensus.domain.entities.debate_message import Message
from apps.custom_auth.models import Group, User
import json

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_id = self.scope['url_route']['kwargs']['group_id']
        self.debate_id = self.scope['url_route']['kwargs']['debate_id']
        self.room_group_name = f"chat_{self.group_id}_{self.debate_id}"

        try:
            # Verificar si el usuario está autenticado
            if not self.scope['user'].is_authenticated:
                raise PermissionDenied("Usuario no autenticado.")

            # Verificar si el usuario pertenece al grupo
            is_member = await self.check_group_membership(self.scope['user'], self.group_id)
            if not is_member:
                raise PermissionDenied("Acceso denegado al grupo.")

            # Agregar al cliente al grupo WebSocket
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
        except PermissionDenied as e:
            await self.close(code=403)
            print(f"Conexión rechazada: {e}")
        except Exception as e:
            await self.close(code=500)
            print(f"Error al conectar al WebSocket: {e}")

    async def disconnect(self, close_code):
        # Remover al cliente del grupo WebSocket
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        user = self.scope['user']
        group_id = self.scope['url_route']['kwargs']['group_id']
        debate_id = self.scope['url_route']['kwargs']['debate_id']
        message_text = data['text']
        posture = data.get('posture', 'neutral')
        parent_id = data.get('parent')  # ID del mensaje al que se está respondiendo

        parent = None
        if parent_id:
            parent = await sync_to_async(Message.objects.get)(id=parent_id)

        # Guardar el mensaje
        message = await sync_to_async(Message.objects.create)(
            user=user,
            group_id=group_id,
            debate_id=debate_id,
            text=message_text,
            posture=posture,
            parent=parent
        )

        # Enviar el mensaje al grupo
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': {
                    'id': message.id,
                    'user': user.username,
                    'text': message_text,
                    'posture': posture,
                    'parent': parent_id,
                    'created_at': message.created_at.isoformat()
                }
            }
        )

    async def chat_message(self, event):
        """
        Reenvía un mensaje a los clientes.
        """
        await self.send(text_data=json.dumps(event['message']))

    @sync_to_async
    def check_group_membership(self, user, group_id):
        """
        Verifica si el usuario pertenece al grupo.
        """
        try:
            group = Group.objects.get(id=group_id)
            return group.users.filter(id=user.id).exists()
        except Group.DoesNotExist:
            return False
