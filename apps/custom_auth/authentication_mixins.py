from rest_framework.authentication import BaseAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from apps.custom_auth.identity_principal import principal_from_token
from apps.jobs.domain.entities.company import Company


class OptionalJWTAuthentication(JWTAuthentication):
    """
    Autenticación JWT opcional que no falla si el token es inválido.
    Útil para endpoints que pueden funcionar con o sin autenticación.
    """
    
    def authenticate(self, request):
        """
        Intenta autenticar con JWT, pero si falla, retorna None
        en lugar de lanzar una excepción.
        """
        try:
            return super().authenticate(request)
        except (InvalidToken, TokenError):
            return None
    
    def get_user(self, validated_token):
        """
        Obtiene el usuario o empresa basándose en el token validado.
        """
        try:
            # Verificar si el token contiene company_id (empresa)
            if 'company_id' in validated_token:
                company_id = validated_token['company_id']
                try:
                    company = Company.objects.get(id=company_id)
                    if company.is_active:
                        return company
                except Company.DoesNotExist:
                    pass
            
            # Verificar si el token contiene user_id (investigador)
            else:
                principal = principal_from_token(validated_token)
                if principal:
                    return principal
            
            # Si no se encuentra ni usuario ni empresa, lanzar excepción
            raise InvalidToken('No valid user found')
            
        except (KeyError, ValueError):
            raise InvalidToken('Invalid token format')


class NoAuthenticationRequired(BaseAuthentication):
    """
    Clase de autenticación que siempre retorna None,
    efectivamente deshabilitando la autenticación para una vista específica.
    """
    
    def authenticate(self, request):
        return None
