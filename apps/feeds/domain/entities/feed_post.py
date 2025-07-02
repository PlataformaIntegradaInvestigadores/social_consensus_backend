"""
Modelo para los posts del feed social
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from pgvector.django import VectorField
import uuid

User = get_user_model()


def get_post_file_path(instance, filename):
    """Genera ruta para archivos de posts"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return f'feed_posts/{instance.post.id}/{filename}'


class FeedPost(models.Model):
    """
    Modelo para posts del feed social
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feed_posts', verbose_name="Autor")
    content = models.TextField(verbose_name="Contenido del post")
    
    # Vector embedding para recomendaciones (768 dimensiones)
    embedding = VectorField(dimensions=768, null=True, blank=True, verbose_name="Vector de embedding para recomendaciones")
    
    # Métricas de interacción
    likes_count = models.IntegerField(default=0, verbose_name="Número de likes")
    comments_count = models.IntegerField(default=0, verbose_name="Número de comentarios")
    views_count = models.IntegerField(default=0, verbose_name="Número de visualizaciones")
    shares_count = models.IntegerField(default=0, verbose_name="Número de compartidos")
    
    # Score compuesto para trending
    engagement_score = models.FloatField(default=0.0, verbose_name="Score de engagement")
    
    # Configuración de privacidad
    is_public = models.BooleanField(default=True, verbose_name="Post público")
    is_pinned = models.BooleanField(default=False, verbose_name="Post fijado")
    
    # Relación con encuesta (opcional)
    poll = models.OneToOneField('feeds.Poll', on_delete=models.CASCADE, null=True, blank=True, related_name='post', verbose_name="Encuesta del post")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    
    # Metadatos
    tags = models.JSONField(default=list, blank=True, verbose_name="Tags del post")
    metadata = models.JSONField(default=dict, blank=True, verbose_name="Metadatos adicionales")
    
    class Meta:
        verbose_name = "Post del Feed"
        verbose_name_plural = "Posts del Feed"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['-engagement_score']),
            models.Index(fields=['author', '-created_at']),
        ]
    
    def __str__(self):
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"{self.author.username} - {content_preview}"
    
    def update_engagement_score(self):
        """
        Actualiza el score de engagement basado en interacciones
        """
        # Algoritmo de scoring: likes*1 + comments*2 + shares*3 + views*0.1
        hours_old = (timezone.now() - self.created_at).total_seconds() / 3600
        
        raw_score = (
            self.likes_count * 1.0 +
            self.comments_count * 2.0 +
            self.shares_count * 3.0 +
            self.views_count * 0.1
        )
        
        # Penalización por tiempo (decay factor)
        time_decay = 1 / (1 + hours_old / 24)  # Decae por días
        
        self.engagement_score = raw_score * time_decay
        self.save(update_fields=['engagement_score'])
    
    def get_files(self):
        """Retorna todos los archivos asociados al post"""
        return self.post_files.all()
    
    def get_images(self):
        """Retorna solo las imágenes del post"""
        return self.post_files.filter(file_type='image')
    
    def get_documents(self):
        """Retorna solo los documentos del post"""
        return self.post_files.filter(file_type='document')
