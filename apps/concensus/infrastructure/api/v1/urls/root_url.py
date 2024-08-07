from django.http import JsonResponse
from django.urls import include, path

from apps.concensus.infrastructure.api.v1.views.final_topic_views import SaveFinalTopicOrderView
from apps.concensus.infrastructure.api.v1.views.notification_views import CombinedSearchView, NotificationListView, NotificationPhaseTwoListView, PhaseOneCompletedView, TopicReorderView, TopicTagView, TopicVisitedView
from apps.concensus.infrastructure.api.v1.views.result_concensus_views import ExecuteConsensusCalculationsView
from apps.concensus.infrastructure.api.v1.views.topic_views import AddTopicView, GroupTopicsView, RandomRecommendedTopicView, RecommendedTopicsByGroupView, TopicsAddedByGroupView
from apps.concensus.infrastructure.api.v1.views.user_expertice_views import UserExpertiseView
from apps.concensus.infrastructure.api.v1.views.user_phase_views import UserCurrentPhaseView
from apps.concensus.infrastructure.api.v1.views.user_satisfaction_views import LoadSatisfactionCountsView, LoadUserSatisfactionNotificationsView, UserSatisfactionView

def test_view(request):
    return JsonResponse({"message": "Test URL of concensus works!"})

urlpatterns=[  
    path('topic/', include('apps.concensus.infrastructure.api.v1.urls.topic_url'), name='topic'),
    path('groups/<str:group_id>/topics/random/', RandomRecommendedTopicView.as_view(), name='random-recommended-topic'),
    path('groups/<str:group_id>/recommended-topics/', RecommendedTopicsByGroupView.as_view(), name='recommended-topics-by-group'),
    path('groups/<str:group_id>/added-topics/', TopicsAddedByGroupView.as_view(), name='topics-added-by-group'),
    path('groups/<str:group_id>/topics/', GroupTopicsView.as_view(), name='group-topics'),
    path('groups/<str:group_id>/add-topic/', AddTopicView.as_view(), name='add-topic'),
    path('groups/<str:group_id>/notifications/', NotificationListView.as_view(), name='group-notifications'),
    path('groups/<str:group_id>/notifications-phase-two/', NotificationPhaseTwoListView.as_view(), name='group-notifications-phase-two'),
    
    path('groups/<str:group_id>/topic-visited/', TopicVisitedView.as_view(), name='topic-visited'),
    path('groups/<str:group_id>/combined-search/', CombinedSearchView.as_view(), name='combined-search'),
    path('groups/<str:group_id>/phase-one-completed/', PhaseOneCompletedView.as_view(), name='phase-one-completed'),
    path('groups/<str:group_id>/user-expertise/', UserExpertiseView.as_view(), name='user-expertise'),

    path('groups/<str:group_id>/topic-reorder/', TopicReorderView.as_view(), name='topic-reorder'),
    path('groups/<str:group_id>/tag-topic/', TopicTagView.as_view(), name='tag-topic'),

    path('groups/<str:group_id>/save-final-topic-order/', SaveFinalTopicOrderView.as_view(), name='save-final-topic-order'),

    path('groups/<str:group_id>/execute_consensus_calculations/', ExecuteConsensusCalculationsView.as_view(), name='execute_consensus_calculations'),
    path('groups/<str:group_id>/user_satisfaction/', UserSatisfactionView.as_view(), name='user_satisfaction'),
    path('groups/<str:group_id>/satisfaction/notifications/', LoadUserSatisfactionNotificationsView.as_view(), name='load-user-satisfaction-notifications'),

    path('groups/<str:group_id>/satisfaction-counts/', LoadSatisfactionCountsView.as_view(), name='satisfaction-counts'),

    path('groups/<str:group_id>/current-phase/', UserCurrentPhaseView.as_view(), name='current-phase'),
]
