import pytest
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.concensus.domain.entities.topic import Topic


@pytest.mark.integration
class TopicListIntegrationTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_topics_filtered_by_group(self):
        Topic.objects.create(
            name="IA en salud publica",
            group_identity_id="group-1",
            group_snapshot={"id": "group-1", "name": "Grupo Uno", "title": ""},
        )
        Topic.objects.create(
            name="Topic de otro grupo",
            group_identity_id="group-2",
            group_snapshot={"id": "group-2", "name": "Grupo Dos", "title": ""},
        )

        response = self.client.get("/api/v1/topic/", {"group_id": "group-1"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data["data"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "IA en salud publica")
        self.assertEqual(data[0]["group_name"], "Grupo Uno")

    def test_list_topics_empty_for_unknown_group(self):
        Topic.objects.create(
            name="Topic existente",
            group_identity_id="group-1",
            group_snapshot={"id": "group-1", "name": "Grupo Uno", "title": ""},
        )

        response = self.client.get("/api/v1/topic/", {"group_id": "group-does-not-exist"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"], [])
