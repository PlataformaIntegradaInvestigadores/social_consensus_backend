from django.http import JsonResponse
from django.urls import path, re_path
from rest_framework_simplejwt.views import TokenRefreshView
from apps.custom_auth.infrastructure.api.v1.views.group_views import GroupDeleteView, GroupDetailView, GroupLeaveView, UserDetailViewtoGroup, UserGroupsListView
from apps.custom_auth.views import *

def test_view(request):
    return JsonResponse({"message": "Test URL works!"})



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
     path('profile-information/', ProfileInformationDetailView.as_view(),
         name='profile-information-detail'),
     path('profile-information/<str:user__id>/', PublicProfileInformationDetailView.as_view(),
         name='public-profile-information-detail'),
     path('posts/', PostListView.as_view(), name='post-list'),
     path('posts/create/', PostCreateView.as_view(), name='post-create'),
     path('posts/<pk>/delete/', PostDeleteView.as_view(),
         name='post-delete'),  # URL para eliminar post
     
     # Nueva ruta para listar grupos del usuario autenticado
     #path('test/user/groups/', UserGroupsListView.as_view(), name='user-groups-list'),
     
     # Ruta temporal para pruebas
     path('test/user/groups/', UserGroupsListView.as_view(), name='test-user-groups-list'),
     #path('test/', test_view, name='test-view'),  # Ruta de prueba básica


    path('test/user/groups/<pk>/delete/', GroupDeleteView.as_view(), name='group-delete'),
    path('test/user/groups/<pk>/leave/', GroupLeaveView.as_view(), name='group-leave'),

    path('test/users/groups/<str:pk>/', UserDetailViewtoGroup.as_view(), name='user-detail'),

    path('groups/<str:pk>/', GroupDetailView.as_view(), name='group-detail'),

]
