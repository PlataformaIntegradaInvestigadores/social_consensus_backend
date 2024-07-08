# views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.apps import apps
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from apps.concensus.domain.entities.final_topic_order import FinalTopicOrder
from apps.concensus.infrastructure.api.v1.serializers.final_topic_serializer import FinalTopicOrderSerializer
from django.utils import timezone

from apps.concensus.infrastructure.api.v1.serializers.notification_serializer import NotificationPhaseTwoSerializer
from apps.custom_auth.domain.entities.user import User


class SaveFinalTopicOrderView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FinalTopicOrderSerializer

    def post(self, request, group_id):
        data = request.data
        user_id = request.user.id

        final_topic_orders = data.get('final_topic_orders', [])

        if not final_topic_orders:
            return Response({"error": "No topic order data provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Delete existing records for this user and group
        FinalTopicOrder.objects.filter(idGroup=group_id, idUser=user_id).delete()

        # Save new records
        for order in final_topic_orders:
            order['idGroup'] = group_id
            order['idUser'] = user_id
            serializer = self.serializer_class(data=order)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Send WebSocket notification
        group = apps.get_model('custom_auth', 'Group').objects.get(id=group_id)
        message = f'{request.user.first_name} {request.user.last_name} has finalized the consensus phase 2.'
        user = User.objects.get(id=user_id)
        
        NotificationPhaseTwo = apps.get_model('concensus', 'NotificationPhaseTwo')
        notification = NotificationPhaseTwo.objects.create(
            user=user,
            group=group,
            notification_type='consensus_finalized',
            message=message
        )
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'phase2_group_{group_id}',
            {
                'type': 'group_message',
                'message': {
                    'type': 'consensus_finalized',
                    'user_id': user_id,
                    'group_id': group_id,
                    'notification_message': message,
                    'added_at': timezone.now().isoformat(),
                }
            }
        )

        notification_serializer = NotificationPhaseTwoSerializer(notification)
        return Response(notification_serializer.data, status=status.HTTP_201_CREATED)