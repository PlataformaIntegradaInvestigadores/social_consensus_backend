from django.db import models
from django.conf import settings

class ProfileInformation(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile_information')
    about_me = models.TextField(blank=True, null=True)
    disciplines = models.JSONField(default=list, blank=True)
    contact_info = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile Information"

    class Meta:
        db_table = 'profiles_information'