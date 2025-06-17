"""
Vistas para manejo de vectores y embeddings de usuario
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.custom_auth.domain.services.user_vector_service import user_vector_service


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_user_job_embedding(request):
    """
    Actualiza el embedding del usuario para recomendaciones de jobs
    """
    try:
        user_id = request.user.id
        
        # Actualizar intereses si se proporcionan
        interests = request.data.get('interests')
        if interests:
            request.user.interests = interests
            request.user.save(update_fields=['interests'])
        
        # Actualizar embedding
        success = user_vector_service.update_user_job_embedding(user_id)
        
        if success:
            return Response({
                'message': 'Embedding de jobs actualizado correctamente',
                'user_id': user_id,
                'timestamp': request.user.profile_vector_updated_at
            })
        else:
            return Response({
                'error': 'No se pudo actualizar el embedding'
            }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({
            'error': f'Error al actualizar embedding: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_user_feed_embedding(request):
    """
    Actualiza el embedding del usuario para recomendaciones de feed
    """
    try:
        user_id = request.user.id
        
        # Actualizar intereses si se proporcionan
        interests = request.data.get('interests')
        if interests:
            request.user.interests = interests
            request.user.save(update_fields=['interests'])
        
        # Actualizar embedding
        success = user_vector_service.update_user_feed_embedding(user_id)
        
        if success:
            return Response({
                'message': 'Embedding de feed actualizado correctamente',
                'user_id': user_id,
                'timestamp': request.user.profile_vector_updated_at
            })
        else:
            return Response({
                'error': 'No se pudo actualizar el embedding'
            }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({
            'error': f'Error al actualizar embedding: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_all_user_embeddings(request):
    """
    Actualiza ambos embeddings del usuario (jobs y feed)
    """
    try:
        user_id = request.user.id
        
        # Actualizar intereses si se proporcionan
        interests = request.data.get('interests')
        if interests:
            request.user.interests = interests
            request.user.save(update_fields=['interests'])
        
        # Actualizar ambos embeddings
        job_success = user_vector_service.update_user_job_embedding(user_id)
        feed_success = user_vector_service.update_user_feed_embedding(user_id)
        
        if job_success and feed_success:
            return Response({
                'message': 'Ambos embeddings actualizados correctamente',
                'user_id': user_id,
                'job_embedding_updated': job_success,
                'feed_embedding_updated': feed_success,
                'timestamp': request.user.profile_vector_updated_at
            })
        elif job_success or feed_success:
            return Response({
                'message': 'Algunos embeddings actualizados',
                'user_id': user_id,
                'job_embedding_updated': job_success,
                'feed_embedding_updated': feed_success,
                'timestamp': request.user.profile_vector_updated_at
            }, status=status.HTTP_206_PARTIAL_CONTENT)
        else:
            return Response({
                'error': 'No se pudieron actualizar los embeddings'
            }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({
            'error': f'Error al actualizar embeddings: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_embedding_status(request):
    """
    Obtiene el estado de los embeddings del usuario
    """
    try:
        user = request.user
        
        return Response({
            'user_id': user.id,
            'has_job_embedding': user.job_recommendations_embedding is not None,
            'has_feed_embedding': user.feed_recommendations_embedding is not None,
            'last_updated': user.profile_vector_updated_at,
            'interaction_count': user.interaction_count,
            'interests': user.interests,
            'job_embedding_dimensions': len(user.job_recommendations_embedding or []),
            'feed_embedding_dimensions': len(user.feed_recommendations_embedding or [])
        })
        
    except Exception as e:
        return Response({
            'error': f'Error al obtener estado: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_user_interests(request):
    """
    Actualiza solo los intereses del usuario sin regenerar embeddings
    """
    try:
        interests = request.data.get('interests')
        
        if not interests:
            return Response({
                'error': 'Campo interests es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        request.user.interests = interests
        request.user.save(update_fields=['interests'])
        
        return Response({
            'message': 'Intereses actualizados correctamente',
            'user_id': request.user.id,
            'interests': interests
        })
        
    except Exception as e:
        return Response({
            'error': f'Error al actualizar intereses: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
