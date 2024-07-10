from rest_framework import serializers
from apps.concensus.domain.entities.user_satisfaction import UserSatisfaction


class UserSatisfactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSatisfaction
        fields = ['user', 'group', 'satisfaction_level', 'created_at', 'message']

