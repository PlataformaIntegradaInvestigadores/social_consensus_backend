from django.urls import path

from apps.custom_auth.infrastructure.api.v1.views.profile_sync_views import (
    GroupMembershipSyncView,
    GroupSyncView,
    ProfileInformationSyncView,
    UserSyncView,
)


urlpatterns = [
    path("users/", UserSyncView.as_view(), name="profile-sync-users"),
    path("profile-information/", ProfileInformationSyncView.as_view(), name="profile-sync-profile-information"),
    path("groups/", GroupSyncView.as_view(), name="profile-sync-groups"),
    path("group-memberships/", GroupMembershipSyncView.as_view(), name="profile-sync-group-memberships"),
]
