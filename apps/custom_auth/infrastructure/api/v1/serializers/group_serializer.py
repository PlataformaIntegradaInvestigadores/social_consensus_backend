from rest_framework import serializers
from apps.custom_auth.models import Group, User


class GroupSerializer(serializers.ModelSerializer):
    users = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, required=False)

    class Meta:
        model = Group
        fields = ['id', 'title', 'description', 'admin', 'users']
        read_only_fields = ['id', 'admin']

    def create(self, validated_data):
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
        fields = ['id', 'title', 'description']
        read_only_fields = ['id', 'title', 'description']