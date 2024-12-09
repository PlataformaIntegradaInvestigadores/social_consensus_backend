from django.db import models
from django.conf import settings
from .debate import Debate


class DebateParticipant(models.Model):
    id = models.AutoField(primary_key=True)
    idDebate = models.ForeignKey(Debate, on_delete=models.CASCADE, related_name='participants')
    idUser = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='participated_debates')
    joinedAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'debate_participants'
        unique_together = ('idDebate', 'idUser')

    def __str__(self):
        return f'Participant {self.idUser} in Debate {self.idDebate}'
