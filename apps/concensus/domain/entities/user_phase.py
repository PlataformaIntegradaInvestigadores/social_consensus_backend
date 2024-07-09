
from django.db import models
from apps.custom_auth.domain.entities.group import Group
from apps.custom_auth.domain.entities.user import User


class UserPhase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    phase = models.IntegerField(default=0)
    completed_at = models.DateTimeField(null=True, blank=True)

#select * from "concensus_userphase";