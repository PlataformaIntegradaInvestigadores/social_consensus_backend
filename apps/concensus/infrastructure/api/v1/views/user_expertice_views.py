from django.utils import timezone
from venv import logger
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.apps import apps
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from apps.concensus.domain.entities.notification import NotificationPhaseOne
from apps.concensus.domain.entities.user_expertice import UserExpertise
from apps.concensus.infrastructure.api.v1.serializers.user_expertice_serializer import UserExpertiseSerializer

class UserExpertiseView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserExpertiseSerializer

    def create(self, request, *args, **kwargs):
        group_id = self.kwargs['group_id']
        data = request.data
        topic_id = data.get('topic_id')
        user_id = data.get('user_id')
        expertise_level = data.get('expertise_level', 1)

        # Agregar prints para depuración
        logger.info(f"Received data: {data}")
        logger.info(f'Data : group_id: {group_id}, topic_id: {topic_id}, user_id: {user_id}, expertise_level: {expertise_level}')

        if not topic_id or not user_id:
            logger.error("Invalid data: Missing topic_id or user_id")
            return Response({"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Convertir expertise_value a entero y asegurarse de que sea entre 1 y 100
            expertise_value = int(expertise_level)
            if expertise_value < 0:
                expertise_value = 1
            elif expertise_value > 100:
                expertise_value = 100
        except ValueError:
            return Response({"error": "experticeValue must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

        # Convertir expertise_value de 0-100 a 1-10
        expertise_level = max(1, (expertise_value // 10))
        
        
        # Obtener modelos dinámicamente
        RecommendedTopic = apps.get_model('concensus', 'RecommendedTopic')
        TopicAddedUser = apps.get_model('concensus', 'TopicAddedUser')
        User = apps.get_model('custom_auth', 'User')
        Group = apps.get_model('custom_auth', 'Group')
        NotificationPhaseOne = apps.get_model('concensus', 'NotificationPhaseOne')

        try:
            user = User.objects.get(id=user_id)
            group = Group.objects.get(id=group_id)
        except User.DoesNotExist:
            logger.error("User does not exist")
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            logger.error("Group does not exist")
            return Response({"error": "Group does not exist"}, status=status.HTTP_404_NOT_FOUND)

        try:
            recommendedTopic = RecommendedTopic.objects.get(id=topic_id, group_id=group_id)
        except RecommendedTopic.DoesNotExist:
            try:
                topic_added_user = TopicAddedUser.objects.get(id=topic_id, group_id=group_id)
                recommendedTopic = topic_added_user.topic
            except TopicAddedUser.DoesNotExist:
                logger.error("Topic does not exist")
                return Response({"error": "Topic does not exist in this group"}, status=status.HTTP_404_NOT_FOUND)

        try:
            user_expertise, created = UserExpertise.objects.update_or_create(
                user=user, group=group, topic=recommendedTopic,
                defaults={'expertise_level': expertise_level, 'has_provided_expertise': True}
            )
            logger.info(f"User expertise {'created' if created else 'updated'} successfully")
        except Exception as e:
            logger.error(f"Error in update_or_create: {str(e)}")
            return Response({"error": "Error updating or creating user expertise"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Crear mensaje de notificación basado en el nivel de experiencia
         # Crear mensaje de notificación basado en el nivel de experiencia
        #message = f'{user.first_name} {user.last_name} set their expertise level to {expertise_level} ({expertise_status}) for topic <i>{recommendedTopic.topic_name}</i>'

        if expertise_level <= 3:
            #expertise_status = 'junior'
            message = f'{user.first_name} {user.last_name} 🌱 is a junior in <i>{recommendedTopic.topic_name}</i>'
        elif expertise_level <= 7:
            #expertise_status = 'intermediate'
            message = f'{user.first_name} {user.last_name} 📖 has intermediate knowledge in <i>{recommendedTopic.topic_name}</i>'
        else:
            #expertise_status = 'expert'
            message = f'{user.first_name} {user.last_name} 🧠 is an expert in <i>{recommendedTopic.topic_name}</i>'

         # Verificar si ya existe una notificación similar
        existing_notification = NotificationPhaseOne.objects.filter(
            user=user, group=group, notification_type='user_expertise', message=message
        ).first()

        # Construir la URL completa de la imagen de perfil
        profile_picture_url = user.profile_picture.url if user.profile_picture else None


        
        if existing_notification:
            existing_notification.created_at = timezone.now()
            existing_notification.save()
            notification = existing_notification
        else:
            notification = NotificationPhaseOne.objects.create(
                user=user,
                group=group,
                notification_type='user_expertise',
                message=message
            )
        
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'group_{group_id}',
                {
                    'type': 'group_message',
                    'message': {
                        'id': notification.id,
                        'type': 'user_expertise',
                        'user_id': user_id,
                        'group_id': group_id,
                        'topic_id': topic_id,
                        'expertise_level': expertise_level,
                        'added_at': user_expertise.updated_at.isoformat(),
                        'notification_message': message,
                        'profile_picture_url': profile_picture_url,
                    }
                }
            )
            logger.info("Message sent through channels successfully")
        except Exception as e:
            logger.error(f"Error sending message through channels: {str(e)}")
            return Response({"error": "Error sending message through channels"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializer = self.get_serializer(user_expertise)
        return Response(serializer.data, status=status.HTTP_201_CREATED)