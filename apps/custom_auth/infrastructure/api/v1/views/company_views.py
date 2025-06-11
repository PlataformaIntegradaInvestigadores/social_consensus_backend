from django.forms import ValidationError
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.views import TokenObtainPairView
from ..serializers.company_serializer import (
    CompanyListSerializer, 
    CompanySerializer, 
    CompanyRegisterSerializer, 
    CompanyTokenObtainPairSerializer,
    CompanyProfileSerializer
)
from apps.custom_auth.models import Company


class CompanyListView(generics.ListAPIView):
    """Lista todas las empresas (para administradores o uso interno)."""
    serializer_class = CompanyListSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Company.objects.filter(is_active=True)

    def get_queryset(self):
        """Filtra las empresas activas y verificadas."""
        queryset = super().get_queryset()
        # Opcionalmente, solo mostrar empresas verificadas
        if self.request.query_params.get('verified_only', '').lower() == 'true':
            queryset = queryset.filter(is_verified=True)
        return queryset


class CompanyUpdateView(generics.UpdateAPIView):
    """Permite a una empresa actualizar su perfil."""
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get_object(self):
        """Asegura que solo la empresa puede editar su propio perfil."""
        obj = super().get_object()
        if obj.id != self.request.user.id:
            raise PermissionDenied(
                "No tienes permiso para editar esta empresa.")
        return obj

    def update(self, request, *args, **kwargs):
        """Actualiza el perfil de la empresa."""
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class CompanyTokenObtainPairView(TokenObtainPairView):
    """Vista de autenticación JWT para empresas."""
    serializer_class = CompanyTokenObtainPairSerializer


class CompanyDetailView(generics.RetrieveAPIView):
    """Obtiene los detalles de una empresa específica."""
    queryset = Company.objects.filter(is_active=True)
    serializer_class = CompanyProfileSerializer
    permission_classes = [permissions.IsAuthenticated]


class CompanyProfileView(generics.RetrieveAPIView):
    """Obtiene el perfil de la empresa autenticada."""
    serializer_class = CompanyProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retorna la empresa autenticada."""
        return self.request.user


class CompanyRegisterView(generics.CreateAPIView):
    """Registro de nuevas empresas."""
    queryset = Company.objects.all()
    serializer_class = CompanyRegisterSerializer

    def create(self, request, *args, **kwargs):
        """Crea una nueva empresa y maneja los errores de validación."""
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            
            # Respuesta de éxito sin datos sensibles
            response_data = {
                'message': 'Empresa registrada exitosamente',
                'company_name': serializer.instance.company_name,
                'username': serializer.instance.username,
                'industry': serializer.instance.get_industry_display_name()
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)
            
        except ValidationError as e:
            return Response(self.format_errors(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def format_errors(self, errors):
        """Formatea los errores de validación personalizados."""
        custom_errors = {}
        for field, field_errors in errors.items():
            custom_errors[field] = [self.get_custom_error_message(
                field, error) for error in field_errors]
        return {'errors': custom_errors}

    def get_custom_error_message(self, field, error):
        """Obtiene mensajes de error personalizados."""
        custom_messages = {
            'username': {
                'company with this username already exists.': "Ya existe una empresa con este correo electrónico.",
                'Enter a valid email address.': "Ingresa una dirección de correo electrónico válida."
            },
            'company_name': {
                'This field may not be blank.': "El nombre de la empresa es requerido."
            },
            'password': {
                'This field may not be blank.': "La contraseña es requerida.",
                'Ensure this field has at least 8 characters.': "La contraseña debe tener al menos 8 caracteres."
            }
        }
        return custom_messages.get(field, {}).get(error, error)
