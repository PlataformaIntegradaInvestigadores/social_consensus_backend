from rest_framework import serializers

from apps.concensus.domain.entities.user_phase import UserPhase


class UserPhaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPhase
        fields = ['user', 'group', 'phase', 'completed_at']
