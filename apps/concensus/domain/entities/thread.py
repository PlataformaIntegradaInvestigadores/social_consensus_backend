from django.db import models
from .message import DebateMessage


class MessageThread(models.Model):
    id = models.AutoField(primary_key=True)
    idParentMessage = models.ForeignKey(DebateMessage, on_delete=models.CASCADE, related_name='child_threads')
    idChildMessage = models.ForeignKey(DebateMessage, on_delete=models.CASCADE, related_name='parent_threads')

    class Meta:
        db_table = 'message_threads'

    def __str__(self):
        return f'Thread: Parent {self.idParentMessage.id} -> Child {self.idChildMessage.id}'
