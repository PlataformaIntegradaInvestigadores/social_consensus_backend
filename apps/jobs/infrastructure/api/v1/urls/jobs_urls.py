from django.urls import path
from apps.jobs.infrastructure.api.v1.views.jobs_views import JobsView
from apps.jobs.infrastructure.api.v1.views.postulants_views import PostulantsView
from apps.jobs.infrastructure.api.v1.views.recommendations_views import (
    JobRecommendationsView, 
    JobTrendingView, 
    JobSemanticSearchView
)

urlpatterns = [
    # Jobs endpoints
    path('jobs/', JobsView.as_view(), name='jobs-list-create'),
    path('jobs/<int:pk>/', JobsView.as_view(), name='jobs-detail'),
    
    # Job recommendations and search endpoints
    path('jobs/recommendations/', JobRecommendationsView.as_view(), name='jobs-recommendations'),
    path('jobs/trending/', JobTrendingView.as_view(), name='jobs-trending'),
    path('jobs/semantic-search/', JobSemanticSearchView.as_view(), name='jobs-semantic-search'),
    
    # Applications endpoints
    path('applications/', PostulantsView.as_view(), name='applications-list-create'),
    path('applications/<int:pk>/', PostulantsView.as_view(), name='applications-detail'),
]
