from django.db import models
from django.conf import settings
from .debate import Debate


class DebateMessage(models.Model):
    id = models.AutoField(primary_key=True)
    idDebate = models.ForeignKey(Debate, on_delete=models.CASCADE, related_name='messages')
    idUser = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    createdAt = models.DateTimeField(auto_now_add=True)
    isSystemMessage = models.BooleanField(default=False)
    classification = models.CharField(
        max_length=20,
        choices=[('favor', 'Favor'), ('contra', 'Contra'), ('neutral', 'Neutral')],
        default='neutral',
    )

    class Meta:
        db_table = 'debate_messages'

    def __str__(self):
        return f'Message {self.id} by User {self.idUser} in Debate {self.idDebate}'
