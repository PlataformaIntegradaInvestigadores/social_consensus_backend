from django.db import models
from django.conf import settings
from .message import DebateMessage


class ClassificationVote(models.Model):
    id = models.AutoField(primary_key=True)
    idMessage = models.ForeignKey(DebateMessage, on_delete=models.CASCADE, related_name='votes')
    idUser = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='classification_votes')
    vote = models.CharField(max_length=10, choices=[('favor', 'Favor'), ('contra', 'Contra')])
    createdAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'classification_votes'
        unique_together = ('idMessage', 'idUser')

    def __str__(self):
        return f'Vote by {self.idUser} on Message {self.idMessage}'
