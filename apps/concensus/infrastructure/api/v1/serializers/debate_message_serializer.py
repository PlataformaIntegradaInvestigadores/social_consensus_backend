from rest_framework import serializers
from apps.concensus.domain.entities.debate_message import Message

class MessageSerializer(serializers.ModelSerializer):
    # Un campo extra para mostrar el username, sin exponer la relación entera:
    user_name = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Message
        fields = [
            'id',
            'user',
            'user_name',
            'debate',
            'text',
            'posture',
            'parent',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
