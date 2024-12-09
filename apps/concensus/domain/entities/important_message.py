from django.db import models
from django.conf import settings
from .message import DebateMessage


class ImportantMessage(models.Model):
    id = models.AutoField(primary_key=True)
    idMessage = models.ForeignKey(DebateMessage, on_delete=models.CASCADE, related_name='important_marks')
    idMarkedByUser = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='important_messages')
    markedAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'important_messages'

    def __str__(self):
        return f'Message {self.idMessage.id} marked as important by {self.idMarkedByUser}'
