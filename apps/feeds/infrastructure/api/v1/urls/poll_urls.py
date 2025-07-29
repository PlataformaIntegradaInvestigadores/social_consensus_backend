from django.urls import path
from apps.feeds.infrastructure.api.v1.views.poll_views import (
    vote_poll,
    remove_vote,
    get_poll_details
)

urlpatterns = [
    # Polls
    path('polls/<str:poll_id>/', get_poll_details, name='poll-detail'),
    path('polls/<str:poll_id>/vote/', vote_poll, name='poll-vote'),
    path('polls/<str:poll_id>/remove-vote/', remove_vote, name='poll-remove-vote'),
]
