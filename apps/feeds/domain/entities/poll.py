from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class Poll(models.Model):
    """
    Modelo para encuestas en posts del feed
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.TextField(max_length=500)
    is_multiple_choice = models.BooleanField(default=False)
    is_anonymous = models.BooleanField(default=False)
    allows_other = models.BooleanField(default=False)  # Permite opción "Otro"
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'feed_polls'
        verbose_name = 'Poll'
        verbose_name_plural = 'Polls'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Poll: {self.question[:50]}..."
    
    @property
    def total_votes(self):
        """Retorna el total de votos en todas las opciones"""
        return sum(option.votes_count for option in self.options.all())
    
    @property
    def is_expired(self):
        """Verifica si la encuesta ha expirado"""
        if not self.expires_at:
            return False
        from django.utils import timezone
        return timezone.now() > self.expires_at


class PollOption(models.Model):
    """
    Modelo para opciones de encuestas
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    poll = models.ForeignKey('feeds.Poll', on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=200)
    votes_count = models.PositiveIntegerField(default=0)
    order = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'feed_poll_options'
        verbose_name = 'Poll Option'
        verbose_name_plural = 'Poll Options'
        ordering = ['order', 'created_at']
        unique_together = ['poll', 'order']
    
    def __str__(self):
        return f"{self.poll.question[:30]}... - {self.text}"


class PollVote(models.Model):
    """
    Modelo para votos en encuestas
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='poll_votes')
    poll = models.ForeignKey('feeds.Poll', on_delete=models.CASCADE, related_name='votes')
    option = models.ForeignKey('feeds.PollOption', on_delete=models.CASCADE, related_name='votes')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'feed_poll_votes'
        verbose_name = 'Poll Vote'
        verbose_name_plural = 'Poll Votes'
        unique_together = ['user', 'poll', 'option']  # Un usuario puede votar una vez por opción
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} voted for {self.option.text}"
    
    def save(self, *args, **kwargs):
        """Actualiza el contador de votos al guardar"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            # Incrementar contador de votos
            self.option.votes_count = self.option.votes.count()
            self.option.save(update_fields=['votes_count'])
    
    def delete(self, *args, **kwargs):
        """Actualiza el contador de votos al eliminar"""
        option = self.option
        super().delete(*args, **kwargs)
        
        # Decrementar contador de votos
        option.votes_count = option.votes.count()
        option.save(update_fields=['votes_count'])
