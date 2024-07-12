from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied, ValidationError
from apps.custom_auth.models import ProfileInformation
from apps.custom_auth.infrastructure.api.v1.serializers.profile_information_serializer import ProfileInformationSerializer


class ProfileInformationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProfileInformation.objects.all()
    serializer_class = ProfileInformationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_object(self):
        """Obtiene o crea la información de perfil del usuario actual."""
        profile_information, created = ProfileInformation.objects.get_or_create(
            user=self.request.user)
        return profile_information

    def perform_update(self, serializer):
        """Verifica que el usuario tenga permiso para actualizar el perfil."""
        if self.request.user.id != serializer.instance.user.id:
            raise PermissionDenied(
                "No tienes permiso para editar este perfil.")
        serializer.save()

    def perform_destroy(self, instance):
        """Verifica que el usuario tenga permiso para eliminar el perfil y que la información del perfil esté vacía."""
        if self.request.user.id != instance.user.id:
            raise PermissionDenied(
                "No tienes permiso para eliminar este perfil.")
        if not instance.about_me and not instance.disciplines and not instance.contact_info:
            instance.delete()
        else:
            raise ValidationError(
                "La información del perfil debe estar vacía para ser eliminada.")


class PublicProfileInformationDetailView(generics.RetrieveAPIView):
    queryset = ProfileInformation.objects.all()
    serializer_class = ProfileInformationSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'user__id'
