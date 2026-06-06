from rest_framework import permissions


class IsResearcherPermission(permissions.BasePermission):
    """
    Permite acceso a principales autenticados de identidad.
    Las empresas siguen identificandose por company_name y no entran al feed.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return not hasattr(request.user, 'company_name')

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        return not hasattr(request.user, 'company_name')
