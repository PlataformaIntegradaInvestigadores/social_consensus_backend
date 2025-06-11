from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth.models import AnonymousUser
from apps.custom_auth.models import User, Company


class DualUserJWTAuthentication(JWTAuthentication):
    """
    Autenticación JWT que puede manejar tanto usuarios como empresas
    basándose en el contenido del token.
    """
    
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
            elif 'user_id' in validated_token:
                user_id = validated_token['user_id']
                try:
                    user = User.objects.get(id=user_id)
                    if user.is_active:
                        return user
                except User.DoesNotExist:
                    pass
            
            # Si no se encuentra ni usuario ni empresa, devolver usuario anónimo
            return AnonymousUser()
            
        except (KeyError, ValueError):
            # Si hay algún error en el formato del token
            return AnonymousUser()
