from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied, ValidationError
from apps.custom_auth.models import ProfileInformation
from apps.custom_auth.infrastructure.api.v1.serializers.profile_information_serializer import ProfileInformationSerializer


class ProfileInformationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProfileInformation.objects.all()
    serializer_class = ProfileInformationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_object(self):
        profile_information, created = ProfileInformation.objects.get_or_create(
            user=self.request.user)
        return profile_information

    def perform_update(self, serializer):
        if self.request.user.id != serializer.instance.user.id:
            raise PermissionDenied(
                "You do not have permission to edit this profile.")
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user.id != instance.user.id:
            raise PermissionDenied(
                "You do not have permission to delete this profile.")
        if not instance.about_me and not instance.disciplines and not instance.contact_info:
            instance.delete()
        else:
            raise ValidationError(
                "Profile information must be empty to be deleted.")


class PublicProfileInformationDetailView(generics.RetrieveAPIView):
    queryset = ProfileInformation.objects.all()
    serializer_class = ProfileInformationSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'user__id'
