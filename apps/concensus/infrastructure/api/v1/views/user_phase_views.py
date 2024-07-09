from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db.models import Max

from apps.concensus.domain.entities.user_phase import UserPhase
from apps.concensus.infrastructure.api.v1.serializers.user_phase_serializer import UserPhaseSerializer
from apps.custom_auth.domain.entities.group import Group
from apps.custom_auth.domain.entities.user import User


class UpdatePhaseView(APIView):
    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        group_id = request.data.get('group_id')
        phase = request.data.get('phase')

        if not user_id or not group_id or phase is None:
            return Response({'error': 'Missing parameters'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
            group = Group.objects.get(id=group_id)
        except User.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response({"error": "Group does not exist"}, status=status.HTTP_404_NOT_FOUND)

        # Actualizar o crear el registro de fase del usuario
        user_phase, created = UserPhase.objects.get_or_create(user=user, group=group)
        user_phase.phase = phase
        user_phase.completed_at = timezone.now() if phase in [2, 3] else None
        user_phase.save()

        # Verificar si todos los usuarios han completado la fase actual
        all_completed = self.check_all_users_completed_phase(group_id, phase)

        if all_completed:
            # Ejecutar el código necesario para la fase completada
            self.trigger_phase_completion_logic(group_id, phase)

        serializer = UserPhaseSerializer(user_phase)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def check_all_users_completed_phase(self, group_id, phase):
        # Obtener todos los usuarios del grupo
        group_users = UserPhase.objects.filter(group_id=group_id)
        # Verificar si todos los usuarios han completado la fase actual
        return all(user_phase.phase >= phase for user_phase in group_users)

    def trigger_phase_completion_logic(self, group_id, phase):
        # Lógica para ejecutar cuando todos los usuarios completan la fase
        if phase == 2:
            self.perform_calculations_for_phase_two(group_id)
        elif phase == 3:
            self.perform_calculations_for_phase_three(group_id)

    def perform_calculations_for_phase_two(self, group_id):
        # Lógica personalizada para la fase 2
        pass

    def perform_calculations_for_phase_three(self, group_id):
        # Lógica personalizada para la fase 3
        pass

    