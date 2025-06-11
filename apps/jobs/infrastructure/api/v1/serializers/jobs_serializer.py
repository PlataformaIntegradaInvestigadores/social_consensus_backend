# apps/jobs/infrastructure/api/v1/serializers.py

from rest_framework import serializers
from apps.jobs.domain.entities.jobs import Jobs

class JobsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Jobs
        fields = '__all__'
