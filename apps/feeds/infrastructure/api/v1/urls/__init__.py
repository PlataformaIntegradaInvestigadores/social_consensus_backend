from .feed_post_urls import urlpatterns as post_patterns
from .comment_urls import urlpatterns as comment_patterns
from .like_urls import urlpatterns as like_patterns
from .feed_urls import urlpatterns as feed_patterns

urlpatterns = []
urlpatterns.extend(post_patterns)
urlpatterns.extend(comment_patterns)
urlpatterns.extend(like_patterns)
urlpatterns.extend(feed_patterns)
