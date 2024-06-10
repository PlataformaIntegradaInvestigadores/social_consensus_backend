from django.urls import path, re_path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from apps.custom_auth.views import *

urlpatterns = [
    path('token/', UserTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='register'),
    re_path(r'^users/(?P<pk>[a-zA-Z0-9]+)/$',
            UserDetailView.as_view(), name='user-detail'),
    re_path(r'^users/(?P<pk>[a-zA-Z0-9]+)/update/$',
            UserUpdateView.as_view(), name='user-update'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('groups/', GroupListCreateView.as_view(), name='group-list-create'),
]
