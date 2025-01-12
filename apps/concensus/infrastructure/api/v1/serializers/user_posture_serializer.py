from rest_framework import serializers
from apps.concensus.domain.entities.debate_participant_posture import UserPosture


class UserPostureSerializer(serializers.ModelSerializer):
    class Meta:
        # El modelo al que hace referencia:
        model = UserPosture

        # Campos a exponer
        fields = ['id', 'user', 'debate', 'posture', 'updated_at']

        # Campos que son de solo lectura (no se aceptan en el POST/PUT):
        read_only_fields = ['id', 'updated_at']

        # extra_kwargs si se requiere personalizar algo adicional:
        # extra_kwargs = {
        #     'posture': {'required': True, 'allow_blank': False},
        # }

