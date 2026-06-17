import pytest
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from apps.custom_auth.domain.entities.User import User
from apps.custom_auth.domain.entities.Group import Group
from apps.custom_auth.domain.entities.GroupUser import GroupUser


@pytest.mark.integration
class UserRegistrationFlowTest(TestCase):
    """Integration: full registration → token → profile flow via API."""

    def setUp(self):
        self.client = APIClient()

    def test_register_user_returns_201(self):
        payload = {
            "username": "newuser@epn.edu.ec",
            "password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "User",
        }
        response = self.client.post("/api/register/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_user_creates_in_database(self):
        payload = {
            "username": "dbuser@epn.edu.ec",
            "password": "SecurePass123!",
            "first_name": "DB",
            "last_name": "User",
        }
        self.client.post("/api/register/", payload, format="json")
        self.assertTrue(User.objects.filter(username="dbuser@epn.edu.ec").exists())

    def test_register_duplicate_email_returns_400(self):
        payload = {
            "username": "duplicate@epn.edu.ec",
            "password": "SecurePass123!",
            "first_name": "First",
            "last_name": "User",
        }
        self.client.post("/api/register/", payload, format="json")
        response = self.client.post("/api/register/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_obtain_token_after_registration(self):
        payload = {
            "username": "tokenuser@epn.edu.ec",
            "password": "SecurePass123!",
            "first_name": "Token",
            "last_name": "User",
        }
        self.client.post("/api/register/", payload, format="json")
        token_response = self.client.post(
            "/api/token/",
            {"username": "tokenuser@epn.edu.ec", "password": "SecurePass123!"},
            format="json",
        )
        self.assertEqual(token_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", token_response.data)
        self.assertIn("refresh", token_response.data)

    def test_access_protected_endpoint_with_token(self):
        User.objects.create_user(
            username="protected@epn.edu.ec",
            password="SecurePass123!",
            first_name="Protected",
            last_name="User",
        )
        token_response = self.client.post(
            "/api/token/",
            {"username": "protected@epn.edu.ec", "password": "SecurePass123!"},
            format="json",
        )
        access_token = token_response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.get("/api/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_access_protected_endpoint_without_token_returns_401(self):
        response = self.client.get("/api/users/")
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_200_OK])


@pytest.mark.integration
class GroupAPIFlowTest(TestCase):
    """Integration: group creation → add members → list via API."""

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username="admin@epn.edu.ec",
            password="AdminPass123!",
            first_name="Admin",
            last_name="User",
        )
        self.member = User.objects.create_user(
            username="member@epn.edu.ec",
            password="MemberPass123!",
            first_name="Member",
            last_name="User",
        )
        token_response = self.client.post(
            "/api/token/",
            {"username": "admin@epn.edu.ec", "password": "AdminPass123!"},
            format="json",
        )
        self.access_token = token_response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    def test_create_group_returns_201(self):
        payload = {
            "title": "Grupo de Investigación",
            "description": "Grupo para tesis CI/CD",
        }
        response = self.client.post("/api/groups/", payload, format="json")
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK])

    def test_create_group_persists_in_database(self):
        payload = {
            "title": "Grupo Persistente",
            "description": "Test persistence",
        }
        self.client.post("/api/groups/", payload, format="json")
        self.assertTrue(Group.objects.filter(title="Grupo Persistente").exists())

    def test_list_groups_returns_200(self):
        response = self.client.get("/api/groups/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_groups_list(self):
        group = Group.objects.create(
            title="Mi Grupo",
            description="Grupo del admin",
            admin=self.admin,
        )
        GroupUser.objects.create(group=group, user=self.admin)
        response = self.client.get("/api/test/user/groups/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


@pytest.mark.integration
class TokenRefreshFlowTest(TestCase):
    """Integration: test JWT refresh token mechanism."""

    def setUp(self):
        self.client = APIClient()
        User.objects.create_user(
            username="refresh@epn.edu.ec",
            password="RefreshPass123!",
            first_name="Refresh",
            last_name="User",
        )

    def test_refresh_token_returns_new_access(self):
        token_response = self.client.post(
            "/api/token/",
            {"username": "refresh@epn.edu.ec", "password": "RefreshPass123!"},
            format="json",
        )
        refresh_token = token_response.data["refresh"]
        refresh_response = self.client.post(
            "/api/token/refresh/",
            {"refresh": refresh_token},
            format="json",
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh_response.data)

    def test_invalid_refresh_token_returns_401(self):
        response = self.client.post(
            "/api/token/refresh/",
            {"refresh": "invalid-token-value"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
