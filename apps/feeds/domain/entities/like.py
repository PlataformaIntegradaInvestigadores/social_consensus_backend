"""
Modelo para likes en posts y comentarios del feed
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import uuid

User = get_user_model()


class Like(models.Model):
    """
    Modelo para likes que puede aplicarse tanto a posts como a comentarios
    usando Generic Foreign Keys
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Usuario que da el like
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='likes_given',
        verbose_name="Usuario"
    )
    
    # Generic Foreign Key para likes en posts o comentarios
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de like")
    
    class Meta:
        verbose_name = "Like"
        verbose_name_plural = "Likes"
        unique_together = ['user', 'content_type', 'object_id']  # Un usuario solo puede dar un like por objeto
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} likes {self.content_object}"
    
    @classmethod
    def toggle_like(cls, user, target_object):
        """
        Alterna el like de un usuario en un objeto (post o comentario)
        
        Args:
            user: Usuario que da/quita el like
            target_object: Objeto que recibe el like (FeedPost o Comment)
            
        Returns:
            tuple: (like_instance, created) donde created=True si se creó el like
        """
        content_type = ContentType.objects.get_for_model(target_object)
        
        like, created = cls.objects.get_or_create(
            user=user,
            content_type=content_type,
            object_id=target_object.id
        )
        
        if not created:
            # Si ya existía el like, lo eliminamos (unlike)
            like.delete()
            like = None
        
        # Actualizar el contador en el objeto target
        cls._update_likes_count(target_object)
        
        return like, created
    
    @classmethod
    def _update_likes_count(cls, target_object):
        """
        Actualiza el contador de likes en el objeto target
        """
        content_type = ContentType.objects.get_for_model(target_object)
        
        likes_count = cls.objects.filter(
            content_type=content_type,
            object_id=target_object.id
        ).count()
        
        target_object.likes_count = likes_count
        target_object.save(update_fields=['likes_count'])
        
        # Si es un post, también actualizar engagement_score
        if hasattr(target_object, 'update_engagement_score'):
            target_object.update_engagement_score()
    
    @classmethod
    def get_user_likes_for_objects(cls, user, objects):
        """
        Retorna los likes que un usuario ha dado a una lista de objetos
        
        Args:
            user: Usuario
            objects: Lista de objetos (posts o comentarios)
            
        Returns:
            dict: Mapeo de object_id -> Like instance
        """
        if not objects:
            return {}
        
        # Agrupar objetos por tipo
        objects_by_type = {}
        for obj in objects:
            content_type = ContentType.objects.get_for_model(obj)
            if content_type not in objects_by_type:
                objects_by_type[content_type] = []
            objects_by_type[content_type].append(obj.id)
        
        # Obtener todos los likes del usuario para estos objetos
        likes = []
        for content_type, object_ids in objects_by_type.items():
            likes.extend(
                cls.objects.filter(
                    user=user,
                    content_type=content_type,
                    object_id__in=object_ids
                )
            )
        
        # Crear mapeo
        return {str(like.object_id): like for like in likes}
    
    @classmethod
    def get_likes_count_for_objects(cls, objects):
        """
        Retorna el conteo de likes para una lista de objetos
        
        Args:
            objects: Lista de objetos (posts o comentarios)
            
        Returns:
            dict: Mapeo de object_id -> likes_count
        """
        if not objects:
            return {}
        
        # Agrupar objetos por tipo
        objects_by_type = {}
        for obj in objects:
            content_type = ContentType.objects.get_for_model(obj)
            if content_type not in objects_by_type:
                objects_by_type[content_type] = []
            objects_by_type[content_type].append(obj.id)
        
        # Contar likes
        likes_count = {}
        for content_type, object_ids in objects_by_type.items():
            counts = cls.objects.filter(
                content_type=content_type,
                object_id__in=object_ids
            ).values('object_id').annotate(
                count=models.Count('id')
            )
            
            for item in counts:
                likes_count[str(item['object_id'])] = item['count']
        
        return likes_count
