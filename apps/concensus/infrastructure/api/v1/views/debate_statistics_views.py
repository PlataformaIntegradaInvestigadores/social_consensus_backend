from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.concensus.domain.entities.debate_participant_posture import UserPosture


class StatisticsView(APIView):
    """
    Muestra un conteo simple de cuántos están de acuerdo, en desacuerdo y neutrales,
    para un debate específico.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, debate_id):
        total_agree = UserPosture.objects.filter(
            debate_id=debate_id, posture='agree'
        ).count()
        total_disagree = UserPosture.objects.filter(
            debate_id=debate_id, posture='disagree'
        ).count()
        total_neutral = UserPosture.objects.filter(
            debate_id=debate_id, posture='neutral'
        ).count()

        data = {
            'debate_id': debate_id,
            'total_agree': total_agree,
            'total_disagree': total_disagree,
            'total_neutral': total_neutral,
        }
        return Response(data)

