from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from django.utils.timezone import now
from apps.concensus.domain.entities.debate import Debate
from apps.custom_auth.domain.entities.group import Group
from apps.concensus.infrastructure.api.v1.serializers.debate_serializer import DebateSerializer

class DebateViewSet(ModelViewSet):
    """
    ViewSet para manejar los debates relacionados con los grupos.
    """
    queryset = Debate.objects.all()
    serializer_class = DebateSerializer

    def get_queryset(self):
        """
        Filtra los debates basados en el group_id proporcionado en la URL.
        """
        group_id = self.kwargs.get('group_id')
        if not group_id:
            return Debate.objects.none()  # Devuelve un queryset vacío si no hay group_id
        return Debate.objects.filter(group__id=group_id)

    def create(self, request, *args, **kwargs):
        """
        Crea un nuevo debate asociado a un grupo.
        """
        group_id = self.kwargs.get('group_id')
        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            return Response({"detail": "Group not found."}, status=status.HTTP_404_NOT_FOUND)

        # Validar si ya existe un debate activo en el grupo
        if Debate.objects.filter(group=group, is_closed=False).exists():
            return Response({"detail": "This group already has an active debate."}, status=status.HTTP_400_BAD_REQUEST)

        # Crear el debate
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(group=group)  # Asocia el debate al grupo

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def close(self, _request, *_args, **_kwargs):
        """
        Cierra un debate específico asociado a un grupo.
        """
        debate = self.get_object()

        if debate.is_closed:
            return Response({"detail": "Debate is already closed."}, status=status.HTTP_400_BAD_REQUEST)

        # Cerrar el debate
        debate.is_closed = True
        debate.save()

        # Notificar a los participantes del cierre (si es necesario)
        self.notify_participants(debate, "The debate has been manually closed.")

        return Response({"detail": "Debate closed successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def validate_status(self, _request, *_args, **_kwargs):
        """
        Valida el estado del debate y lo cierra automáticamente si ya expiró.
        """
        debate = self.get_object()

        if debate.is_closed:
            return Response({"detail": "Debate is already closed."}, status=status.HTTP_200_OK)

        # Verificar si el debate ha llegado a su fecha de finalización
        if now() >= debate.end_time:
            debate.is_closed = True
            debate.save()
            self.notify_participants(debate, "The debate has been automatically closed due to expiration.")
            return Response({"detail": "Debate was automatically closed due to expiration."}, status=status.HTTP_200_OK)

        return Response({"detail": "Debate is still active."}, status=status.HTTP_200_OK)

    @staticmethod
    def notify_participants(debate, message):
        """
        Envía notificaciones a los participantes del debate.
        """
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        channel_layer = get_channel_layer()
        participants = debate.participants.values_list('participant__id', flat=True)

        for participant_id in participants:
            async_to_sync(channel_layer.group_send)(
                f"user_{participant_id}",
                {"type": "notify", "message": message}
            )