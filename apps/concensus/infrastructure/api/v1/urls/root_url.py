from django.http import JsonResponse
from django.urls import include, path

from apps.concensus.infrastructure.api.v1.views.topic_views import AddTopicView, GroupTopicsView, RandomRecommendedTopicView, RecommendedTopicsByGroupView, TopicsAddedByGroupView
def test_view(request):
    return JsonResponse({"message": "Test URL of concensus works!"})

urlpatterns=[  
    path('topic/', include('apps.concensus.infrastructure.api.v1.urls.topic_url'), name='topic'),
    path('groups/<str:group_id>/topics/random/', RandomRecommendedTopicView.as_view(), name='random-recommended-topic'),
    path('groups/<str:group_id>/recommended-topics/', RecommendedTopicsByGroupView.as_view(), name='recommended-topics-by-group'),
    path('groups/<str:group_id>/added-topics/', TopicsAddedByGroupView.as_view(), name='topics-added-by-group'),
    path('groups/<str:group_id>/topics/', GroupTopicsView.as_view(), name='group-topics'),
    path('groups/<str:group_id>/add-topic/', AddTopicView.as_view(), name='add-topic'),
]
