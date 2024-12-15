from django.db import models
from apps.custom_auth.domain.entities.group import Group

class Debate(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='debates')
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField()
    is_closed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} - {self.group.title}"

    class Meta:
        db_table = 'debates'