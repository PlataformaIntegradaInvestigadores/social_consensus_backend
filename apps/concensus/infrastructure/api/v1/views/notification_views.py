from rest_framework import generics, permissions
from django.apps import apps 
from apps.concensus.domain.entities.notification import NotificationPhaseOne
from apps.concensus.infrastructure.api.v1.serializers.notification_serializer import NotificationSerializer
from rest_framework import status
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework.response import Response


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        group_id = self.kwargs['group_id']
        return NotificationPhaseOne.objects.filter(group_id=group_id).order_by('created_at')


class TopicVisitedView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        group_id = self.kwargs['group_id']
        data = request.data
        topic_id = data.get('topic_id')
        user_id = data.get('user_id')

        if not topic_id or not user_id:
            return Response({"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)

        Topic = apps.get_model('concensus', 'RecommendedTopic')
        TopicAddedUser = apps.get_model('concensus', 'TopicAddedUser')
        User = apps.get_model('custom_auth', 'User')
        Group = apps.get_model('custom_auth', 'Group')

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
        message = f'{user.first_name} {user.last_name} 👀 visited <i>{topic.topic_name}<i>'

        # Almacenar la notificación en la base de datos
        notification = NotificationPhaseOne.objects.create(
            user=user,
            group=group,
            notification_type='topic_visited',
            message=message
        )

        # Enviar notificación por WebSocket
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
        User = apps.get_model('custom_auth', 'User')
        Group = apps.get_model('custom_auth', 'Group')

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
                return Response({"error": f"Topic with id {topic_id} does not exist in this group"}, status=status.HTTP_404_NOT_FOUND)
            topic_names.append(topic.topic_name)

        combined_topics = ', '.join(topic_names)
        message = f'{user.first_name} {user.last_name} 🔍 made a combined search for Topics: {combined_topics}'

        notification = NotificationPhaseOne.objects.create(
            user=user,
            group=group,
            notification_type='combined_search',
            message=message
        )

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'group_{group_id}',
            {
                'type': 'group_message',
                'message': {
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