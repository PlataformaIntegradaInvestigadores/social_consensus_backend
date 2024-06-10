from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import User, Group
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

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


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username']


class UserTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['user_id'] = user.id
        return token


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'scopus_id', 'institution',
                  'website', 'investigation_camp', 'profile_picture', 'email_institution']

    def validate_website(self, value):
        if value and not value.startswith(('http://', 'https://')):
            value = 'http://' + value
        return value


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name',
                  'username', 'scopus_id', 'password']

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
