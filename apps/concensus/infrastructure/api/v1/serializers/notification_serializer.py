from rest_framework import serializers

from apps.concensus.domain.entities.notification import NotificationPhaseOne
from apps.concensus.domain.entities.notification import NotificationPhaseTwo

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPhaseOne
        fields = ['id', 'user', 'group', 'notification_type', 'message', 'created_at']
    
class NotificationPhaseTwoSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPhaseTwo
        fields = ['id', 'user', 'group', 'notification_type', 'message', 'created_at']
