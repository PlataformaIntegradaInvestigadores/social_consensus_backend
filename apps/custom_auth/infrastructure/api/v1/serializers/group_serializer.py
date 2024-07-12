from rest_framework import serializers
from apps.custom_auth.models import Group, User


class GroupSerializer(serializers.ModelSerializer):
    users = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, required=False)

    class Meta:
        model = Group
        fields = ['id', 'title', 'description', 'admin_id', 'users']
        read_only_fields = ['id', 'admin']

    def create(self, validated_data):
        """Crea un nuevo grupo y asigna el usuario actual como administrador y miembro."""
        request = self.context.get('request')
        validated_data['admin'] = request.user
        users = validated_data.pop('users', [])

        # Crear el grupo con los datos validados
        group = Group.objects.create(**validated_data)

        # Agregar al creador del grupo como miembro
        group.users.add(request.user)

        # Agregar cualquier otro usuario proporcionado
        group.users.add(*users)

        return group
    
# Nuevo serializador para listar grupos del usuario autenticado
class UserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'title', 'description','admin_id', 'users']
        read_only_fields = ['id', 'title', 'description','admin_id', 'users']

""" Para consensus recuperar info del grupo y miembros """
class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'scopus_id', 'investigation_camp', 'institution', 'email_institution', 'website', 'profile_picture', 'is_active', 'is_staff']

class GroupDetailSerializer(serializers.ModelSerializer):
    users = UserDetailSerializer(many=True, read_only=True)  # Incluir los detalles de los miembros del grupo

    class Meta:
        model = Group
        fields = ['id', 'title', 'description', 'admin_id', 'users']
        read_only_fields = ['id', 'admin_id']