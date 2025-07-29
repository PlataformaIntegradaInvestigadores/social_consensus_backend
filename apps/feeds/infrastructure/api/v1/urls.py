from django.urls import path, include

# Import individual URL modules
from .urls.feed_post_urls import urlpatterns as post_patterns
from .urls.comment_urls import urlpatterns as comment_patterns
from .urls.like_urls import urlpatterns as like_patterns
from .urls.feed_urls import urlpatterns as feed_patterns
from .urls.poll_urls import urlpatterns as poll_patterns

app_name = 'feeds_v1'

# Combine all URL patterns
urlpatterns = []
urlpatterns.extend(post_patterns)
urlpatterns.extend(comment_patterns)
urlpatterns.extend(like_patterns)
urlpatterns.extend(feed_patterns)
urlpatterns.extend(poll_patterns)
