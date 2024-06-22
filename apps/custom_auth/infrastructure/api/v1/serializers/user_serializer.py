from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from apps.custom_auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username']


class UserTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        """Agrega el ID del usuario al token."""
        token = super().get_token(user)
        token['user_id'] = user.id
        return token


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'scopus_id', 'institution',
                  'website', 'investigation_camp', 'profile_picture', 'email_institution']

    def validate_website(self, value):
        """Valida y ajusta la URL del sitio web."""
        if value and not value.startswith(('http://', 'https://')):
            value = 'http://' + value
        return value

    def update(self, instance, validated_data):
        profile_picture = validated_data.get(
            'profile_picture', instance.profile_picture)

        if isinstance(profile_picture, str) and profile_picture == instance.profile_picture.url:
            validated_data['profile_picture'] = instance.profile_picture

        return super().update(instance, validated_data)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name',
                  'username', 'scopus_id', 'password']

    def create(self, validated_data):
        """Crea un nuevo usuario y encripta su contraseña."""
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
