from django.db import models
from apps.concensus.domain.entities.debate import Debate


class DebateParticipant(models.Model):
    debate = models.ForeignKey(Debate, on_delete=models.CASCADE, related_name='participants')
    participant = models.ForeignKey('custom_auth.User', on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    is_collaborator = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.participant.username} in debate {self.debate.title}"
    class Meta:
        db_table = 'debate_participants'