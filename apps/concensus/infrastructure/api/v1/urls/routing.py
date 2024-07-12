from django.urls import re_path
from apps.concensus.consumer import GroupConsumer
from apps.concensus.consumer_phase_two import PhaseTwoConsumer
from apps.concensus.consumer_phase_three import PhaseThreeConsumer

websocket_urlpatterns = [
    re_path(r'ws/groups/(?P<group_id>\w+)/$', GroupConsumer.as_asgi()),
    re_path(r'ws/phase2/groups/(?P<group_id>\w+)/$', PhaseTwoConsumer.as_asgi()),
    re_path(r'ws/phase3/groups/(?P<group_id>\w+)/$', PhaseThreeConsumer.as_asgi()),
]
