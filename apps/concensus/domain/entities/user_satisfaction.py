from django.db import models
from django.conf import settings

class UserSatisfaction(models.Model):
    SATISFACTION_CHOICES = [
        ('Unsatisfied', 'Unsatisfied'),
        ('Slightly Unsatisfied', 'Slightly Unsatisfied'),
        ('Neutral', 'Neutral'),
        ('Slightly Satisfied', 'Slightly Satisfied'),
        ('Satisfied', 'Satisfied'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    group = models.ForeignKey('custom_auth.Group', on_delete=models.CASCADE)
    satisfaction_level = models.CharField(max_length=20, choices=SATISFACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    message = models.TextField()

    class Meta:
        unique_together = ('user', 'group')

#select * from concensus_usersatisfaction;
       # truncate table concensus_usersatisfaction;