import logging
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from apps.concensus.domain.entities.user_phase import UserPhase
from apps.concensus.infrastructure.api.v1.serializers.user_phase_serializer import UserPhaseSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample, OpenApiRequest
from django.utils import timezone
from apps.custom_auth.domain.entities.group import Group

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)

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

# TODO: Add OpenAPI documentation
class UpdateGroupPhaseView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserPhaseSerializer

    @extend_schema(
        summary="Update the phase of all users in a group.",
        description=(
                "Update the phase of all users in a group to the phase specified in the request. "
                "The phase must be an integer in the range from 0 to 2."
        ),
        request=OpenApiRequest(
            examples=[
                OpenApiExample(
                    name="Update the phase of all users in a group to phase 1.",
                    value={"phase": 1}
                )
            ]
        ),
        responses={
            200: OpenApiResponse(
                description="User phases updated successfully.",
                response=Response,
                examples=[
                    OpenApiExample(
                        name="User phases updated successfully.",
                        value={
                            "response": [
                                {
                                    "user": "FuAYWrO2YP",
                                    "group": "SjkocmB41m",
                                    "phase": 1,
                                    "completed_at": "2024-12-17T03:01:35.344689Z"
                                },
                                {
                                    "user": "FHpJSp6Xnh",
                                    "group": "SjkocmB41m",
                                    "phase": 1,
                                    "completed_at": "2024-12-17T03:01:35.344689Z"
                                }
                            ]
                        }
                    )
                ]
            ),
            404: OpenApiResponse(
                description="No user phases found for this group.",
                response=Response,
                examples=[
                    OpenApiExample(
                        name="No user phases found for this group.",
                        summary="No user phases found for this group.",
                        value={"detail": "No user phases found for this group."},
                    ),
                    OpenApiExample(
                        name="Group not found.",
                        summary="Group not found.",
                        value={"detail": "Group not found."}
                    )
                ]
            ),
            403: OpenApiResponse(
                description="You do not have permission to update this group.",
                response=Response,
                examples=[
                    OpenApiExample(
                        name="You do not have permission to update this group.",
                        summary="You do not have permission to update this group.",
                        value={"detail": "You do not have permission to update this group."}
                    )
                ]
            ),
        }
    )
    def post(self, request, group_id):
        user = request.user
        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            return Response({'detail': 'Group not found.'}, status=status.HTTP_404_NOT_FOUND)

        phase = request.data.get('phase')

        if group.admin != user:
            return Response({'detail': 'You do not have permission to update this group.'},
                            status=status.HTTP_403_FORBIDDEN)

        user_phases = UserPhase.objects.filter(group=group)

        if not user_phases.exists():
            return Response({'detail': 'No user phases found for this group.'}, status=status.HTTP_404_NOT_FOUND)

        user_phases.update(phase=phase, completed_at=timezone.now())

        updated_user_phases = UserPhase.objects.filter(group=group)
        serializer = self.get_serializer(updated_user_phases, many=True)

        # Send WebSocket notification
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(f'phase3_group_{group_id}', {
            'type': 'group_message',
            'message': {
                'type': 'phase_update',
                'phase': phase,
            }
        })

        logger.info(f'Websocket message sent to group {group_id} to update phase to {phase}')

        return Response(serializer.data, status=status.HTTP_200_OK)
