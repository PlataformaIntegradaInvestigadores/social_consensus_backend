from django.db import models

from apps.concensus.domain.entities.debate import Debate
from apps.custom_auth.domain.entities.user import User


class UserPosture(models.Model):
    """
    Registra la postura de un usuario respecto a un debate.
    """
    POSTURES = (
        ('agree', 'De acuerdo'),
        ('disagree', 'No de acuerdo'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='postures')
    debate = models.ForeignKey(Debate, on_delete=models.CASCADE, related_name='postures')
    posture = models.CharField(max_length=10, choices=POSTURES)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'debate')

    def __str__(self):
        return f'{self.user.username} - {self.posture} - {self.debate.title}'