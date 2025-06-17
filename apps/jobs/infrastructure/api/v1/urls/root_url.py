from django.urls import path, include

from apps.jobs.infrastructure.api.v1.views.jobs_views import JobsView
from apps.jobs.infrastructure.api.v1.views.postulants_views import PostulantsView

urlpatterns = [
    path('jobs/', JobsView.as_view(), name='jobs'),
    path('postulants/', PostulantsView.as_view(), name='postulants'),
    
    # Sistema de recomendaciones
    path('jobs/', include('apps.jobs.infrastructure.api.v1.urls.recommendation_urls')),
]
