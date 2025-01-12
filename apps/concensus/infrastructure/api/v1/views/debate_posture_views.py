# discussion_app/views.py
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


from apps.concensus.domain.entities.debate_participant_posture import UserPosture
from apps.concensus.infrastructure.api.v1.serializers.user_posture_serializer import UserPostureSerializer

# de prueba

from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.apps import apps
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets

from apps.concensus.domain.entities.debate import Debate
from apps.concensus.domain.entities.debate_participant import DebateParticipant
from apps.concensus.infrastructure.api.v1.serializers.notification_serializer import NotificationSerializer
from apps.custom_auth.domain.entities.group import Group
from apps.custom_auth.domain.entities.group import GroupUser
from apps.concensus.infrastructure.api.v1.serializers.debate_serializer import DebateSerializer

def send_notification(user, group, notification_type, message, extra_data=None):
    """
    Función auxiliar para crear o actualizar una notificación en la base de datos
    y enviar un mensaje en tiempo real a través de Channels a todos los miembros del grupo.

    :param user: El usuario que genera la notificación.
    :param group: El grupo al que pertenece la notificación.
    :param notification_type: El tipo de notificación (e.g. 'debate_created', 'user_expertise').
    :param message: El mensaje descriptivo de la notificación.
    :param extra_data: Un diccionario opcional con información adicional (ej. debate_id, profile_picture_url).
    """
    if extra_data is None:
        extra_data = {}

    NotificationPhaseOne = apps.get_model('concensus', 'NotificationPhaseOne')

    # Verificar si ya existe una notificación idéntica
    existing_notification = NotificationPhaseOne.objects.filter(
        user=user,
        group=group,
        notification_type=notification_type,
        message=message
    ).first()

    if existing_notification:
        existing_notification.created_at = timezone.now()
        existing_notification.save()
        notification = existing_notification
    else:
        notification = NotificationPhaseOne.objects.create(
            user=user,
            group=group,
            notification_type=notification_type,
            message=message
        )

        # Enviar notificación por WebSocket solo si es nueva
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'group_{group.id}',
            {
                'type': 'group_message',
                'message': {
                    'id': notification.id,
                    'type': notification_type,
                    'user_id': user.id,
                    'group_id': group.id,
                    'notification_message': message,
                    'added_at': notification.created_at.isoformat(),
                    'profile_picture_url': getattr(user.profile_picture, 'url', None),
                }
            }
        )

    return notification


class PostureViewSet(viewsets.ModelViewSet):
    """
    CRUD de posturas de los usuarios.
    Un usuario puede crear o actualizar su postura frente a un debate.
    """
    queryset = UserPosture.objects.all()
    serializer_class = UserPostureSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        Crea una nueva postura para el usuario autenticado y notifica.
        """
        user = request.user
        data = request.data.copy()
        data['user'] = user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        posture = serializer.save()

        # Enviar notificación
        message = f'{user.first_name} {user.last_name} 🎯 has defined its position: “{posture.posture}” in the debate “{posture.debate.title}”.'
        send_notification(
            user=user,
            group=posture.debate.group,
            notification_type='posture_created',
            message=message,
            extra_data={'debate_id': posture.debate.id, 'posture_id': posture.id}
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        Actualiza la postura y envía una notificación si es válida.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # Si el debate está cerrado, devolvemos error:
        if instance.debate.is_closed:
            return Response(
                {"detail": "El debate está cerrado, no se puede cambiar la postura."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Si no está cerrado, entonces procedemos con la actualización.
        data = request.data.copy()
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        posture = serializer.save()

        # Enviar notificación
        user = request.user
        message = f'{user.first_name} {user.last_name} 🔄 has updated its position: “{posture.posture}” in the discussion “{posture.debate.title}”.'
        send_notification(
            user=user,
            group=posture.debate.group,
            notification_type='posture_updated',
            message=message,
            extra_data={'debate_id': posture.debate.id, 'posture_id': posture.id}
        )

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        user_id = kwargs.get('pk')  # pk es el valor del {id} en la URL
        queryset = self.queryset.filter(user__id=user_id)  # Filtra por el ID del usuario
        if not queryset.exists():
            return Response({"detail": "No se encontraron posturas para este usuario."}, status=404)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], url_path='debate/(?P<debate_id>[^/.]+)')
    def get_posture_by_debate(self, request, debate_id=None):
        """
        Devuelve la postura del usuario autenticado para un debate específico.
        """
        user = request.user
        try:
            posture = UserPosture.objects.get(user=user, debate_id=debate_id)
            serializer = self.get_serializer(posture)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserPosture.DoesNotExist:
            return Response(
                {"detail": "El usuario no tiene postura registrada para este debate."},
                status=status.HTTP_404_NOT_FOUND,
            )


