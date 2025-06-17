from django.urls import path
from apps.jobs.infrastructure.api.v1.views.jobs_views import JobsView
from apps.jobs.infrastructure.api.v1.views.postulants_views import PostulantsView

urlpatterns = [
    # Jobs endpoints
    path('jobs/', JobsView.as_view(), name='jobs-list-create'),
    path('jobs/<int:pk>/', JobsView.as_view(), name='jobs-detail'),
    
    # Applications endpoints
    path('applications/', PostulantsView.as_view(), name='applications-list-create'),
    path('applications/<int:pk>/', PostulantsView.as_view(), name='applications-detail'),
]
