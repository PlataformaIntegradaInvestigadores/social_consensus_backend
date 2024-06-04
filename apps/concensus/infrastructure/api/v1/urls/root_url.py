from django.urls import include, path


urlpatterns=[  
    path('topic/', include('apps.concensus.infrastructure.api.v1.urls.topic_url'), name='topic'),
]