from rest_framework import serializers
from apps.jobs.domain.entities.jobs import Jobs
from apps.custom_auth.domain.entities.company import Company


class CompanyBasicSerializer(serializers.ModelSerializer):
    """Serializer básico para mostrar información de la compañía en los jobs"""
    class Meta:
        model = Company
        fields = ['id', 'company_name', 'logo', 'industry', 'website', 'address']


class JobsSerializer(serializers.ModelSerializer):
    company_info = CompanyBasicSerializer(source='company', read_only=True)
    status_display = serializers.CharField(source='get_status_display_name', read_only=True)
    experience_display = serializers.CharField(source='get_experience_display_name', read_only=True)
    job_type_display = serializers.CharField(source='get_job_type_display_name', read_only=True)
    applications_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Jobs
        fields = [
            'id', 'title', 'description', 'requirements', 'benefits', 
            'location', 'job_type', 'job_type_display', 'experience_level', 
            'experience_display', 'salary_min', 'salary_max', 'status', 
            'status_display', 'is_remote', 'application_deadline', 
            'created_at', 'updated_at', 'company', 'company_info', 
            'applications_count'
        ]
        extra_kwargs = {
            'company': {'write_only': True},  # Solo para escritura, no se muestra en respuesta
        }
    
    def get_applications_count(self, obj):
        """Retorna el número de postulaciones para este trabajo"""
        return obj.applications.count()
    
    def validate(self, data):
        """Validaciones personalizadas"""
        salary_min = data.get('salary_min')
        salary_max = data.get('salary_max')
        
        if salary_min and salary_max and salary_min > salary_max:
            raise serializers.ValidationError("El salario mínimo no puede ser mayor al salario máximo")
        
        return data


class JobsListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados de jobs"""
    company_info = CompanyBasicSerializer(source='company', read_only=True)
    status_display = serializers.CharField(source='get_status_display_name', read_only=True)
    job_type_display = serializers.CharField(source='get_job_type_display_name', read_only=True)
    
    class Meta:
        model = Jobs
        fields = [
            'id', 'title', 'location', 'job_type', 'job_type_display', 
            'experience_level', 'salary_min', 'salary_max', 'status', 
            'status_display', 'is_remote', 'created_at', 'company_info'
        ]
