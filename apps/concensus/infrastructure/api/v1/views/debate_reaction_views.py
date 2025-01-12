from rest_framework import mixins, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.concensus.domain.entities.debate_reaction import Reaction
from apps.concensus.infrastructure.api.v1.serializers.debate_reaction_serializer import ReactionSerializer


class ReactionViewSet(mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    """
    Permite dar 'Me gusta' (reacción) a un mensaje o quitarla.
    - POST -> crea una reacción
    - DELETE -> elimina la reacción (si es del mismo usuario)
    """
    queryset = Reaction.objects.all()
    serializer_class = ReactionSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data.copy()
        data['user'] = user.id  # Asociación con el usuario logueado
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Solo el mismo usuario que hizo la reacción puede borrarla
        if instance.user == request.user:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {"detail": "No tienes permiso para eliminar esta reacción."},
                status=status.HTTP_403_FORBIDDEN
            )
