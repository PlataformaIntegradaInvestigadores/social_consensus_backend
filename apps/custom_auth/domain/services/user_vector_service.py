"""
Servicio para manejo de vectores de usuario y recomendaciones personalizadas
"""
import requests
import logging
from typing import List, Optional, Dict, Any
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


class UserVectorService:
    """
    Servicio para manejar vectores de usuario y actualización basada en interacciones
    """
    
    def __init__(self, embedding_service_url: str = None):
        self.embedding_service_url = embedding_service_url or settings.EMBEDDING_SERVICE_URL
    
    def get_embedding_from_microservice(self, text: str) -> Optional[List[float]]:
        """
        Obtiene embedding desde el microservicio
        
        Args:
            text: Texto para convertir a embedding
            
        Returns:
            Vector embedding o None si hay error
        """
        try:
            payload = {
                "text": text,
                "translate_to_english": True,
                "clean_text": True
            }
            
            response = requests.post(
                f"{self.embedding_service_url}/text-processing/vectorize/",
                json=payload,
                timeout=30,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                vector = result.get('vector')
                
                if vector:
                    logger.info(f"Embedding de usuario generado. Dimensiones: {result.get('dimension', len(vector))}")
                    return vector
                else:
                    logger.error("El microservicio no devolvió un vector válido")
                    return None
            else:
                logger.error(f"Error al obtener embedding: {response.status_code} - {response.text}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Error de conexión con microservicio: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}")
            return None
    
    def generate_user_job_profile_text(self, user) -> str:
        """
        Genera texto del perfil del usuario para recomendaciones de jobs
        
        Args:
            user: Instancia del modelo User
            
        Returns:
            Texto combinado del perfil del usuario
        """
        profile_parts = []
        
        # Información básica
        profile_parts.append(f"Investigador: {user.first_name} {user.last_name}")
        
        if user.investigation_camp:
            profile_parts.append(f"Campo de investigación: {user.investigation_camp}")
        
        if user.institution:
            profile_parts.append(f"Institución: {user.institution}")
        
        if user.interests:
            profile_parts.append(f"Intereses: {user.interests}")
        
        # Información adicional si existe
        if hasattr(user, 'profileinformation'):
            try:
                profile_info = user.profileinformation
                if hasattr(profile_info, 'skills') and profile_info.skills:
                    profile_parts.append(f"Habilidades: {profile_info.skills}")
                if hasattr(profile_info, 'experience') and profile_info.experience:
                    profile_parts.append(f"Experiencia: {profile_info.experience}")
            except:
                pass
        
        return ". ".join(profile_parts)
    
    def generate_user_feed_profile_text(self, user) -> str:
        """
        Genera texto del perfil del usuario para recomendaciones de posts del feed
        Incluye intereses y actividad reciente
        
        Args:
            user: Instancia del modelo User
            
        Returns:
            Texto para generar embedding de feed
        """
        profile_parts = []
        
        # Información de intereses
        if user.interests:
            profile_parts.append(f"Intereses: {user.interests}")
        
        if user.investigation_camp:
            profile_parts.append(f"Área de investigación: {user.investigation_camp}")
        
        # TODO: Agregar posts recientes del usuario, likes, comentarios
        # Esto se implementará cuando tengamos el módulo de feeds
        
        return ". ".join(profile_parts) or "Investigador académico"
    
    def update_user_job_embedding(self, user_id: int) -> bool:
        """
        Actualiza el embedding del usuario para recomendaciones de jobs
        
        Args:
            user_id: ID del usuario
            
        Returns:
            True si se actualizó correctamente
        """
        try:
            user = User.objects.get(id=user_id)
            
            # Generar texto del perfil
            profile_text = self.generate_user_job_profile_text(user)
            
            if not profile_text.strip():
                logger.warning(f"Usuario {user_id} no tiene suficiente información para generar embedding")
                return False
            
            # Obtener embedding
            embedding = self.get_embedding_from_microservice(profile_text)
            
            if embedding:
                user.job_recommendations_embedding = embedding
                user.profile_vector_updated_at = timezone.now()
                user.save(update_fields=['job_recommendations_embedding', 'profile_vector_updated_at'])
                
                logger.info(f"Embedding de jobs actualizado para usuario {user_id}")
                return True
            else:
                logger.error(f"No se pudo generar embedding para usuario {user_id}")
                return False
                
        except User.DoesNotExist:
            logger.error(f"Usuario {user_id} no encontrado")
            return False
        except Exception as e:
            logger.error(f"Error actualizando embedding de usuario {user_id}: {str(e)}")
            return False
    
    def update_user_feed_embedding(self, user_id: int) -> bool:
        """
        Actualiza el embedding del usuario para recomendaciones de feed
        
        Args:
            user_id: ID del usuario
            
        Returns:
            True si se actualizó correctamente
        """
        try:
            user = User.objects.get(id=user_id)
            
            # Generar texto del perfil para feed
            profile_text = self.generate_user_feed_profile_text(user)
            
            # Obtener embedding
            embedding = self.get_embedding_from_microservice(profile_text)
            
            if embedding:
                user.feed_recommendations_embedding = embedding
                user.profile_vector_updated_at = timezone.now()
                user.save(update_fields=['feed_recommendations_embedding', 'profile_vector_updated_at'])
                
                logger.info(f"Embedding de feed actualizado para usuario {user_id}")
                return True
            else:
                logger.error(f"No se pudo generar embedding de feed para usuario {user_id}")
                return False
                
        except User.DoesNotExist:
            logger.error(f"Usuario {user_id} no encontrado")
            return False
        except Exception as e:
            logger.error(f"Error actualizando embedding de feed para usuario {user_id}: {str(e)}")
            return False
    
    def update_user_vectors_on_interaction(self, user_id: int, interaction_type: str, content: str = None):
        """
        Actualiza los vectores del usuario cuando interactúa con contenido
        (likes, comentarios, views, etc.)
        
        Args:
            user_id: ID del usuario
            interaction_type: Tipo de interacción ('like', 'comment', 'view', etc.)
            content: Contenido con el que interactuó (opcional)
        """
        try:
            user = User.objects.get(id=user_id)
            
            # Incrementar contador de interacciones
            user.interaction_count += 1
            
            # Actualizar vectores cada 10 interacciones o si es una interacción importante
            should_update = (
                user.interaction_count % 10 == 0 or 
                interaction_type in ['comment', 'post_created'] or
                user.job_recommendations_embedding is None or
                user.feed_recommendations_embedding is None
            )
            
            if should_update:
                logger.info(f"Actualizando vectores de usuario {user_id} tras {user.interaction_count} interacciones")
                
                # Actualizar ambos embeddings
                job_success = self.update_user_job_embedding(user_id)
                feed_success = self.update_user_feed_embedding(user_id)
                
                if job_success or feed_success:
                    logger.info(f"Vectores actualizados para usuario {user_id}")
                else:
                    logger.warning(f"No se pudieron actualizar vectores para usuario {user_id}")
            
            # Guardar contador
            user.save(update_fields=['interaction_count'])
            
        except User.DoesNotExist:
            logger.error(f"Usuario {user_id} no encontrado")
        except Exception as e:
            logger.error(f"Error actualizando vectores en interacción: {str(e)}")
    
    def get_users_for_job_recommendations(self, job_embedding: List[float], limit: int = 10) -> List:
        """
        Encuentra usuarios similares a un job específico para notificaciones
        
        Args:
            job_embedding: Vector del job
            limit: Número de usuarios a retornar
            
        Returns:
            Lista de usuarios ordenados por similitud
        """
        from django.db.models.expressions import RawSQL
        
        if not job_embedding:
            return []
        
        embedding_str = '[' + ','.join(map(str, job_embedding)) + ']'
        similarity_sql = f"(1 - (job_recommendations_embedding <#> '{embedding_str}'))"
        
        users = User.objects.filter(
            job_recommendations_embedding__isnull=False
        ).annotate(
            similarity=RawSQL(similarity_sql, [])
        ).filter(
            similarity__gte=0.7  # Umbral de similitud
        ).order_by('-similarity')[:limit]
        
        return list(users)


# Instancia global del servicio
user_vector_service = UserVectorService()
