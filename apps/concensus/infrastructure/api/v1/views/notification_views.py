from rest_framework import generics, permissions

from apps.concensus.domain.entities.notification import NotificationPhaseOne
from apps.concensus.infrastructure.api.v1.serializers.notification_serializer import NotificationSerializer


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        group_id = self.kwargs['group_id']
        return NotificationPhaseOne.objects.filter(group_id=group_id).order_by('created_at')

