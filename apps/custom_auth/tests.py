from django.test import SimpleTestCase
from django.urls import resolve
from rest_framework import status
from rest_framework.test import APIClient

from apps.custom_auth.infrastructure.api.v1.views.company_views import CompanyRegisterView


class RetiredLegacyIdentityRoutesTests(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()

    def test_researcher_auth_profile_and_group_routes_are_retired(self):
        retired_routes = [
            ("post", "/api/token/"),
            ("post", "/api/token/refresh/"),
            ("post", "/api/register/"),
            ("get", "/api/users/"),
            ("patch", "/api/users/user-1/update/"),
            ("get", "/api/profile-information/"),
            ("put", "/api/profile-information/user-1/"),
            ("get", "/api/groups/"),
            ("delete", "/api/test/user/groups/group-1/delete/"),
            ("post", "/api/test/user/groups/group-1/leave/"),
        ]

        for method, path in retired_routes:
            with self.subTest(path=path, method=method):
                response = getattr(self.client, method)(path, {}, format="json")
                self.assertEqual(response.status_code, status.HTTP_410_GONE)
                self.assertEqual(response.data["canonical_service"], "profile_identity_backend")

    def test_magic_link_legacy_auth_is_retired(self):
        response = self.client.get("/auth/magic-link/")

        self.assertEqual(response.status_code, status.HTTP_410_GONE)
        self.assertEqual(response.data["canonical_service"], "profile_identity_backend")


class CompanyRoutesRemainOwnedBySocialBackendTests(SimpleTestCase):
    def test_company_register_route_is_not_retired(self):
        resolved = resolve("/api/companies/register/")

        self.assertIs(resolved.func.view_class, CompanyRegisterView)
