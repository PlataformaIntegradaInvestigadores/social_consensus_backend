from django.urls import re_path
from apps.concensus.consumer import GroupConsumer

websocket_urlpatterns = [
    re_path(r'ws/groups/(?P<group_id>\w+)/$', GroupConsumer.as_asgi()),
]
