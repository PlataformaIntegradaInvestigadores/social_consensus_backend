import json
import logging
import redis
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async, async_to_sync
from django.apps import apps
from django.conf import settings



logger = logging.getLogger(__name__)

class GroupConsumer(AsyncWebsocketConsumer):
    """
    Consumer de WebSocket para manejar conexiones y mensajes de un grupo específico.
    """

    # 1. Métodos de Conexión y Desconexión
    async def connect(self):
        """
        Método asíncrono llamado cuando un cliente intenta conectarse.
        Se añade el cliente al grupo de canales y se acepta la conexión WebSocket.
        También incrementa el contador de conexiones activas.
        """
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
        """
        Método asíncrono llamado cuando un cliente se desconecta.
        Se elimina el cliente del grupo de canales y se decrementa el contador de conexiones activas.
        """
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

        await self.decrement_connection_count()

    # 2. Método de Envío de Mensajes del WebSocket del Servidor
    async def receive(self, text_data):
        """
        Método asíncrono llamado cuando se recibe un mensaje del cliente.
        Procesa el mensaje, creando o obteniendo un tema recomendado y añadiéndolo al grupo.
        Luego, envía un mensaje al grupo con los detalles del tema añadido.
        """
        try:
            data = json.loads(text_data)
            logger.info(f'Data received: {data}')  # Loguear datos recibidos

            # Verificar que 'user_id' está en los datos recibidos
            if 'topic' not in data or 'user_id' not in data['topic']:
                logger.error(f'Error: user_id is required, {data} received')
                return

            user_id = data['topic']['user_id']
            topic_name = data['topic']['topic']

            RecommendedTopic = apps.get_model('concensus', 'RecommendedTopic')
            TopicAddedUser = apps.get_model('concensus', 'TopicAddedUser')

            recommended_topic, created = await sync_to_async(RecommendedTopic.objects.get_or_create)(
                topic_name=topic_name, defaults={'group_id': self.group_id}
            )
            topic_added = await sync_to_async(TopicAddedUser.objects.create)(
                topic=recommended_topic, group_id=self.group_id, user_id=user_id
            )

            await self.notify_new_topic(topic_added)
            logger.info(f'SE ENVIO LAS NOTIFICAIONES DE NUEVO TOPIC:') 

        except json.JSONDecodeError:
            logger.error('Error: received data is not valid JSON')
        except KeyError as e:
            logger.error(f'Error: Missing key in data received: {e}')
        except Exception as e:
            logger.error(f'Unexpected error: {e}')


    async def group_message(self, event):
        """
        Método asíncrono que maneja los mensajes recibidos en el grupo y los envía a través del WebSocket.
        """
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))

    # 3. Métodos Adicionales: Conteo de Conexiones y Notificación de Nuevo Tema
    @sync_to_async
    def increment_connection_count(self):
        """
        Incrementa el contador de conexiones activas en el grupo y notifica a los clientes.
        """
        connection_count = self.get_connection_count() + 1
        self.set_connection_count(connection_count)
        self.notify_connection_count(connection_count)

    @sync_to_async
    def decrement_connection_count(self):
        """
        Decrementa el contador de conexiones activas en el grupo y notifica a los clientes.
        """
        connection_count = self.get_connection_count() - 1
        if connection_count < 0:
            connection_count = 0
        self.set_connection_count(connection_count)
        self.notify_connection_count(connection_count)

    def get_connection_count(self):
        """
        Obtiene el número actual de conexiones activas desde Redis.
        """
        connection_count = self.redis.get(self.group_name)
        return int(connection_count) if connection_count else 0

    def set_connection_count(self, count):
        """
        Establece el número de conexiones activas en Redis.
        """
        self.redis.set(self.group_name, count)

    def notify_connection_count(self, count):
        """
        Notifica a los clientes el número actualizado de conexiones activas en el grupo.
        """
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

    async def notify_new_topic(self, topic_added):
        """
        Notifica a los clientes que se ha añadido un nuevo tema al grupo.
        """
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'group_message',
                'message': {
                    'type': 'new_topic',
                    'id': topic_added.id,
                    'topic_name': topic_added.topic.topic_name,
                    'user_id': topic_added.user_id,
                    'group_id': topic_added.group_id,
                    'added_at': topic_added.added_at.isoformat()
                }
            }
        )


# concensus_recommendedtopic
# concensus_topicaddeduser