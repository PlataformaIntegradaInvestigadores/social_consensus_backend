from django.db import models
import logging
from django.apps import apps
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from apps.concensus.domain.entities.user_satisfaction import UserSatisfaction
from apps.concensus.infrastructure.api.v1.serializers.user_satisfaction_serializer import UserSatisfactionSerializer


logger = logging.getLogger(__name__)

class UserSatisfactionView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSatisfactionSerializer

    def post(self, request, *args, **kwargs):
        group_id = self.kwargs['group_id']
        user_id = request.user.id
        satisfaction_level = request.data.get('satisfaction_level')

        if not satisfaction_level:
            return Response({"error": "Satisfaction level is required"}, status=status.HTTP_400_BAD_REQUEST)

        Group = apps.get_model('custom_auth', 'Group')
        User = apps.get_model('custom_auth', 'User')

        try:
            group = Group.objects.get(id=group_id)
            user = User.objects.get(id=user_id)
        except Group.DoesNotExist:
            return Response({"error": "Group does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

        notification_message = f'{user.first_name} {user.last_name} is {satisfaction_level}'

        # Create or update the satisfaction record
        satisfaction, created = UserSatisfaction.objects.update_or_create(
            user=user,
            group=group,
            defaults={'satisfaction_level': satisfaction_level},
            created_at=timezone.now(),
            message=notification_message
        )

        # Calculate the new counts for each satisfaction level
        satisfaction_counts = UserSatisfaction.objects.filter(group=group).values('satisfaction_level').annotate(count=models.Count('satisfaction_level'))

        counts = {item['satisfaction_level']: item['count'] for item in satisfaction_counts}

        profile_picture_url = user.profile_picture.url if user.profile_picture else None

        # Prepare WebSocket message
        message = {
            'type': 'user_satisfaction',
            'user_id': user_id,
            'group_id': group_id,
            'satisfaction_level': satisfaction_level,
            'notification_message': notification_message,
            'added_at': timezone.now().isoformat(),
            'profile_picture_url': profile_picture_url,
            'counts': counts
        }

        # Send WebSocket notification
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'phase3_group_{group_id}',
            {
                'type': 'group_message',
                'message': message
            }
        )

        logger.info(f'WebSocket notification sent for group: {group_id} with satisfaction level: {satisfaction_level}')
        return Response({"message": "Satisfaction recorded successfully.", "data": message}, status=status.HTTP_201_CREATED)

class LoadUserSatisfactionNotificationsView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSatisfactionSerializer

    def get_queryset(self):
        group_id = self.kwargs['group_id']
        return UserSatisfaction.objects.filter(group_id=group_id).order_by('-created_at')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context
    
class LoadSatisfactionCountsView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, group_id):
        Group = apps.get_model('custom_auth', 'Group')

        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            return Response({"error": "Group does not exist"}, status=status.HTTP_404_NOT_FOUND)

        satisfaction_counts = UserSatisfaction.objects.filter(group=group).values('satisfaction_level').annotate(count=models.Count('satisfaction_level'))

        counts = {item['satisfaction_level']: item['count'] for item in satisfaction_counts}

        return Response({"counts": counts}, status=status.HTTP_200_OK)