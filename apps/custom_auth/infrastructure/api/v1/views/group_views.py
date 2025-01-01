from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from apps.concensus.domain.entities.topic import RecommendedTopic, TopicAddedUser
from apps.custom_auth.domain.entities.user import User
from apps.custom_auth.infrastructure.api.v1.serializers.user_serializer import UserListSerializer
from apps.custom_auth.models import Group
from apps.custom_auth.infrastructure.api.v1.serializers.group_serializer import GroupDetailSerializer, GroupSerializer , UserGroupSerializer
from rest_framework.exceptions import PermissionDenied
from apps.concensus.domain.entities.user_phase import UserPhase

class GroupListCreateView(generics.ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """Asigna el usuario actual como administrador al crear un nuevo grupo."""
        serializer.save(admin=self.request.user)

    def create(self, request, *args, **kwargs):
        """Maneja la creación de un nuevo grupo."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

""" Para listar los grupos de un usuario autenticado """
class UserGroupsListView(generics.ListAPIView):
    serializer_class = UserGroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Filtrar los grupos por el usuario autenticado y ordenar por 'id' en orden descendente
        return Group.objects.filter(users=user)

""" Para borrar un grupo"""
class GroupDeleteView(generics.DestroyAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        group = self.get_object()
        if group.admin != request.user:
            return Response({'detail': 'You do not have permission to delete this group.'}, status=status.HTTP_403_FORBIDDEN)

        # Obtener los topics agregados por los usuarios del grupo
        added_topic_ids = TopicAddedUser.objects.filter(group=group).values_list('topic_id', flat=True)

        # Borrar los registros de RecommendedTopic correspondientes
        RecommendedTopic.objects.filter(id__in=added_topic_ids).delete()

        # Actualizar los registros restantes de RecommendedTopic para establecer el campo group a NULL
        RecommendedTopic.objects.filter(group=group).update(group=None)
        
        return self.destroy(request, *args, **kwargs)
    
""" Para dejar un grupo """
class GroupLeaveView(generics.GenericAPIView):
    queryset = Group.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        group = self.get_object()
        if request.user == group.admin:
            return Response({'detail': 'Admin cannot leave the group. You must delete the group.'}, status=status.HTTP_400_BAD_REQUEST)
        group.users.remove(request.user)
        return Response({'detail': 'You have left the group.'}, status=status.HTTP_200_OK)

""" Para obtener los datos del propietario de un grupo """
class UserDetailViewtoGroup(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated]


""" Vistas para obtener los grupos de un usuario sin autenticar"""
""" class UserGroupsListView(generics.ListAPIView):
    serializer_class = UserGroupSerializer
    permission_classes = [permissions.AllowAny]  # Permitir acceso a cualquier usuario temporalmente

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        print(f"User ID: {user_id}")  # Mensaje de depuración
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                print(f"User found: {user}")  # Mensaje de depuración
                return Group.objects.filter(users=user)
            except User.DoesNotExist:
                print("User does not exist")  # Mensaje de depuración
                return Group.objects.none()
        print("No user ID provided")  # Mensaje de depuración
        return Group.objects.none()

     """

class GroupDetailView(generics.RetrieveAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        group = self.get_object()
        user = request.user

        # Verificar si el usuario es el propietario o un miembro del grupo
        if group.admin == user or group.users.filter(id=user.id).exists():
            serializer = self.get_serializer(group)
            return Response(serializer.data)
        else:
            raise PermissionDenied("You do not have permission to access this group.")


""" para eliminar un miembro en base a su id, solo si esta autenticado y es propietario del grupo """
# TODO: Api documentation
class RemoveMemberView(generics.GenericAPIView):
    queryset = Group.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary='Remove a member from the group',
        description=(
            'Remove a member from the group. Only the group owner can remove a member.'
        ),
        responses={
            200: OpenApiResponse(
                description='Member removed successfully.',
                response=Response,
                examples=[
                    OpenApiExample(
                        name='Member removed successfully',
                        value={'detail': 'Member removed successfully.'}
                    )
                ]
            ),
            400: OpenApiResponse(
                description='You cannot remove yourself from the group.',
                response=Response,
                examples=[
                    OpenApiExample(
                        name='You cannot remove yourself from the group',
                        value={'detail': 'You cannot remove yourself from the group.'}
                    )
                ]
            ),
            403: OpenApiResponse(
                description='You do not have permission to remove this member.',
                response=Response,
                examples=[
                    OpenApiExample(
                        name='You do not have permission to remove this member',
                        value={'detail': 'You do not have permission to remove this member.'}
                    )
                ]
            ),
            404: OpenApiResponse(
                description='User does not exist.',
                response=Response,
                examples=[
                    OpenApiExample(
                        name='User does not exist',
                        value={'detail': 'User does not exist.'}
                    )
                ]
            )
        }
    )
    def delete(self, request, *args, **kwargs):
        group = self.get_object()
        user_id = self.kwargs.get('user_id')
        try:
            user_to_remove = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'detail': 'User does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        if group.admin != request.user:
            return Response({'detail': 'You do not have permission to remove this member.'}, status=status.HTTP_403_FORBIDDEN)

        if user_to_remove == request.user:
            return Response({'detail': 'You cannot remove yourself from the group.'}, status=status.HTTP_400_BAD_REQUEST)

        # Eliminar al usuario de los UserPhase asociados al grupo
        user_phase = UserPhase.objects.filter(user=user_to_remove, group=group.id)
        if user_phase.exists():
            user_phase.delete()

        # Eliminar al usuario del grupo
        group.users.remove(user_to_remove)

        # Send WebSocket notification
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(f'phase3_group_{group.id}', {
            'type': 'group_message',
            'message': {
                'type': 'remove_member',
                'user_id': user_to_remove.id,
                'message': f'{user_to_remove.username} has been removed from the group.'
            }
        })

        return Response({'detail': 'Member removed successfully.'}, status=status.HTTP_200_OK)