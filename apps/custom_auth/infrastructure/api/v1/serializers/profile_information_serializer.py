from rest_framework import serializers
from apps.custom_auth.models import ProfileInformation


class ProfileInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileInformation
        fields = ['about_me', 'disciplines', 'contact_info']
