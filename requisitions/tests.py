from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Project, Delivery, Requisition
from users.models import Profile


class RequisitionAppTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.profile = Profile.objects.create(user=self.user, name="Test User")

        self.project = Project.objects.create(
            title="Test Project",
            description="Test description",
            ceua_protocol="CEUA123",
            author=self.profile,
            advisor=self.profile,
        )

        self.requisition = Requisition.objects.create(
            protocol="123.2023",
            date="2023-08-25",
            project=self.project,
            author=self.profile,
        )

        self.delivery = Delivery.objects.create(
            date="2023-08-25", author=self.profile, requisition=self.requisition
        )

    def test_create_project(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            "title": "New Project",
            "description": "New description",
            "ceua_protocol": "NEWCEUA",
            "author": self.profile.id,
            "advisor": self.profile.id,
        }
        response = self.client.post("/api/projects/", payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 2)

    def test_list_projects(self):
        response = self.client.get("/api/projects/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_requisition(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            "protocol": "124.2023",
            "date": "2023-08-26",
            "project": self.project.id,
            "author": self.profile.id,
        }
        response = self.client.post("/api/requisitions/", payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Requisition.objects.count(), 2)

    def test_list_requisitions(self):
        response = self.client.get("/api/requisitions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_delivery(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            "date": "2023-08-26",
            "author": self.profile.id,
            "requisition": self.requisition.protocol,
        }
        response = self.client.post("/api/deliveries/", payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Delivery.objects.count(), 2)

    def test_list_deliveries(self):
        response = self.client.get("/api/deliveries/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)