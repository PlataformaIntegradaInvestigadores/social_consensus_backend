import pytz
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


class DebateViewSet(viewsets.ModelViewSet):
    queryset = Debate.objects.all()
    serializer_class = DebateSerializer
    permission_classes = [IsAuthenticated]

    def initial(self, request, *args, **kwargs):
        """
        Activa una zona horaria específica para toda la vista.
        """
        super().initial(request, *args, **kwargs)

        # Aquí obtendremos la zona horaria del usuario. Si no tiene, usamos 'UTC'.
        user_timezone = getattr(request.user, 'timezone', None) or 'UTC'

        # Activar la zona horaria utilizando pytz.
        timezone.activate(pytz.timezone(user_timezone))

    def finalize_response(self, request, response, *args, **kwargs):
        """
        Resetea la zona horaria al finalizar.
        """
        timezone.deactivate()
        return super().finalize_response(request, response, *args, **kwargs)

    def get_serializer_context(self):
        """
        Agregar el grupo al contexto del serializador para validaciones.
        """
        group_id = self.kwargs.get("group_id")
        group = Group.objects.filter(id=group_id).first()

        if not group:
            raise ValidationError({"detail": "El grupo especificado no existe."})

        context = super().get_serializer_context()
        context["group"] = group
        return context

    def get_queryset(self):
        """
        Filtra los debates por grupo y cierra automáticamente los expirados.
        """
        group_id = self.kwargs.get("group_id")
        queryset = Debate.objects.filter(group_id=group_id)

        for debate in queryset.filter(is_closed=False):
            if debate.is_time_exceeded():
                debate.is_closed = True
                debate.save()

        return queryset

    @staticmethod
    def validate_debate_status(debate_instance):
        """
        Valida si el debate está abierto.
        Lanza una excepción si el debate está cerrado.
        """
        if debate_instance.is_closed:
            raise ValidationError({"detail": "El debate está cerrado y no se pueden realizar más acciones."})

    @action(detail=True, methods=['get'], url_path='validate-status')
    def validate_status(self, _request, *_args, **_kwargs):
        """
        Valida el estado de un debate específico (abierto o cerrado).
        """
        debate = self.get_object()
        try:
            self.validate_debate_status(debate)
            return Response({"detail": "El debate está abierto."}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        """
        Crea un debate y registra automáticamente a los participantes que pertenecen al grupo.
        Evita agregar participantes duplicados.
        """
        context = self.get_serializer_context()
        group = context["group"]

        # Verificar si el grupo ya tiene un debate activo
        active_debate_exists = Debate.objects.filter(group=group, is_closed=False).exists()
        if active_debate_exists:
            raise ValidationError({"detail": "Este grupo ya tiene un debate activo."})

        # Validar y guardar el debate
        serializer = self.get_serializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        debate = serializer.save(group=group)

        # Validar que end_time sea mayor a 0
        # end_time = serializer.validated_data.get('end_time')
        # if end_time.total_seconds() <= 0:
        #     raise ValidationError({"detail": "La duración debe ser mayor a 0."})

        # Registrar participantes en el debate
        group_users = GroupUser.objects.filter(group=group).values_list("user", flat=True)
        for user_id in group_users:
            DebateParticipant.objects.get_or_create(debate=debate, participant_id=user_id)

        # Usuario que inicia el debate
        user = request.user
        message = f'{user.first_name} {user.last_name} 🗣️  started a new discussion: <i>{debate.title}</i>'

        # Enviar la notificación del debate
        send_notification(
            user=user,
            group=group,
            notification_type='debate_created',
            message=message,
            extra_data={'debate_id': debate.id}
        )

        # Preparar la respuesta correcta (con los datos del debate)
        response_data = {
            "id": debate.id,
            "title": debate.title,
            "description": debate.description,
            "is_closed": debate.is_closed,
            "created_at": debate.created_at.isoformat(),
            "group_id": debate.group.id,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        """
        Lista todos los debates del grupo y actualiza el estado si alguno expiró.
        """
        context = self.get_serializer_context()
        queryset = Debate.objects.filter(group=context["group"])
        serializer = self.get_serializer(queryset, many=True, context=context)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """
        Recupera un debate específico.
        Cierra automáticamente si el tiempo ha expirado.
        """
        debate = self.get_object()

        # Verificar si el tiempo del debate ha expirado
        if not debate.is_closed and debate.is_time_exceeded():
            debate.is_closed = True
            debate.save()

        serializer = self.get_serializer(debate)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='close')
    def close(self, request, *args, **kwargs):
        """
        Permite cerrar un debate manualmente y envía una notificación.
        """
        # Obtener el debate de forma robusta
        debate = self.get_object()

        # Verificar si el usuario tiene permiso para cerrar el debate
        if request.user != debate.group.admin:
            raise PermissionDenied({"detail": "No tienes permisos para cerrar este debate."})

        # Validar si el debate ya está cerrado
        if debate.is_closed:
            return Response({"detail": "El debate ya está cerrado."}, status=status.HTTP_400_BAD_REQUEST)

        # Cerrar el debate
        debate.is_closed = True
        debate.save()

        # Enviar una notificación de cierre
        user = request.user
        message = f'{user.first_name} {user.last_name} 🔒 Close the debate: <i>{debate.title}</i>'

        send_notification(
            user=user,
            group=debate.group,
            notification_type='debate_closed',
            message=message,
            extra_data={'debate_id': debate.id}
        )

        return Response({
                            "detail": f"El debate '{debate.title}' ha sido cerrado manualmente y se ha notificado a los participantes."},
                        status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        debate = self.get_object()
        print(f"Request User: {request.user}")
        print(f"Group Admin: {debate.group.admin}")
        if debate.group.admin != request.user:
            raise PermissionDenied({"detail": "No tienes permisos para eliminar este debate."})

        title = debate.title
        debate.delete()
        return Response({"detail": f"El debate '{title}' ha sido eliminado."}, status=status.HTTP_204_NO_CONTENT)
