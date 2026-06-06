from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from apps.jobs.domain.entities.company import Company
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CompanyListSerializer(serializers.ModelSerializer):
    industry_display = serializers.CharField(source='get_industry_display_name', read_only=True)
    
    class Meta:
        model = Company
        fields = ['id', 'company_name', 'username', 'industry', 'industry_display', 'is_verified']


class CompanyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        """Valida las credenciales de la empresa."""
        username = attrs.get('username')
        password = attrs.get('password')
        
        # Buscar la empresa por username
        try:
            company = Company.objects.get(username=username)
        except Company.DoesNotExist:
            raise serializers.ValidationError('No active account found with the given credentials')
        
        # Verificar la contraseña
        if not company.check_password(password):
            raise serializers.ValidationError('No active account found with the given credentials')
        
        # Verificar que la empresa esté activa
        if not company.is_active:
            raise serializers.ValidationError('User account is disabled.')
        
        # Crear los tokens
        refresh = self.get_token(company)
        
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'company_id': company.id,
            'user_type': 'company'
        }
    
    @classmethod
    def get_token(cls, company):
        """Agrega el ID de la empresa al token."""
        token = super().get_token(company)
        token['company_id'] = company.id
        token['user_type'] = 'company'
        return token


class CompanySerializer(serializers.ModelSerializer):
    industry_display = serializers.CharField(source='get_industry_display_name', read_only=True)
    
    class Meta:
        model = Company
        fields = [
            'company_name', 'industry', 'industry_display', 'description', 
            'website', 'phone', 'address', 'logo', 'founded_year', 
            'employee_count', 'is_verified'
        ]

    def validate_website(self, value):
        if value and not value.startswith(('http://', 'https://')):
            value = 'http://' + value
        return value

    def update(self, instance, validated_data):
        logo = validated_data.pop('logo', None)
        if logo:
            # Eliminar logo anterior si no es el por defecto
            default_logo = 'company_logos/default_company_logo.png'
            if logo != instance.logo and str(instance.logo) != default_logo:
                instance.logo.delete(save=False)
            instance.logo = logo
        
        return super().update(instance, validated_data)


class CompanyRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = Company
        fields = [
            'company_name', 'username', 'password', 'confirm_password', 
            'industry', 'description', 'website', 'phone'
        ]

    def validate(self, attrs):
        """Valida que las contraseñas coincidan."""
        password = attrs.get('password')
        confirm_password = attrs.pop('confirm_password', None)
        
        if password != confirm_password:
            raise serializers.ValidationError("Las contraseñas no coinciden.")
        
        return attrs

    def validate_company_name(self, value):
        """Valida que el nombre de la empresa no esté vacío."""
        if not value or value.strip() == '':
            raise serializers.ValidationError("El nombre de la empresa es requerido.")
        return value.strip()

    def create(self, validated_data):
        """Crea una nueva empresa y encripta su contraseña."""
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


class CompanyProfileSerializer(serializers.ModelSerializer):
    """Serializador para mostrar el perfil completo de la empresa."""
    industry_display = serializers.CharField(source='get_industry_display_name', read_only=True)
    
    class Meta:
        model = Company
        fields = [
            'id', 'company_name', 'username', 'industry', 'industry_display',
            'description', 'website', 'phone', 'address', 'logo', 
            'founded_year', 'employee_count', 'is_verified', 'date_joined'
        ]
        read_only_fields = ['id', 'username', 'is_verified', 'date_joined']
