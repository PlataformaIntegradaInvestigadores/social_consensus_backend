from django.conf import settings
from rest_framework import status
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.custom_auth.models import Group, ProfileInformation, User


def normalize_contact_info(value):
    if isinstance(value, list):
        return value
    if not value:
        return []
    if isinstance(value, dict):
        if "type" in value and "value" in value:
            return [value]
        return [{"type": key, "value": item} for key, item in value.items() if item]
    return []


class HasInternalSyncToken(BasePermission):
    def has_permission(self, request, view):
        configured_token = getattr(settings, "PROFILE_SYNC_INTERNAL_TOKEN", "")
        provided_token = request.headers.get("X-Internal-Sync-Token", "")
        return bool(configured_token and provided_token == configured_token)


class InternalSyncPermissionMixin:
    permission_classes = [HasInternalSyncToken]
    authentication_classes = []


class UserSyncView(InternalSyncPermissionMixin, APIView):
    def post(self, request):
        payload = request.data.copy()
        user_id = payload.pop("id", None)
        if not user_id:
            return Response({"detail": "id is required"}, status=status.HTTP_400_BAD_REQUEST)

        allowed_fields = {
            "first_name",
            "last_name",
            "username",
            "password",
            "scopus_id",
            "investigation_camp",
            "institution",
            "email_institution",
            "website",
            "profile_picture",
            "is_active",
            "is_staff",
            "interests",
            "interaction_count",
        }
        defaults = {key: value for key, value in payload.items() if key in allowed_fields}
        user, created = User.objects.update_or_create(id=user_id, defaults=defaults)
        return Response({"id": user.id, "created": created})


class ProfileInformationSyncView(InternalSyncPermissionMixin, APIView):
    def post(self, request):
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"detail": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        if request.data.get("deleted"):
            ProfileInformation.objects.filter(user_id=user_id).delete()
            return Response({"user_id": user_id, "deleted": True})

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

        defaults = {
            "about_me": request.data.get("about_me"),
            "disciplines": request.data.get("disciplines") or [],
            "contact_info": normalize_contact_info(request.data.get("contact_info")),
        }
        profile, created = ProfileInformation.objects.update_or_create(user=user, defaults=defaults)
        return Response({"user_id": profile.user_id, "created": created})


class GroupSyncView(InternalSyncPermissionMixin, APIView):
    def post(self, request):
        group_id = request.data.get("id")
        if not group_id:
            return Response({"detail": "id is required"}, status=status.HTTP_400_BAD_REQUEST)

        if request.data.get("deleted"):
            Group.objects.filter(id=group_id).delete()
            return Response({"id": group_id, "deleted": True})

        try:
            admin = User.objects.get(id=request.data.get("admin_id"))
        except User.DoesNotExist:
            return Response({"detail": "Admin user does not exist"}, status=status.HTTP_404_NOT_FOUND)

        defaults = {
            "title": request.data.get("title", ""),
            "description": request.data.get("description", ""),
            "admin": admin,
            "voting_type": request.data.get("voting_type", Group.VotingType.POSITIONAL),
        }
        group, created = Group.objects.update_or_create(id=group_id, defaults=defaults)
        if "users" in request.data:
            group.users.set(User.objects.filter(id__in=request.data.get("users", [])))
        return Response({"id": group.id, "created": created})


class GroupMembershipSyncView(InternalSyncPermissionMixin, APIView):
    def post(self, request):
        group_id = request.data.get("group_id")
        user_ids = request.data.get("users", [])
        if not group_id:
            return Response({"detail": "group_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            return Response({"detail": "Group does not exist"}, status=status.HTTP_404_NOT_FOUND)

        group.users.set(User.objects.filter(id__in=user_ids))
        return Response({"group_id": group.id, "users": list(group.users.values_list("id", flat=True))})
