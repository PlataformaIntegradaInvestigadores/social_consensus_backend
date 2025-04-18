import random
import string
from django.db import models
from django.conf import settings

def generate_unique_id(length=10):
    """Genera un ID único con la longitud especificada."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

class Group(models.Model):
    class VotingType(models.TextChoices):
        POSITIONAL = 'Positional Voting'
        NONPOSITIONAL = 'Non-Positional Voting'
        
    id = models.CharField(max_length=10, primary_key=True, default=generate_unique_id, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='administered_groups')
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='GroupUser', related_name='member_groups')
    voting_type = models.CharField(max_length=50, choices=VotingType.choices, default=VotingType.POSITIONAL)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'groups'

class GroupUser(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        db_table = 'group_users'
