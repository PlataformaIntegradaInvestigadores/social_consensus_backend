from django.db import models
from django.conf import settings
from .message import DebateMessage


class MessageReaction(models.Model):
    id = models.AutoField(primary_key=True)
    idMessage = models.ForeignKey(DebateMessage, on_delete=models.CASCADE, related_name='reactions')
    idUser = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reactions')
    reaction = models.CharField(max_length=20)  # Example: 👍, 👎, ❓
    createdAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'message_reactions'

    def __str__(self):
        return f'Reaction {self.reaction} by User {self.idUser} on Message {self.idMessage}'
