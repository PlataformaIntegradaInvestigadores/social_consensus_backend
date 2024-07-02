from rest_framework import serializers

from apps.concensus.domain.entities.notification import NotificationPhaseOne

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPhaseOne
        fields = ['id', 'user', 'group', 'notification_type', 'message', 'created_at']
