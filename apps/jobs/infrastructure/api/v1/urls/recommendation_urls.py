"""
URLs para el sistema de recomendaciones de jobs
"""
from django.urls import path
from apps.jobs.infrastructure.api.v1.recommendation_views import (
    get_job_recommendations,
    get_trending_jobs,
    track_job_interaction,
    update_job_embedding
)

urlpatterns = [
    # Recomendaciones personalizadas
    path('recommendations/', get_job_recommendations, name='job_recommendations'),
    
    # Jobs en tendencia
    path('trending/', get_trending_jobs, name='trending_jobs'),
    
    # Tracking de interacciones
    path('<int:job_id>/interaction/', track_job_interaction, name='track_job_interaction'),
    
    # Actualización de embeddings
    path('<int:job_id>/update-embedding/', update_job_embedding, name='update_job_embedding'),
]
