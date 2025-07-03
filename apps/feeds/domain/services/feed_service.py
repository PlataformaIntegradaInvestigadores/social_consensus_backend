"""
Servicio principal para manejo del feed social con embeddings y recomendaciones
"""
import requests
import logging
from typing import List, Optional, Dict, Any
from django.db.models import QuerySet, F, Q
from django.db.models.expressions import RawSQL
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model

# Importar modelos del feed
from apps.feeds.domain.entities.feed_post import FeedPost
from apps.feeds.domain.entities.comment import Comment
from apps.feeds.domain.entities.like import Like

# Importar servicio de vectores de usuario
from apps.custom_auth.domain.services.user_vector_service import user_vector_service

logger = logging.getLogger(__name__)
User = get_user_model()


class FeedService:
    """
    Servicio principal para manejo del feed social
    """
    
    def __init__(self, embedding_service_url: str = None):
        self.embedding_service_url = embedding_service_url or settings.EMBEDDING_SERVICE_URL
    
    def get_embedding_from_microservice(self, text: str) -> Optional[List[float]]:
        """
        Obtiene embedding de texto desde el microservicio
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
                    logger.info(f"Embedding generado para post. Dimensiones: {result.get('dimension', len(vector))}")
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
    
    def create_post(self, author=None, author_id: str = None, content: str = None, tags: List[str] = None, files: List[Dict] = None, is_public: bool = True) -> Optional[FeedPost]:
        """
        Crea un nuevo post en el feed
        
        Args:
            author: Instancia del usuario autor (alternativo a author_id)
            author_id: ID del autor (alternativo a author)
            content: Contenido del post
            tags: Lista de tags
            files: Lista de archivos del post
            is_public: Si el post es público
            
        Returns:
            Instancia del post creado o None si hay error
        """
        try:
            # Determinar el autor
            if author:
                author_instance = author
                author_id = str(author.id)
            elif author_id:
                author_instance = User.objects.get(id=author_id)
            else:
                raise ValueError("Debe proporcionar author o author_id")
              # Crear el post
            post = FeedPost.objects.create(
                author=author_instance,
                content=content,
                tags=tags or [],
                is_public=is_public
            )
            
            # Generar embedding para el post
            self.update_post_embedding(post.id)
            
            # Actualizar vectores del usuario basado en su nuevo post
            user_vector_service.update_user_vectors_on_interaction(
                user_id=author_id,
                interaction_type='post_created',
                content=content
            )
            
            logger.info(f"Post creado: {post.id} por {author_instance.username}")
            return post
            
        except User.DoesNotExist:
            logger.error(f"Usuario {author_id} no encontrado")
            return None
        except Exception as e:
            logger.error(f"Error creando post: {str(e)}")
            return None
    
    def update_post_embedding(self, post_id: str) -> bool:
        """
        Actualiza el embedding de un post
        """
        try:
            post = FeedPost.objects.get(id=post_id)
            
            # Generar texto para embedding
            embedding_text = self._generate_post_embedding_text(post)
            
            # Obtener embedding
            embedding = self.get_embedding_from_microservice(embedding_text)
            
            if embedding:
                post.embedding = embedding
                post.save(update_fields=['embedding'])
                logger.info(f"Embedding actualizado para post {post_id}")
                return True
            else:
                logger.error(f"No se pudo generar embedding para post {post_id}")
                return False
                
        except FeedPost.DoesNotExist:
            logger.error(f"Post {post_id} no encontrado")
            return False
        except Exception as e:
            logger.error(f"Error actualizando embedding: {str(e)}")
            return False
    
    def _generate_post_embedding_text(self, post: FeedPost) -> str:
        """
        Genera texto completo del post para crear embedding
        """
        text_parts = [post.content]
        
        # Agregar tags
        if post.tags:
            text_parts.append("Tags: " + ", ".join(post.tags))
        
        # Agregar información del autor
        text_parts.append(f"Autor: {post.author.first_name} {post.author.last_name}")
        if post.author.investigation_camp:
            text_parts.append(f"Campo: {post.author.investigation_camp}")
        
        return ". ".join(text_parts)
    
    def get_personalized_feed(self, user_id: str = None, user=None, limit: int = 20, cursor: str = None):
        """
        Obtiene feed personalizado basado en el embedding del usuario
        """
        try:
            # Permitir usar tanto user_id como objeto user
            if user:
                user_obj = user
                user_id = user.id
            else:
                user_obj = User.objects.get(id=user_id)
            
            logger.info(f"Obteniendo feed personalizado para usuario {user_id}")
            
            if not user_obj.feed_recommendations_embedding:
                # Si el usuario no tiene embedding, retornar feed trending
                logger.info(f"Usuario {user_id} sin embedding, retornando feed trending")
                return self.get_trending_feed(limit, cursor)
            
            # Contar posts disponibles
            total_posts = FeedPost.objects.filter(is_public=True).count()
            posts_with_embedding = FeedPost.objects.filter(is_public=True, embedding__isnull=False).count()
            logger.info(f"Total posts públicos: {total_posts}, Posts con embedding: {posts_with_embedding}")
            
            # Usar embedding del usuario para recomendaciones
            user_embedding = user_obj.feed_recommendations_embedding
            embedding_str = '[' + ','.join(map(str, user_embedding)) + ']'
            
            # Calcular similitud y score compuesto
            similarity_sql = f"(1 - (embedding <#> '{embedding_str}'))"
            hours_old_sql = "EXTRACT(EPOCH FROM (NOW() - created_at)) / 3600"
            
            # Score: 50% similitud + 30% engagement + 20% penalización tiempo
            composite_score_sql = f"""
                (
                    0.5 * {similarity_sql} +
                    0.3 * (engagement_score / 100) -
                    0.2 * ({hours_old_sql} / 24)
                )
            """
            
            # Primero intentar con posts que tienen embedding y buena similitud
            queryset_with_embedding = FeedPost.objects.filter(
                is_public=True,
                embedding__isnull=False
            ).annotate(
                similarity=RawSQL(similarity_sql, []),
                hours_old=RawSQL(hours_old_sql, []),
                recommendation_score=RawSQL(composite_score_sql, [])
            ).filter(
                similarity__gte=0.1  # Umbral más bajo y permisivo
            ).select_related('author').prefetch_related('post_files').order_by('-recommendation_score')
            
            # Aplicar cursor si se proporciona
            if cursor:
                queryset_with_embedding = queryset_with_embedding.filter(created_at__lt=cursor)
            
            posts_with_embedding = list(queryset_with_embedding[:limit + 1])
            logger.info(f"Posts encontrados con embedding y similitud >= 0.1: {len(posts_with_embedding)}")
            
            # Si no encontramos suficientes posts con embedding, mezclar con trending
            if len(posts_with_embedding) < limit:
                logger.info(f"Completando con posts trending (necesitamos {limit - len(posts_with_embedding)} más)")
                # Obtener posts trending para completar
                trending_posts, _, _ = self.get_trending_feed(limit * 2, cursor)
                
                # Combinar y evitar duplicados
                existing_ids = {post.id for post in posts_with_embedding}
                additional_posts = [post for post in trending_posts if post.id not in existing_ids]
                
                # Mezclar los posts
                all_posts = posts_with_embedding[:limit] + additional_posts
                final_posts = all_posts[:limit]
                
                logger.info(f"Feed final personalizado: {len(final_posts)} posts")
                
                has_next = len(all_posts) > limit or len(posts_with_embedding) > limit
                next_cursor = final_posts[-1].created_at.isoformat() if final_posts else None
                
                return final_posts, has_next, next_cursor
            else:
                # Tenemos suficientes posts con embedding
                has_next = len(posts_with_embedding) > limit
                if has_next:
                    posts_with_embedding = posts_with_embedding[:limit]
                    next_cursor = posts_with_embedding[-1].created_at.isoformat() if posts_with_embedding else None
                else:
                    next_cursor = None
                
                logger.info(f"Feed personalizado con embedding: {len(posts_with_embedding)} posts")
                return posts_with_embedding, has_next, next_cursor
            
        except User.DoesNotExist:
            logger.error(f"Usuario {user_id} no encontrado")
            return [], False, None
        except Exception as e:
            logger.error(f"Error obteniendo feed personalizado: {str(e)}")
            return self.get_trending_feed(limit, cursor)
    
    def get_trending_feed(self, limit: int = 20, cursor: str = None):
        """
        Obtiene posts en tendencia basados en engagement
        """
        try:
            logger.info(f"Obteniendo feed trending con límite: {limit}")
            
            hours_old_sql = "EXTRACT(EPOCH FROM (NOW() - created_at)) / 3600"
            
            trending_score_sql = f"""
                (
                    engagement_score / (1 + ({hours_old_sql} / 24))
                )
            """
            
            queryset = FeedPost.objects.filter(
                is_public=True
            ).annotate(
                hours_old=RawSQL(hours_old_sql, []),
                trending_score=RawSQL(trending_score_sql, [])
            ).select_related('author').prefetch_related('post_files').order_by('-trending_score')
            
            # Contar posts disponibles
            total_count = queryset.count()
            logger.info(f"Posts públicos disponibles para trending: {total_count}")
            
            # Aplicar cursor si se proporciona
            if cursor:
                queryset = queryset.filter(created_at__lt=cursor)
            
            posts = list(queryset[:limit + 1])  # +1 to check if there's more
            
            # Si no hay posts con engagement score, obtener los más recientes
            if not posts:
                logger.info("No hay posts trending, obteniendo los más recientes")
                return self.get_latest_feed(limit, cursor)
            
            has_next = len(posts) > limit
            
            if has_next:
                posts = posts[:limit]
                next_cursor = posts[-1].created_at.isoformat() if posts else None
            else:
                next_cursor = None
            
            logger.info(f"Feed trending obtenido: {len(posts)} posts")
            return posts, has_next, next_cursor
            
        except Exception as e:
            logger.error(f"Error obteniendo feed trending: {str(e)}")
            return self.get_latest_feed(limit, cursor)
            return [], False, None
    
    def handle_user_interaction(self, user_id: str, post_id: str, interaction_type: str):
        """
        Maneja interacciones del usuario con posts (view, like, comment, share)
        """
        try:
            post = FeedPost.objects.get(id=post_id)
            
            # Actualizar métricas del post
            if interaction_type == 'view':
                post.views_count = F('views_count') + 1
            elif interaction_type == 'share':
                post.shares_count = F('shares_count') + 1
            
            if interaction_type in ['view', 'share']:
                post.save(update_fields=[f'{interaction_type}s_count'])
                post.refresh_from_db()
                post.update_engagement_score()
            
            # Actualizar vectores del usuario basado en la interacción
            user_vector_service.update_user_vectors_on_interaction(
                user_id=user_id,
                interaction_type=interaction_type,
                content=post.content[:200]  # Primeros 200 caracteres
            )
            
            logger.info(f"Interacción {interaction_type} registrada: Usuario {user_id} - Post {post_id}")
            
        except FeedPost.DoesNotExist:
            logger.error(f"Post {post_id} no encontrado")
        except Exception as e:
            logger.error(f"Error manejando interacción: {str(e)}")
    
    def create_comment(self, author_id: str, post_id: str, content: str, parent_comment_id: str = None) -> Optional[Comment]:
        """
        Crea un comentario en un post
        """
        try:
            author = User.objects.get(id=author_id)
            post = FeedPost.objects.get(id=post_id)
            
            parent_comment = None
            if parent_comment_id:
                parent_comment = Comment.objects.get(id=parent_comment_id)
                
                # Verificar límite de anidación
                if not parent_comment.can_reply():
                    logger.warning(f"Máximo nivel de anidación alcanzado para comentario {parent_comment_id}")
                    return None
            
            # Crear comentario
            comment = Comment.objects.create(
                post=post,
                author=author,
                parent_comment=parent_comment,
                content=content
            )
            
            # Actualizar engagement del post
            post.update_engagement_score()
              # Actualizar vectores del usuario
            user_vector_service.update_user_vectors_on_interaction(
                user_id=author_id,
                interaction_type='comment',
                content=content
            )
            
            logger.info(f"Comentario creado: {comment.id} por {author.username}")
            return comment
            
        except (User.DoesNotExist, FeedPost.DoesNotExist, Comment.DoesNotExist) as e:
            logger.error(f"Objeto no encontrado: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error creando comentario: {str(e)}")
            return None
    
    def toggle_like(self, user, post):
        """
        Alterna like en post específico
        """
        try:
            # Toggle like
            like, created = Like.toggle_like(user, post)
            
            # Actualizar engagement del post
            post.update_engagement_score()
            
            # Actualizar vectores del usuario si se creó el like
            if created:
                user_vector_service.update_user_vectors_on_interaction(
                    user_id=user.id,
                    interaction_type='like',
                    content=post.content[:100]
                )
            
            logger.info(f"Like {'creado' if created else 'eliminado'}: Usuario {user.id} - Post {post.id}")
            return created  # Return True if liked, False if unliked
            
        except Exception as e:
            logger.error(f"Error toggleando like en post: {str(e)}")
            return False
    
    def get_latest_feed(self, limit: int = 20, cursor: str = None):
        """
        Obtiene feed con posts más recientes
        """
        try:
            logger.info(f"Obteniendo feed más reciente con límite: {limit}")
            
            queryset = FeedPost.objects.filter(is_public=True).order_by('-created_at')
            
            # Contar posts disponibles
            total_count = queryset.count()
            logger.info(f"Posts públicos más recientes disponibles: {total_count}")
            
            if cursor:
                # Cursor-based pagination
                queryset = queryset.filter(created_at__lt=cursor)
            
            posts = list(queryset[:limit + 1])  # +1 to check if there's more
            has_next = len(posts) > limit
            
            if has_next:
                posts = posts[:limit]
                next_cursor = posts[-1].created_at.isoformat() if posts else None
            else:
                next_cursor = None
            
            logger.info(f"Feed más reciente obtenido: {len(posts)} posts")
            return posts, has_next, next_cursor
            
        except Exception as e:
            logger.error(f"Error obteniendo feed reciente: {str(e)}")
            return [], False, None
    
    def get_filtered_feed(self, user, feed_type: str, filters: Dict[str, Any], 
                         limit: int = 20, cursor: str = None):
        """
        Obtiene feed filtrado según criterios
        """
        try:
            # Start with base feed
            if feed_type == 'personalized':
                posts, _, _ = self.get_personalized_feed(user, limit * 2, cursor)
                queryset = FeedPost.objects.filter(id__in=[p.id for p in posts])
            elif feed_type == 'trending':
                posts, _, _ = self.get_trending_feed(limit * 2, cursor)
                queryset = FeedPost.objects.filter(id__in=[p.id for p in posts])
            else:
                queryset = FeedPost.objects.filter(is_public=True)
            
            # Apply filters
            if filters.get('tags'):
                queryset = queryset.filter(tags__overlap=filters['tags'])
            
            if filters.get('author_ids'):
                queryset = queryset.filter(author_id__in=filters['author_ids'])
            
            if filters.get('date_from'):
                queryset = queryset.filter(created_at__gte=filters['date_from'])
            
            if filters.get('date_to'):
                queryset = queryset.filter(created_at__lte=filters['date_to'])
            
            if filters.get('has_files') is True:
                queryset = queryset.filter(files__isnull=False).distinct()
            elif filters.get('has_files') is False:
                queryset = queryset.filter(files__isnull=True)
            
            if filters.get('file_types'):
                queryset = queryset.filter(
                    files__file_type__in=filters['file_types']
                ).distinct()
            
            # Order and paginate
            queryset = queryset.order_by('-created_at')
            
            if cursor:
                queryset = queryset.filter(created_at__lt=cursor)
                
            posts = list(queryset[:limit + 1])
            has_next = len(posts) > limit
            
            if has_next:
                posts = posts[:limit]
                next_cursor = posts[-1].created_at.isoformat() if posts else None
            else:
                next_cursor = None
                
            return posts, has_next, next_cursor
            
        except Exception as e:
            logger.error(f"Error obteniendo feed filtrado: {str(e)}")
            return [], False, None
    
    def toggle_comment_like(self, user, comment):
        """
        Alterna like en comentario específico
        """
        try:
            # Toggle like
            like, created = Like.toggle_like(user, comment)
            
            # Actualizar vectores del usuario si se creó el like
            if created:
                user_vector_service.update_user_vectors_on_interaction(
                    user_id=user.id,
                    interaction_type='like',
                    content=comment.content[:100]
                )
            
            logger.info(f"Like {'creado' if created else 'eliminado'}: Usuario {user.id} - Comentario {comment.id}")
            return created  # Return True if liked, False if unliked
            
        except Exception as e:
            logger.error(f"Error toggleando like en comentario: {str(e)}")
            return False
    
    def search_posts_by_similarity(self, query: str, limit: int = 20, similarity_threshold: float = 0.65) -> List[FeedPost]:
        """
        Busca posts usando similitud vectorial semántica con máxima precisión
        
        Args:
            query: Texto de búsqueda
            limit: Número máximo de resultados
            similarity_threshold: Umbral mínimo de similitud (0.0 a 1.0) - valor alto para mayor precisión
            
        Returns:
            Lista de posts ordenados por relevancia semántica
        """
        try:
            # Limpiar y preprocesar el query de manera menos agresiva
            cleaned_query = self._preprocess_search_query_conservative(query)
            if not cleaned_query or len(cleaned_query.strip()) < 2:
                logger.warning(f"Query muy corto o vacío después de limpieza: '{query}' -> '{cleaned_query}'")
                return []
            
            # Obtener embedding del query de búsqueda
            query_embedding = self.get_embedding_from_microservice(cleaned_query)
            
            if not query_embedding:
                logger.warning(f"No se pudo generar embedding para query: {cleaned_query}")
                # Fallback muy limitado y estricto
                return list(FeedPost.objects.filter(
                    is_public=True,
                    content__icontains=cleaned_query
                ).exclude(content__regex=r'^.{0,20}$')  # Excluir posts muy cortos
                .order_by('-created_at')[:min(limit // 3, 5)])  # Muy pocos resultados de fallback
            
            # Convertir embedding a string para la consulta SQL
            embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
            
            # Calcular similitud coseno usando operador <#> de pgvector
            # (1 - (embedding <#> query_embedding)) da la similitud coseno
            similarity_sql = f"(1 - (embedding <#> '{embedding_str}'))"
            
            # Score que prioriza casi completamente la similitud semántica
            score_sql = f"""
                (
                    {similarity_sql} * 0.95 +  -- Máximo peso a similitud semántica
                    (COALESCE(engagement_score, 0) / 1000.0) * 0.03 +  -- Engagement mínimo
                    (1.0 / (1.0 + EXTRACT(EPOCH FROM (NOW() - created_at)) / 2592000.0)) * 0.02  -- Recencia mínima (30 días)
                )
            """
            
            # Query principal con filtros muy estrictos
            queryset = FeedPost.objects.filter(
                is_public=True,
                embedding__isnull=False,  # Solo posts que tienen embedding
                content__isnull=False,    # Solo posts con contenido
            ).exclude(
                content__exact='',        # Excluir posts vacíos
            ).exclude(
                content__regex=r'^.{0,30}$'  # Excluir posts muy cortos (menos de 30 caracteres)
            ).annotate(
                similarity=RawSQL(similarity_sql, []),
                relevance_score=RawSQL(score_sql, [])
            ).filter(
                similarity__gte=similarity_threshold  # Umbral alto por defecto
            ).select_related('author').prefetch_related('post_files').order_by('-similarity', '-relevance_score')  # Priorizar similitud pura
            
            posts = list(queryset[:limit])
            
            logger.info(f"Búsqueda vectorial para '{cleaned_query}': {len(posts)} posts encontrados con similitud >= {similarity_threshold}")
            
            # Solo si realmente no encontramos nada y el query es específico, bajar el umbral
            if len(posts) == 0 and similarity_threshold > 0.5 and len(cleaned_query.split()) >= 2:
                logger.info(f"Sin resultados con umbral alto, intentando con umbral medio para query específico: '{cleaned_query}'")
                additional_posts = self.search_posts_by_similarity(
                    query=query, 
                    limit=min(limit, 10),  # Limitar aún más los resultados con umbral bajo
                    similarity_threshold=0.5
                )
                posts.extend(additional_posts)
            
            # Solo fallback a texto si el query es muy simple y no hay resultados vectoriales
            if len(posts) == 0 and len(cleaned_query.split()) == 1 and len(cleaned_query) > 4:
                logger.info(f"Sin resultados vectoriales para query simple específico, búsqueda de texto limitada: '{cleaned_query}'")
                text_search_posts = list(FeedPost.objects.filter(
                    is_public=True,
                    content__icontains=cleaned_query
                ).order_by('-created_at')[:limit // 2])  # Limitar fallback
                
                posts.extend(text_search_posts)
            
            return posts[:limit]
            
        except Exception as e:
            logger.error(f"Error en búsqueda vectorial: {str(e)}")
            # Fallback mínimo con query limpio
            cleaned_query = self._preprocess_search_query(query)
            return list(FeedPost.objects.filter(
                is_public=True,
                content__icontains=cleaned_query
            ).order_by('-created_at')[:limit // 2])  # Limitar resultados de fallback
    
    def _preprocess_search_query(self, query: str) -> str:
        """
        Preprocesa mínimamente el query - el microservicio ya hace el filtrado y limpieza
        """
        if not query:
            return ""
        
        # Solo normalizar espacios múltiples y quitar espacios al inicio/final
        import re
        cleaned = re.sub(r'\s+', ' ', query.strip())
        
        return cleaned


# Instancia global del servicio
feed_service = FeedService()
