from django.contrib import admin
from apps.jobs.domain.entities.jobs import Jobs
from apps.jobs.domain.entities.postulants import Postulants

# Register your models here.

admin.site.register(Jobs)
admin.site.register(Postulants)
