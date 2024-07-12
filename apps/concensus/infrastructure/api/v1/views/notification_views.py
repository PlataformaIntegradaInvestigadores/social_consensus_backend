from venv import logger
from rest_framework import generics, permissions
from django.apps import apps 
from apps.concensus.domain.entities.notification import NotificationPhaseOne, NotificationPhaseTwo
from apps.concensus.domain.entities.user_phase import UserPhase
from apps.concensus.infrastructure.api.v1.serializers.notification_serializer import NotificationPhaseTwoSerializer, NotificationSerializer
from rest_framework import status
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework.response import Response
from django.utils import timezone


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        group_id = self.kwargs['group_id']
        return NotificationPhaseOne.objects.filter(group_id=group_id).order_by('created_at')
    

class NotificationPhaseTwoListView(generics.ListAPIView):
    serializer_class = NotificationPhaseTwoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        group_id = self.kwargs['group_id']
        return NotificationPhaseTwo.objects.filter(group_id=group_id).order_by('created_at')

class TopicVisitedView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        group_id = self.kwargs['group_id']
        data = request.data
        topic_id = data.get('topic_id')
        user_id = data.get('user_id')

        logger.info(f"Received data: {data}")

        if not topic_id or not user_id:
            return Response({"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)

        Topic = apps.get_model('concensus', 'RecommendedTopic')
        TopicAddedUser = apps.get_model('concensus', 'TopicAddedUser')
        User = apps.get_model('custom_auth', 'User')
        Group = apps.get_model('custom_auth', 'Group')
        NotificationPhaseOne = apps.get_model('concensus', 'NotificationPhaseOne')

        # Verificar que el usuario y el grupo existen
        try:
            user = User.objects.get(id=user_id)
            group = Group.objects.get(id=group_id)
        except User.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response({"error": "Group does not exist"}, status=status.HTTP_404_NOT_FOUND)

        # Intentar obtener el topic directamente
        try:
            topic = Topic.objects.get(id=topic_id, group_id=group_id)
        except Topic.DoesNotExist:
            # Si el topic no se encuentra, intentar obtenerlo desde la tabla TopicAddedUser
            try:
                topic_added_user = TopicAddedUser.objects.get(id=topic_id, group_id=group_id)
                topic = topic_added_user.topic
            except TopicAddedUser.DoesNotExist:
                return Response({"error": "Topic does not exist in this group"}, status=status.HTTP_404_NOT_FOUND)

        # Crear mensaje de notificación
        message = f'{user.first_name} {user.last_name} 👀 visited <i>{topic.topic_name}</i>'

        # Verificar si ya existe una notificación similar
        existing_notification = NotificationPhaseOne.objects.filter(
            user=user, group=group, notification_type='topic_visited', message=message
        ).first()

        logger.info(f"Existing notification: {existing_notification}")

        if existing_notification:
            # Si la notificación ya existe, actualizar la fecha
            existing_notification.created_at = timezone.now()
            existing_notification.save()
            notification = existing_notification
        else:
            # Si la notificación no existe, crear una nueva
            notification = NotificationPhaseOne.objects.create(
                user=user,
                group=group,
                notification_type='topic_visited',
                message=message
            )

             # Construir la URL completa de la imagen de perfil
        profile_picture_url = user.profile_picture.url if user.profile_picture else None

        # Enviar notificación por WebSocket solo si es nueva
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'group_{group_id}',
            {
                'type': 'group_message',
                'message': {
                    'id': notification.id,
                    'user_id': user_id,
                    'group_id': group_id,
                    'type': 'topic_visited',
                    'notification_message': message,
                    'added_at': notification.created_at.isoformat(),
                    'topic_id': topic_id,
                    'profile_picture_url': profile_picture_url,  # Añadir la URL de la imagen de perfil

                }
            }
        )

        serializer = NotificationSerializer(notification)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CombinedSearchView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        group_id = self.kwargs['group_id']
        data = request.data
        topics = data.get('topics', [])
        user_id = data.get('user_id')

        if not topics or not user_id:
            return Response({"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)

        Topic = apps.get_model('concensus', 'RecommendedTopic')
        TopicAddedUser = apps.get_model('concensus', 'TopicAddedUser')
        User = apps.get_model('custom_auth', 'User')
        Group = apps.get_model('custom_auth', 'Group')
        NotificationPhaseOne = apps.get_model('concensus', 'NotificationPhaseOne')

        try:
            user = User.objects.get(id=user_id)
            group = Group.objects.get(id=group_id)
        except User.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response({"error": "Group does not exist"}, status=status.HTTP_404_NOT_FOUND)

        topic_names = []
        for topic_id in topics:
            try:
                topic = Topic.objects.get(id=topic_id, group_id=group_id)
            except Topic.DoesNotExist:
                try:
                    topic_added_user = TopicAddedUser.objects.get(id=topic_id, group_id=group_id)
                    topic = topic_added_user.topic
                except TopicAddedUser.DoesNotExist:
                    return Response({"error": f"Topic with id {topic_id} does not exist in this group"}, status=status.HTTP_404_NOT_FOUND)
            topic_names.append(topic.topic_name)

        combined_topics = ', '.join(topic_names)
        message = f'{user.first_name} {user.last_name} 🔍 made a combined search for Topics: {combined_topics}'

        # Verificar si ya existe una notificación similar
        existing_notification = NotificationPhaseOne.objects.filter(
            user=user, group=group, notification_type='combined_search', message=message
        ).first()

        if existing_notification:
            # Si la notificación ya existe, actualizar la fecha
            existing_notification.created_at = timezone.now()
            existing_notification.save()
            notification = existing_notification
        else:
            # Si la notificación no existe, crear una nueva
            notification = NotificationPhaseOne.objects.create(
                user=user,
                group=group,
                notification_type='combined_search',
                message=message
            )

        # Enviar notificación por WebSocket solo si es nueva
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'group_{group_id}',
            {
                'type': 'group_message',
                'message': {
                    'id': notification.id,
                    'type': 'combined_search',
                    'topics': topics,
                    'user_id': user_id,
                    'group_id': group_id,
                    'notification_message': message,
                    'added_at': notification.created_at.isoformat(),
                }
            }
        )

        serializer = NotificationSerializer(notification)
        return Response(serializer.data, status=status.HTTP_201_CREATED)    

class PhaseOneCompletedView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        group_id = self.kwargs['group_id']
        user_id = request.user.id

        User = apps.get_model('custom_auth', 'User')
        Group = apps.get_model('custom_auth', 'Group')

        try:
            user = User.objects.get(id=user_id)
            group = Group.objects.get(id=group_id)
        except User.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response({"error": "Group does not exist"}, status=status.HTTP_404_NOT_FOUND)

        message = f'{user.first_name} {user.last_name} ✔️ has completed the phase One'
        notification = NotificationPhaseOne.objects.create(
            user=user,
            group=group,
            notification_type='phase_one_completed',
            message=message
        )

        # Update or create UserPhase
        UserPhase.objects.update_or_create(user=user, group=group, defaults={'phase': 1, 'completed_at': timezone.now()})

        # Emit WebSocket message
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'group_{group_id}',
            {
                'type': 'group_message',
                'message': {
                    'id': notification.id,
                    'type': 'consensus_completed',
                    'user_id': user_id,
                    'group_id': group_id,
                    'added_at': notification.created_at.isoformat(),
                    'notification_message': message
                }
            }
        )

        serializer = NotificationSerializer(notification)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class TopicReorderView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, group_id):
        data = request.data
        topic_id = data.get('topic_id')
        user_id = data.get('user_id')
        original_position = data.get('original_position')
        new_position = data.get('new_position')

        if not topic_id or not user_id or original_position is None or new_position is None:
            return Response({"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)

        Topic = apps.get_model('concensus', 'RecommendedTopic')
        Group = apps.get_model('custom_auth', 'Group')
        User = apps.get_model('custom_auth', 'User')

        try:
            topic = Topic.objects.get(id=topic_id, group_id=group_id)
            user = User.objects.get(id=user_id)
            group = Group.objects.get(id=group_id)
        except Topic.DoesNotExist:
            return Response({"error": "Topic does not exist in this group"}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response({"error": "Group does not exist"}, status=status.HTTP_404_NOT_FOUND)

        # Crear mensaje de notificación personalizado
        if new_position < original_position:
            message = f'{user.first_name} {user.last_name} moved 🚀 up topic "{topic.topic_name}" from {original_position} to {new_position}'
        else:
            message = f'{user.first_name} {user.last_name} moved 👇 down topic "{topic.topic_name}" from {original_position} to {new_position}'

        # Almacenar la notificación en la base de datos
        notification = NotificationPhaseTwo.objects.create(
            user=user,
            group=group,
            notification_type='topic_reorder',
            message=message
        )

        # Enviar notificación por WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'phase2_group_{group_id}',  # Asegúrate de que la ruta sea correcta
            {
                'type': 'group_message',
                'message': {
                    'type': 'topic_reorder',
                    'topic_id': topic_id,
                    'user_id': user_id,
                    'group_id': group_id,
                    'added_at': notification.created_at.isoformat(),
                    'notification_message': message
                }
            }
        )

        serializer = NotificationPhaseTwoSerializer(notification)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TopicTagView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, group_id):
        data = request.data
        topic_id = data.get('topic_id')
        user_id = data.get('user_id')
        tag = data.get('tag')

        if not topic_id or not user_id or not tag:
            return Response({"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)

        Topic = apps.get_model('concensus', 'RecommendedTopic')
        Group = apps.get_model('custom_auth', 'Group')
        User = apps.get_model('custom_auth', 'User')

        try:
            topic = Topic.objects.get(id=topic_id, group_id=group_id)
            user = User.objects.get(id=user_id)
            group = Group.objects.get(id=group_id)
        except Topic.DoesNotExist:
            return Response({"error": "Topic does not exist in this group"}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response({"error": "Group does not exist"}, status=status.HTTP_404_NOT_FOUND)

        # Crear mensaje de notificación personalizado con emojis
        emoji_dict = {
            "Novel": "🌟",
            "Attractive": "💖",
            "Trend": "🔥",
            "Obsolete": "🗑️",
            "Unfamiliar": "❓"
        }

        message = f'{user.first_name} {user.last_name} tagged topic "{topic.topic_name}" as "{tag}" {emoji_dict.get(tag, "")}'

        # Almacenar la notificación en la base de datos
        NotificationPhaseTwo = apps.get_model('concensus', 'NotificationPhaseTwo')
        notification = NotificationPhaseTwo.objects.create(
            user=user,
            group=group,
            notification_type='topic_tag',
            message=message
        )

        # Enviar notificación por WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'phase2_group_{group_id}',  # Asegúrate de que la ruta sea correcta
            {
                'type': 'group_message',
                'message': {
                    'type': 'topic_tag',
                    'topic_id': topic_id,
                    'user_id': user_id,
                    'group_id': group_id,
                    'added_at': notification.created_at.isoformat(),
                    'notification_message': message
                }
            }
        )

        serializer = NotificationPhaseTwoSerializer(notification)
        return Response(serializer.data, status=status.HTTP_201_CREATED)