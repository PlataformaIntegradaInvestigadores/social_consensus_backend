from rest_framework import serializers
from apps.jobs.domain.entities.postulants import Postulants
from apps.jobs.domain.entities.jobs import Jobs
from apps.custom_auth.domain.entities.user import User


class UserBasicSerializer(serializers.ModelSerializer):
    """Serializer básico para mostrar información del usuario"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'full_name', 'email', 'profile_picture']


class JobBasicSerializer(serializers.ModelSerializer):
    """Serializer básico para mostrar información del trabajo"""
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    
    class Meta:
        model = Jobs
        fields = ['id', 'title', 'company_name', 'location', 'job_type', 'experience_level']


class PostulantsSerializer(serializers.ModelSerializer):
    user_info = UserBasicSerializer(source='user', read_only=True)
    job_info = JobBasicSerializer(source='job', read_only=True)
    status_display = serializers.CharField(source='get_status_display_name', read_only=True)
    
    class Meta:
        model = Postulants
        fields = [
            'id', 'user', 'job', 'cover_letter', 'resume_file', 'status', 
            'status_display', 'notes', 'applied_at', 'updated_at', 
            'user_info', 'job_info'
        ]
        extra_kwargs = {
            'user': {'write_only': True},
            'job': {'write_only': True},
            'notes': {'read_only': True},  # Solo las compañías pueden escribir notas
        }
    
    def create(self, validated_data):
        """Crear una nueva postulación"""
        # El usuario y job se asignan en la vista
        return super().create(validated_data)


class PostulantsListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados de postulaciones"""
    user_info = UserBasicSerializer(source='user', read_only=True)
    job_info = JobBasicSerializer(source='job', read_only=True)
    status_display = serializers.CharField(source='get_status_display_name', read_only=True)
    
    class Meta:
        model = Postulants
        fields = [
            'id', 'status', 'status_display', 'applied_at', 
            'user_info', 'job_info'
        ]


class PostulantsUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualización de postulaciones por parte de las compañías"""
    
    class Meta:
        model = Postulants
        fields = ['status', 'notes']
    
    def validate_status(self, value):
        """Validar que el estado sea válido"""
        valid_statuses = [choice[0] for choice in Postulants.STATUS_CHOICES]
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Estado inválido. Opciones válidas: {valid_statuses}")
        return value
