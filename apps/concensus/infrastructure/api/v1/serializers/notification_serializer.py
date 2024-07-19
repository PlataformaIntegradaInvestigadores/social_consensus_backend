from rest_framework import serializers

from apps.concensus.domain.entities.notification import NotificationPhaseOne
from apps.concensus.domain.entities.notification import NotificationPhaseTwo

class NotificationSerializer(serializers.ModelSerializer):
    profile_picture_url = serializers.SerializerMethodField()

    class Meta:
        model = NotificationPhaseOne
        fields = ['id', 'user', 'group', 'notification_type', 'message', 'created_at', 'profile_picture_url']

    def get_profile_picture_url(self, obj):
        request = self.context.get('request')
        profile_picture_url = obj.user.profile_picture.url
        return request.build_absolute_uri(profile_picture_url) if profile_picture_url else None
    
class NotificationPhaseTwoSerializer(serializers.ModelSerializer):
    profile_picture_url = serializers.SerializerMethodField()
    
    class Meta:
        model = NotificationPhaseTwo
        fields = ['id', 'user', 'group', 'notification_type', 'message', 'created_at', 'profile_picture_url']
    
    def get_profile_picture_url(self, obj):
        request = self.context.get('request')
        profile_picture_url = obj.user.profile_picture.url
        return request.build_absolute_uri(profile_picture_url) if profile_picture_url else None
