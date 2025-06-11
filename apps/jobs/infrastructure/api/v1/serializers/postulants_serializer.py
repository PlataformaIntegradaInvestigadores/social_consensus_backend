# apps/jobs/infrastructure/api/v1/serializers.py

from rest_framework import serializers
from apps.jobs.domain.entities.postulants import Postulants

class PostulantsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Postulants
        fields = '__all__'
