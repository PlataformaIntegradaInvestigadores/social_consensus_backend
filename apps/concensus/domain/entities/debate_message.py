from django.db import models

from apps.concensus.domain.entities.debate import Debate
from apps.custom_auth.domain.entities.group import Group
from apps.custom_auth.domain.entities.user import User

class Message(models.Model):
    """
    Representa un mensaje dentro del chat grupal de un debate.
    """
    POSTURES = (
        ('agree', 'De acuerdo'),
        ('disagree', 'No de acuerdo'),
        ('neutral', 'Neutral')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    debate = models.ForeignKey(Debate, on_delete=models.CASCADE, related_name='messages')
    text = models.TextField()
    posture = models.CharField(max_length=10, choices=POSTURES, default='neutral')
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Message by {self.user.username} in {self.debate.title}'