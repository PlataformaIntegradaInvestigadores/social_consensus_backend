"""
Servicio principal para manejo de trabajos con embeddings y recomendaciones
"""
import requests
import logging
from typing import List, Optional, Dict, Any
from django.db.models import QuerySet, F, Q
from django.db.models.expressions import RawSQL
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

# Importar modelos de jobs
from apps.jobs.domain.entities.jobs import Jobs
from apps.jobs.domain.services.vector_recommendation_service import VectorRecommendationService

# Importar servicio de vectores de usuario si existe
try:
    from apps.custom_auth.domain.services.user_vector_service import user_vector_service
except ImportError:
    user_vector_service = None

logger = logging.getLogger(__name__)


class JobsService:
    """
    Servicio principal para manejo de trabajos con recomendaciones y búsqueda semántica
    """
    
    def __init__(self, embedding_service_url: str = None):
        self.embedding_service_url = embedding_service_url or settings.EMBEDDING_SERVICE_URL
        self.vector_service = VectorRecommendationService(embedding_service_url)
    
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
                    logger.info(f"Embedding generado para texto. Dimensiones: {result.get('dimension', len(vector))}")
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
    
    def update_job_embedding(self, job_id: int) -> bool:
        """
        Actualiza el embedding de un trabajo
        """
        try:
            job = Jobs.objects.get(id=job_id)
            
            # Generar texto para embedding
            embedding_text = self._generate_job_embedding_text(job)
            
            # Obtener embedding
            embedding = self.get_embedding_from_microservice(embedding_text)
            
            if embedding:
                job.embedding = embedding
                job.save(update_fields=['embedding'])
                logger.info(f"Embedding actualizado para job {job_id}")
                return True
            else:
                logger.error(f"No se pudo generar embedding para job {job_id}")
                return False
                
        except Jobs.DoesNotExist:
            logger.error(f"Job {job_id} no encontrado")
            return False
        except Exception as e:
            logger.error(f"Error actualizando embedding: {str(e)}")
            return False
    
    def _generate_job_embedding_text(self, job: Jobs) -> str:
        """
        Genera texto completo del trabajo para crear embedding
        """
        text_parts = []
        
        # Título del trabajo
        if job.title:
            text_parts.append(f"Puesto: {job.title}")
        
        # Descripción
        if job.description:
            text_parts.append(f"Descripción: {job.description}")
        
        # Requisitos
        if job.requirements:
            text_parts.append(f"Requisitos: {job.requirements}")
        
        # Beneficios
        if job.benefits:
            text_parts.append(f"Beneficios: {job.benefits}")
        
        # Información adicional
        if job.location:
            text_parts.append(f"Ubicación: {job.location}")
        
        if job.job_type:
            text_parts.append(f"Tipo: {job.get_job_type_display_name()}")
        
        if job.experience_level:
            text_parts.append(f"Experiencia: {job.get_experience_display_name()}")
        
        if job.is_remote:
            text_parts.append("Trabajo remoto disponible")
        
        # Información de la empresa
        if job.company and job.company.company_name:
            text_parts.append(f"Empresa: {job.company.company_name}")
        
        if job.company and job.company.industry:
            text_parts.append(f"Industria: {job.company.industry}")
        
        return ". ".join(text_parts)
    
    def get_personalized_job_recommendations(self, user=None, user_id: str = None, limit: int = 20) -> QuerySet:
        """
        Obtiene recomendaciones personalizadas de trabajos basadas en el perfil del usuario
        """
        try:
            if user:
                user_id = str(user.id)
            logger.info(f"Obteniendo recomendaciones de trabajos para usuario {user_id}")
            logger.info("Usando recomendaciones basicas sin consultar custom_auth.User local")
            return self._get_basic_recommendations(None, limit)

            # Permitir usar tanto user_id como objeto user
            if user:
                user_obj = user
                user_id = str(user.id)
            else:
                user_obj = None
            
            logger.info(f"Obteniendo recomendaciones de trabajos para usuario {user_id}")
            
            # Verificar si el usuario tiene embedding para recomendaciones
            if hasattr(user_obj, 'job_recommendations_embedding') and user_obj.job_recommendations_embedding:
                # Usar embedding del usuario para recomendaciones
                user_embedding = user_obj.job_recommendations_embedding
                return self._get_vector_based_recommendations(user_embedding, limit)
            else:
                # Si no hay embedding, usar recomendaciones básicas
                logger.info(f"Usuario {user_id} sin embedding, usando recomendaciones básicas")
                return self._get_basic_recommendations(user_obj, limit)
                
        except NameError:
            logger.error(f"Usuario {user_id} no encontrado")
            return Jobs.objects.none()
        except Exception as e:
            logger.error(f"Error obteniendo recomendaciones: {str(e)}")
            return self._get_basic_recommendations(user_obj if 'user_obj' in locals() else None, limit)
    
    def _get_vector_based_recommendations(self, user_embedding: List[float], limit: int) -> QuerySet:
        """
        Obtiene recomendaciones basadas en similitud de vectores
        """
        try:
            embedding_str = '[' + ','.join(map(str, user_embedding)) + ']'
            
            # Calcular similitud coseno (1 - distancia coseno)
            similarity_sql = f"(1 - (embedding <#> '{embedding_str}'))"
            
            # Score compuesto: similitud + popularidad + recencia
            hours_old_sql = "EXTRACT(EPOCH FROM (NOW() - created_at)) / 3600"
            
            composite_score_sql = f"""
                (
                    ({similarity_sql}) * 0.6 +
                    (LEAST(view_count, 100) / 100.0) * 0.2 +
                    (LEAST(application_count, 50) / 50.0) * 0.1 +
                    (1.0 / (1.0 + ({hours_old_sql}) / 168.0)) * 0.1
                )
            """
            
            queryset = Jobs.objects.filter(
                embedding__isnull=False
            ).annotate(
                similarity=RawSQL(similarity_sql, []),
                composite_score=RawSQL(composite_score_sql, [])
            ).order_by('-composite_score')[:limit]
            
            logger.info(f"Recomendaciones vectoriales generadas: {queryset.count()} trabajos")
            return queryset
            
        except Exception as e:
            logger.error(f"Error en recomendaciones vectoriales: {str(e)}")
            return Jobs.objects.all().order_by('-created_at')[:limit]
    
    def _get_basic_recommendations(self, user, limit: int) -> QuerySet:
        """
        Obtiene recomendaciones básicas cuando no hay embeddings disponibles
        """
        base_queryset = Jobs.objects.all()
        
        # Combinar trabajos populares y recientes
        popular_weight = 0.6
        recent_weight = 0.4
        
        popular_limit = int(limit * popular_weight)
        recent_limit = limit - popular_limit
        
        # Trabajos populares
        popular_jobs = base_queryset.order_by(
            '-view_count', '-application_count', '-created_at'
        )[:popular_limit]
        
        # Trabajos recientes
        recent_jobs = base_queryset.order_by('-created_at')[:recent_limit]
        
        # Combinar y eliminar duplicados manteniendo el orden
        job_ids = []
        for job in popular_jobs:
            if job.id not in job_ids:
                job_ids.append(job.id)
        
        for job in recent_jobs:
            if job.id not in job_ids and len(job_ids) < limit:
                job_ids.append(job.id)
        
        # Retornar queryset ordenado
        return Jobs.objects.filter(id__in=job_ids).order_by('-view_count', '-created_at')
    
    def get_trending_jobs(self, limit: int = 20) -> QuerySet:
        """
        Obtiene trabajos trending basados en interacciones recientes
        """
        try:
            # Trabajos de los últimos 30 días
            recent_date = timezone.now() - timedelta(days=30)
            
            # Score de trending basado en interacciones recientes
            trending_score_sql = """
                (
                    (view_count * 1.0) +
                    (application_count * 3.0) +
                    (EXTRACT(EPOCH FROM (NOW() - created_at)) / 86400.0) * -0.1
                )
            """
            
            # DEBUG: Verificar cuántos jobs hay en total
            total_jobs = Jobs.objects.count()
            logger.info(f"DEBUG: Total jobs en DB: {total_jobs}")
            
            queryset = Jobs.objects.filter(
                created_at__gte=recent_date
            ).annotate(
                trending_score=RawSQL(trending_score_sql, [])
            ).order_by('-trending_score')[:limit]
            
            logger.info(f"DEBUG: Jobs trending query count: {queryset.count()}")
            
            # Si no hay jobs recientes, mostrar todos los disponibles
            if not queryset.exists():
                logger.info("DEBUG: No hay jobs recientes, obteniendo todos")
                queryset = Jobs.objects.all().annotate(
                    trending_score=RawSQL(trending_score_sql, [])
                ).order_by('-trending_score')[:limit]
                logger.info(f"DEBUG: Jobs todos query count: {queryset.count()}")
            
            logger.info(f"Trabajos trending generados: {queryset.count()}")
            return queryset
            
        except Exception as e:
            logger.error(f"Error obteniendo trabajos trending: {str(e)}")
            return Jobs.objects.all().order_by('-view_count', '-created_at')[:limit]
    
    def semantic_search_jobs(self, query: str, filters: Dict[str, Any] = None, limit: int = 20, user=None) -> QuerySet:
        """
        Búsqueda semántica de trabajos usando embeddings
        """
        try:
            # Obtener embedding de la consulta
            query_embedding = self.get_embedding_from_microservice(query)
            
            if not query_embedding:
                # Fallback a búsqueda textual
                logger.warning("No se pudo obtener embedding, usando búsqueda textual")
                return self._text_search_jobs(query, filters, limit)
            
            # Búsqueda por similitud de vectores
            embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
            similarity_sql = f"(1 - (embedding <#> '{embedding_str}'))"
            
            queryset = Jobs.objects.filter(
                embedding__isnull=False
            )
            
            # Aplicar filtros
            if filters:
                queryset = self._apply_filters(queryset, filters)
            
            # Ordenar por similitud
            queryset = queryset.annotate(
                similarity=RawSQL(similarity_sql, [])
            ).order_by('-similarity')[:limit]
            
            logger.info(f"Búsqueda semántica completada: {queryset.count()} resultados")
            
            # Registrar interacción de búsqueda si hay usuario
            if user and user_vector_service:
                user_vector_service.update_user_vectors_on_interaction(
                    user_id=str(user.id),
                    interaction_type='job_search',
                    content=query
                )
            
            return queryset
            
        except Exception as e:
            logger.error(f"Error en búsqueda semántica: {str(e)}")
            return self._text_search_jobs(query, filters, limit)
    
    def _text_search_jobs(self, query: str, filters: Dict[str, Any] = None, limit: int = 20) -> QuerySet:
        """
        Búsqueda textual fallback cuando no hay embeddings disponibles
        """
        queryset = Jobs.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(requirements__icontains=query) |
            Q(company__company_name__icontains=query)
        )
        
        # Aplicar filtros
        if filters:
            queryset = self._apply_filters(queryset, filters)
        
        return queryset.order_by('-created_at')[:limit]
    
    def _apply_filters(self, queryset: QuerySet, filters: Dict[str, Any]) -> QuerySet:
        """
        Aplica filtros al queryset de trabajos
        """
        if filters.get('is_remote') is not None:
            queryset = queryset.filter(is_remote=filters['is_remote'])
        
        if filters.get('job_type'):
            if isinstance(filters['job_type'], list):
                queryset = queryset.filter(job_type__in=filters['job_type'])
            else:
                queryset = queryset.filter(job_type=filters['job_type'])
        
        if filters.get('experience_level'):
            if isinstance(filters['experience_level'], list):
                queryset = queryset.filter(experience_level__in=filters['experience_level'])
            else:
                queryset = queryset.filter(experience_level=filters['experience_level'])
        
        if filters.get('salary_min'):
            queryset = queryset.filter(salary_min__gte=filters['salary_min'])
        
        if filters.get('salary_max'):
            queryset = queryset.filter(salary_max__lte=filters['salary_max'])
        
        if filters.get('location'):
            queryset = queryset.filter(location__icontains=filters['location'])
        
        if filters.get('company'):
            queryset = queryset.filter(company__company_name__icontains=filters['company'])
        
        return queryset
    
    def handle_job_interaction(self, user, job: Jobs, interaction_type: str = 'view'):
        """
        Maneja las interacciones del usuario con trabajos
        """
        try:
            # Incrementar contadores
            if interaction_type == 'view':
                Jobs.objects.filter(id=job.id).update(view_count=F('view_count') + 1)
            elif interaction_type == 'application':
                Jobs.objects.filter(id=job.id).update(application_count=F('application_count') + 1)
            
            # Actualizar vectores del usuario si el servicio está disponible
            if user_vector_service:
                user_vector_service.update_user_vectors_on_interaction(
                    user_id=str(user.id),
                    interaction_type=f'job_{interaction_type}',
                    content=self._generate_job_embedding_text(job)
                )
            
            logger.info(f"Interacción registrada: {interaction_type} en job {job.id} por usuario {user.id}")
            
        except Exception as e:
            logger.error(f"Error registrando interacción: {str(e)}")
