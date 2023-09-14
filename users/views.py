from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import OrderingFilter

from django.contrib.auth.models import User

from .models import Profile, Institute, Department
from .serializers import (
    UserAuthenticationSerializer,
    ProfileSerializer,
    UserSerializer,
    TokenValidationSerializer,
    InstituteSerializer,
    DepartmentSerializer,
)
from .utils.utils import generate_random_password, generate_random_username


class InstituteViewSet(viewsets.ModelViewSet):
    queryset = Institute.objects.all()
    serializer_class = InstituteSerializer
    filter_backends = [SearchFilter]
    search_fields = ["name", "abbreviation"]
    pagination_class = None


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    filter_backends = [SearchFilter]
    search_fields = ["name"]
    pagination_class = None

    def create(self, request):
        institute_received = request.data["institute"]
        institute = Institute.objects.get(name=institute_received)

        data = {
            **request.data,
            "institute": institute.pk
        }

        department_serializer = DepartmentSerializer(data=data)

        if department_serializer.is_valid():
            department_serializer.save()

            return Response(department_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["name"] 

    def get_queryset(self):
        queryset = Profile.objects.all().exclude(is_hidden=True)
        queryset = queryset.order_by("name")

        return queryset

    def partial_update(self, request, *args, **kwargs):
        user_id = request.data.get("id")
        email = request.data.get("email")
        is_staff = request.data.get("isStaff", False)
        is_advisor = request.data.get("isAdvisor", False)

        institute = Institute.objects.get(name=request.data["institute"])
        department = Department.objects.get(name=request.data["department"])

        try:
            profile_instance = Profile.objects.get(id=user_id)
            profile_instance.is_advisor = is_advisor
            profile_instance.institute = institute
            profile_instance.department = department
            profile_instance.save()

            user_instance = User.objects.get(id=profile_instance.user.id)
            user_instance.email = email
            user_instance.is_staff = is_staff
            user_instance.save()

            kwargs["partial"] = True
            return self.update(request, *args, **kwargs)

        except (Profile.DoesNotExist, User.DoesNotExist) as e:
            return Response(
                {"error": "Profile or User not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def create(self, request):
        if not request.data.get("username"):
            request.data["username"] = generate_random_username(random_suffix_length=12)

        if not request.data.get("password"):
            request.data["password"] = generate_random_password(
                random_password_length=12
            )

        is_staff = request.data.get("isStaff", False)
        is_advisor = request.data.get("isAdvisor", False)

        user_serializer = UserSerializer(data=request.data)
        user_serializer.is_valid(raise_exception=True)
        user_instance = user_serializer.save()
        user_instance.is_staff = is_staff
        user_instance.save()

        institute = Institute.objects.get(name=request.data["institute"])
        department = Department.objects.get(name=request.data["department"])

        profile_data = {
            **request.data,
            "user": user_instance,
            "is_advisor": is_advisor,
            "department": department,
            "institute": institute,
        }

        profile_serializer = ProfileSerializer(data=profile_data)

        if profile_serializer.is_valid():
            profile_serializer.save(
                user=user_instance, institute=institute, department=department
            )
            return Response(profile_serializer.data, status=status.HTTP_201_CREATED)

        return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(Profile.objects.all().exclude(is_hidden=True))

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class UserAuthenticationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        serializer = UserAuthenticationSerializer(data=request.data)

        if serializer.is_valid():
            profile = serializer.validated_data
            token, created = Token.objects.get_or_create(user=profile.user)

            return Response(
                {
                    "success": True,
                    "message": "Autenticação válida.",
                    "token": token.key,
                    "user": profile.user.username,
                    "name": profile.name,
                }
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenVerifierView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        serializer = TokenValidationSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            token = serializer.validated_data
            fetched_token = Token.objects.filter(key=token).first()

            if fetched_token:
                return Response(
                    {
                        "success": True,
                        "message": "Token válido.",
                        "is_token_valid": True,
                        "token": fetched_token.key,
                    }
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
