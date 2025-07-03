from rest_framework import permissions
from apps.custom_auth.models import User


class IsResearcherPermission(permissions.BasePermission):
    """
    Permission que solo permite acceso a usuarios con rol de researcher.
    Las empresas (Company) no tienen acceso a los feeds.
    """
    
    def has_permission(self, request, view):
        # Verificar que el usuario esté autenticado
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Verificar que el usuario sea una instancia de User (researcher) y no Company
        return isinstance(request.user, User)
    
    def has_object_permission(self, request, view, obj):
        # Similar verificación para permisos a nivel de objeto
        if not request.user or not request.user.is_authenticated:
            return False
        
        return isinstance(request.user, User)
