from rest_framework import generics, permissions, status
from rest_framework.response import Response
from apps.custom_auth.domain.entities.user import User
from apps.custom_auth.models import Group
from apps.custom_auth.infrastructure.api.v1.serializers.group_serializer import GroupSerializer , UserGroupSerializer


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

""" class UserGroupsListView(generics.ListAPIView):
    serializer_class = UserGroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Group.objects.filter(users=user) """

""" Vistas para obtener los grupos de un usuario sin autenticar"""
class UserGroupsListView(generics.ListAPIView):
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
    
    
