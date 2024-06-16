import random
import string
from django.db import models
from django.conf import settings


def generate_unique_id(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


class Group(models.Model):
    id = models.CharField(max_length=10, primary_key=True,
                          default=generate_unique_id, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='administered_groups')
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through='GroupUser', related_name='member_groups')

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'GROUP'


class GroupUser(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)

    class Meta:
        db_table = 'GROUP_USERS'
