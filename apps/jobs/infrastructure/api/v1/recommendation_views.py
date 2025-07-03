"""
Vistas para el sistema de recomendaciones de jobs
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from django.http import JsonResponse
from typing import List

from apps.jobs.domain.entities.jobs import Jobs
from apps.jobs.domain.services.vector_recommendation_service import vector_service
from apps.jobs.infrastructure.api.v1.serializers import JobsSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_job_recommendations(request):
    """
    Obtiene recomendaciones de jobs para el usuario actual basadas en embeddings
    Si no hay embedding de usuario, devuelve jobs trending como fallback
    """
    try:
        # Parámetros de consulta
        limit = int(request.GET.get('limit', 10))
        user_id = request.user.id
        
        # Intentar obtener el embedding del usuario
        user_embedding = get_user_embedding_vector(user_id)
        
        # Usar el método mejorado que incluye fallback automático
        recommended_jobs = vector_service.get_similar_jobs(
            user_embedding=user_embedding,
            limit=limit,
            exclude_job_ids=[],
            similarity_threshold=0.4  # Threshold más bajo para más resultados
        )
        
        # Serializar los resultados
        serializer = JobsSerializer(recommended_jobs, many=True)
        
        # Agregar información adicional de recomendación
        recommendations_data = []
        for job_data, job_instance in zip(serializer.data, recommended_jobs):
            recommendation_info = {
                **job_data,
                'recommendation_score': getattr(job_instance, 'recommendation_score', 0.5),
                'similarity': getattr(job_instance, 'similarity', 0.5),
                'hours_old': getattr(job_instance, 'hours_old', 0),
                'recommendation_reason': get_recommendation_reason(job_instance),
                'is_fallback': not user_embedding  # Indica si es fallback por falta de embedding
            }
            recommendations_data.append(recommendation_info)
        
        return Response({
            'recommendations': recommendations_data,
            'total_count': len(recommendations_data),
            'user_id': user_id,
            'has_user_embedding': bool(user_embedding),
            'recommendation_type': 'vectorial' if user_embedding else 'trending_fallback'
        })
        
    except Exception as e:
        return Response({
            'error': f'Error al obtener recomendaciones: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_trending_jobs(request):
    """
    Obtiene jobs en tendencia basados en interacciones recientes
    """
    try:
        limit = int(request.GET.get('limit', 10))
        
        trending_jobs = vector_service.get_trending_jobs(limit=limit)
        serializer = JobsSerializer(trending_jobs, many=True)
        
        # Agregar información de trending
        trending_data = []
        for job_data, job_instance in zip(serializer.data, trending_jobs):
            trending_info = {
                **job_data,
                'trending_score': float(job_instance.trending_score),
                'hours_old': float(job_instance.hours_old),
                'view_count': job_instance.view_count,
                'application_count': job_instance.application_count
            }
            trending_data.append(trending_info)
        
        return Response({
            'trending_jobs': trending_data,
            'total_count': len(trending_data)
        })
        
    except Exception as e:
        return Response({
            'error': f'Error al obtener jobs en tendencia: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def track_job_interaction(request, job_id):
    """
    Registra una interacción del usuario con un job (view, application, etc.)
    """
    try:
        interaction_type = request.data.get('interaction_type', 'view')
        
        if interaction_type not in ['view', 'application']:
            return Response({
                'error': 'Tipo de interacción inválido. Usar: view, application'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar que el job existe
        try:
            job = Jobs.objects.get(id=job_id)
        except Jobs.DoesNotExist:
            return Response({
                'error': 'Job no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Registrar la interacción
        vector_service.update_job_interactions(job_id, interaction_type)
        
        return Response({
            'message': f'Interacción {interaction_type} registrada correctamente',
            'job_id': job_id,
            'interaction_type': interaction_type
        })
        
    except Exception as e:
        return Response({
            'error': f'Error al registrar interacción: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_job_embedding(request, job_id):
    """
    Actualiza el embedding de un job específico
    Solo accesible para usuarios autorizados (empresas propietarias o admins)
    """
    try:
        # Verificar que el job existe y el usuario tiene permiso
        try:
            job = Jobs.objects.get(id=job_id)
            
            # Verificar permisos (ajustar según tu lógica de permisos)
            if not (request.user.is_staff or 
                   (hasattr(request.user, 'company') and request.user.company == job.company)):
                return Response({
                    'error': 'No tienes permisos para actualizar este job'
                }, status=status.HTTP_403_FORBIDDEN)
                
        except Jobs.DoesNotExist:
            return Response({
                'error': 'Job no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Actualizar el embedding
        success = vector_service.update_job_embedding(job)
        
        if success:
            return Response({
                'message': 'Embedding actualizado correctamente',
                'job_id': job_id,
                'job_title': job.title
            })
        else:
            return Response({
                'error': 'No se pudo actualizar el embedding'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    except Exception as e:
        return Response({
            'error': f'Error al actualizar embedding: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_user_embedding_vector(user_id: int) -> List[float]:
    """
    Obtiene el vector embedding del usuario desde el microservicio
    
    En producción, esto debería conectarse a tu microservicio de perfiles
    Por ahora retorna un vector de ejemplo
    """
    # TODO: Implementar conexión real al microservicio de perfiles de usuario
    # Ejemplo de cómo sería:
    # user_profile_text = get_user_profile_text(user_id)  # CV, habilidades, experiencia, etc.
    # payload = {
    #     "text": user_profile_text,
    #     "translate_to_english": True,
    #     "clean_text": True
    # }
    # response = requests.post(f"{settings.EMBEDDING_SERVICE_URL}/text-processing/vectorize/", json=payload)
    # return response.json().get('vector')
    
    # Vector de ejemplo (768 dimensiones con valores aleatorios normalizados)
    import random
    return [random.uniform(-1, 1) for _ in range(768)]


def get_recommendation_reason(job_instance) -> str:
    """
    Genera una explicación del por qué se recomienda este job
    """
    similarity = float(job_instance.similarity)
    interactions = job_instance.interactions_score
    
    if similarity > 0.8:
        return "Muy similar a tu perfil profesional"
    elif similarity > 0.7:
        return "Coincide con tus habilidades"
    elif interactions > 5.0:
        return "Popular entre profesionales similares"
    elif job_instance.hours_old < 24:
        return "Publicación reciente"
    else:
        return "Podría interesarte"
