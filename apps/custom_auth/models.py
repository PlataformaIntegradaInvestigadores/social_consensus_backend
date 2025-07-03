from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import uuid

from apps.custom_auth.domain.entities.user import User
from apps.custom_auth.domain.entities.company import Company
from apps.custom_auth.domain.entities.profile_information import ProfileInformation
from apps.custom_auth.domain.entities.group import Group

User = get_user_model()


class MagicLink(models.Model):
    """
    Model to store magic link tokens for passwordless authentication
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='magic_links')
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Magic Link"
        verbose_name_plural = "Magic Links"
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Magic links expire after 30 minutes
            self.expires_at = timezone.now() + timedelta(minutes=30)
        if not self.token:
            self.token = str(uuid.uuid4())
        super().save(*args, **kwargs)
    
    def is_valid(self):
        """Check if the magic link is still valid"""
        return not self.is_used and timezone.now() < self.expires_at
    
    def mark_as_used(self):
        """Mark the magic link as used"""
        self.is_used = True
        self.used_at = timezone.now()
        self.save()
    
    def __str__(self):
        return f"Magic Link for {self.user.email} - {'Valid' if self.is_valid() else 'Invalid'}"
