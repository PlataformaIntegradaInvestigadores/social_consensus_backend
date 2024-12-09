from django.db import models
from django.conf import settings


class Debate(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('open', 'Open'), ('closed', 'Closed')], default='open')
    idGroup = models.ForeignKey('custom_auth.Group', on_delete=models.CASCADE, related_name='debates')
    idCreator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_debates')
    timeLimit = models.DurationField()
    endTime = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'debates'
        indexes = [
            models.Index(fields=['idGroup'], name='debates_group_id_unique_idx'),
        ]

    def __str__(self):
        return f'Debate {self.title} - Group {self.idGroup}'
