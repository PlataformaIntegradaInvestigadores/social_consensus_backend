from django.db import models


from apps.concensus.domain.entities.debate_message import Message
from apps.custom_auth.domain.entities.user import User

class Reaction(models.Model):
    """
    Registra las reacciones ("Me gusta") que hacen los usuarios a los mensajes.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reactions')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reactions')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'message')

    def __str__(self):
        return f'Reaction by {self.user.username} to message {self.message.id}'