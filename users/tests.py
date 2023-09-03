from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Institute, Department, Profile
from .serializers import InstituteSerializer, DepartmentSerializer, ProfileSerializer


class InstituteTestCase(TestCase):
    def setUp(self):
        self.institute_data = {
            "name": "Test Institute",
            "abbreviation": "TI",
            "description": "Test description",
        }
        self.institute = Institute.objects.create(**self.institute_data)

    def test_institute_creation(self):
        self.assertEqual(self.institute.name, "Test Institute")
        self.assertEqual(self.institute.abbreviation, "TI")
        self.assertEqual(self.institute.description, "Test description")


class DepartmentTestCase(TestCase):
    def setUp(self):
        self.institute = Institute.objects.create(name="Test Institute")
        self.department_data = {
            "name": "Test Department",
            "institude": self.institute,
            "description": "Test description",
        }
        self.department = Department.objects.create(**self.department_data)

    def test_department_creation(self):
        self.assertEqual(self.department.name, "Test Department")
        self.assertEqual(self.department.institude, self.institute)
        self.assertEqual(self.department.description, "Test description")


class ProfileTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.institute = Institute.objects.create(name="Test Institute")
        self.department = Department.objects.create(
            name="Test Department", institude=self.institute
        )
        self.profile_data = {
            "user": self.user,
            "name": "Test User",
            "is_advisor": True,
            "institute": self.institute,
            "department": self.department,
            "phone": "1234567890",
        }
        self.profile = Profile.objects.create(**self.profile_data)

    def test_profile_creation(self):
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.name, "Test User")
        self.assertTrue(self.profile.is_advisor)
        self.assertEqual(self.profile.institute, self.institute)
        self.assertEqual(self.profile.department, self.department)
        self.assertEqual(self.profile.phone, "1234567890")


class InstituteViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.institute_data = {
            "name": "Test Institute",
            "abbreviation": "TI",
            "description": "Test description",
        }
        self.institute = Institute.objects.create(**self.institute_data)

    def test_get_all_institutes(self):
        response = self.client.get("/api/institutes/")
        institutes = Institute.objects.all()
        serializer = InstituteSerializer(institutes, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)


class DepartmentViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.institute = Institute.objects.create(name="Test Institute")
        self.department_data = {
            "name": "Test Department",
            "institude": self.institute,
            "description": "Test description",
        }
        self.department = Department.objects.create(**self.department_data)

    def test_get_all_departments(self):
        response = self.client.get("/api/departments/")
        departments = Department.objects.all()
        serializer = DepartmentSerializer(departments, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)


class ProfileViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.institute = Institute.objects.create(name="Test Institute")
        self.department = Department.objects.create(
            name="Test Department", institude=self.institute
        )
        self.profile_data = {
            "user": self.user,
            "name": "Test User",
            "is_advisor": True,
            "institute": self.institute,
            "department": self.department,
            "phone": "1234567890",
        }
        self.profile = Profile.objects.create(**self.profile_data)

    def test_get_all_profiles_as_staff(self):
        self.client.force_login(self.user)
        response = self.client.get("/api/profiles/")
        profiles = Profile.objects.all().exclude(is_hidden=True)
        serializer = ProfileSerializer(profiles, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
