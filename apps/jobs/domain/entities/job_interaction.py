"""
Modelo para tracking de interacciones por usuario
"""
from django.db import models
from django.contrib.auth import get_user_model
from apps.jobs.domain.entities.jobs import Jobs

User = get_user_model()


class JobInteraction(models.Model):
    """
    Registra interacciones específicas de cada usuario con jobs
    """
    INTERACTION_TYPES = [
        ('view', 'Vista'),
        ('application', 'Aplicación'),
        ('save', 'Guardado'),
        ('share', 'Compartido'),
        ('click', 'Click en detalles'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='job_interactions',
        verbose_name="Usuario"
    )
    
    job = models.ForeignKey(
        Jobs,
        on_delete=models.CASCADE,
        related_name='user_interactions',
        verbose_name="Job"
    )
    
    interaction_type = models.CharField(
        max_length=20,
        choices=INTERACTION_TYPES,
        verbose_name="Tipo de interacción"
    )
    
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha y hora"
    )
    
    # Metadatos adicionales (opcional)
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Metadatos adicionales"
    )
    
    class Meta:
        unique_together = ['user', 'job', 'interaction_type']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['job', 'interaction_type']),
            models.Index(fields=['timestamp']),
        ]
        verbose_name = "Interacción con Job"
        verbose_name_plural = "Interacciones con Jobs"
    
    def __str__(self):
        return f"{self.user.username} - {self.job.title} - {self.interaction_type}"
