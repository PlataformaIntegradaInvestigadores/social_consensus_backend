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
        if value and not value.startswith(('http://', 'https://')):
            value = 'http://' + value
        return value

    def update(self, instance, validated_data):
        print("Datos validados recibidos en el serializador:", validated_data)
        profile_picture = validated_data.pop('profile_picture', None)
        if profile_picture:
            print("Nueva imagen de perfil:", profile_picture)
            if profile_picture != instance.profile_picture:
                instance.profile_picture.delete(save=False)
            instance.profile_picture = profile_picture
        instance = super().update(instance, validated_data)
        print("Instancia después de actualizar:", instance)
        return instance


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
