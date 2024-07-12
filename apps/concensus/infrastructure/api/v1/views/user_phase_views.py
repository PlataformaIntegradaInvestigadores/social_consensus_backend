from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.response import Response
from apps.concensus.domain.entities.user_phase import UserPhase
from apps.concensus.infrastructure.api.v1.serializers.user_phase_serializer import UserPhaseSerializer

class UserCurrentPhaseView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserPhaseSerializer

    def get(self, request, group_id):
        user = request.user
        try:
            user_phase = UserPhase.objects.get(user=user, group_id=group_id)
            serializer = self.get_serializer(user_phase)
            return Response(serializer.data)
        except UserPhase.DoesNotExist:
            # Devuelve una fase por defecto (0) si no se encuentra el objeto
            return Response({"phase": 0})