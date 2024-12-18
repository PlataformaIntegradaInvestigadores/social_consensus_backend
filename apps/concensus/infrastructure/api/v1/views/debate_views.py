from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets

from apps.concensus.domain.entities.debate import Debate
from apps.concensus.domain.entities.debate_participant import DebateParticipant
from apps.custom_auth.domain.entities.group import Group
from apps.custom_auth.domain.entities.group import GroupUser
from apps.concensus.infrastructure.api.v1.serializers.debate_serializer import DebateSerializer


def notify_group(group_id, message):
    """
    Envía un mensaje al grupo de canales asociado al 'group_id'.
    Se asume que existe un consumer suscrito a 'group_{group_id}'.
    """
    # Obtenemos la capa de canales (channel layer) configurada.
    layer = get_channel_layer()
    # Definimos el nombre del canal de grupo: 'group_{group_id}'
    group_name = f"group_{group_id}"
    # Enviamos el mensaje al grupo.
    # Este mensaje será recibido por el Consumer correspondiente.
    async_to_sync(layer.group_send)(
        group_name,
        {
            "type": "group.message",  # 'type' indica el tipo de evento que manejará el consumer
            "message": message        # 'message' es el contenido enviado a los clientes
        }
    )


class DebateViewSet(viewsets.ModelViewSet):
    queryset = Debate.objects.all()
    serializer_class = DebateSerializer
    # permission_classes = [IsAuthenticated] # Descomentar para requerir autenticación

    def get_serializer_context(self):
        """
        Agregar el grupo al contexto del serializador para validaciones.
        """
        group_id = self.kwargs.get("group_id")
        group = Group.objects.filter(id=group_id).first()

        if not group:
            raise ValidationError({"detail": "El grupo especificado no existe."})

        context = super().get_serializer_context()
        context["group"] = group  # Agrega el grupo al contexto
        return context
    def get_queryset(self):
        """
        Filtra los debates por grupo.
        """
        group = self.get_serializer_context()["group"]
        return Debate.objects.filter(group=group)

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
        debate = self.get_object()  # Obtiene la instancia de debate basado en 'pk'
        try:
            self.validate_debate_status(debate)  # Valida el estado del debate
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

        #Verificar si el grupo ya tiene un debate activo
        active_debate_exists = Debate.objects.filter(group=group, is_closed=False).exists()
        if active_debate_exists:
            raise ValidationError({"detail": "Este grupo ya tiene un debate activo."})

        serializer = self.get_serializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        # Guardar el debate
        debate = serializer.save(group=group)

        # Obtener los IDs de los usuarios que pertenecen al grupo
        group_users = GroupUser.objects.filter(group=context["group"]).values_list("user", flat=True)

        # Insertar participantes si no existen ya en la tabla
        for user_id in group_users:
            DebateParticipant.objects.get_or_create(
                debate=debate, participant_id=user_id
            )

        # Notificar a los usuarios del grupo sobre el nuevo debate
        notify_group(group.id, f"Se ha creado un nuevo debate: '{debate.title}'")

        return Response(self.get_serializer(debate).data, status=status.HTTP_201_CREATED)

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
        Recupera un debate específico por su ID dentro de un grupo.
        """
        context = self.get_serializer_context()
        debate_id = kwargs.get("pk")
        debate = Debate.objects.filter(id=debate_id, group=context["group"]).first()

        if not debate:
            raise ValidationError({"detail": "El debate no existe en este grupo."})

        self.validate_debate_status(debate)  # Valida que el debate esté abierto

        serializer = self.get_serializer(debate)
        return Response(serializer.data)

    def close(self, _request, *_args, **kwargs):
        """
        Cierra un debate activo manualmente.
        """
        context = self.get_serializer_context()
        debate_id = kwargs.get("pk")
        debate = Debate.objects.filter(id=debate_id, group=context["group"]).first()

        if not debate:
            raise ValidationError({"detail": "El debate no existe en este grupo."})

        if debate.is_closed:
            raise ValidationError({"detail": "El debate ya está cerrado."})

        # Cerrar el debate
        debate.is_closed = True
        debate.save()

        return Response({"detail": f"El debate '{debate.title}' ha sido cerrado."}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        Solo el administrador del grupo puede eliminar el debate.
        Ahora el admin es el usuario en 'group.id_admin'.
        """
        debate = self.get_object()
        if debate.group.id_admin != request.user:
            raise PermissionDenied({"detail": "No tienes permisos para eliminar este debate."})

        title = debate.title
        debate.delete()
        return Response({"detail": f"El debate '{title}' ha sido eliminado."}, status=status.HTTP_204_NO_CONTENT)
