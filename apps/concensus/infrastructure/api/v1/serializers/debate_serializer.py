from rest_framework import serializers
from apps.concensus.domain.entities.debate import Debate
from apps.concensus.domain.entities.debate_participant import DebateParticipant

class DebateSerializer(serializers.ModelSerializer):

    # created_at = serializers.DateTimeField(format="%y-%m-%d %H:%M:%S")  # Formato personalizado
    # end_time = serializers.DurationField()  # Manejo de intervalos

    class Meta:
        model = Debate
        fields = ['id', 'group', 'title', 'description', 'created_at', 'end_time', 'is_closed']
        read_only_fields = ['id', 'created_at', 'is_closed']

    def create(self, validated_data):
        group = validated_data['group']

        # Validar si el grupo ya tiene un debate activo
        if Debate.objects.filter(group=group, is_closed=False).exists():
            raise serializers.ValidationError("This group already has an active debate.")

        # Crear el debate
        debate = super().create(validated_data)

        # Registrar automáticamente a los usuarios del grupo como participantes
        participants = group.users.all()  # Accedes a los usuarios relacionados con el grupo
        for participant in participants:
            DebateParticipant.objects.create(debate=debate, participant=participant)

        return debate

    def validate(self, data):
        group = self.context['group']
        if not group:
            raise serializers.ValidationError("El grupo especificado no existe.")
        return data

class DebateParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = DebateParticipant
        fields = ['id', 'debate', 'participant', 'joined_at', 'is_collaborator']

