from django.db import models
from apps.jobs.domain.entities.jobs import Jobs


class Postulants(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    jobs = models.ManyToManyField(Jobs)

    def __str__(self):
        return f"{self.title}"

    class Meta:
        db_table = 'postulants'
