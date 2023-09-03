from rest_framework import serializers
from rest_framework.authtoken.models import Token

from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from .models import Profile, Institute, Department


class InstituteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institute
        fields = "__all__"


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "username",
            "password",
            "email",
            "is_staff",
            "last_login",
            "date_joined",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        username = validated_data.get("username")
        password = validated_data.get("password")
        email = validated_data.get("email")
        user = User(username=username.lower(), email=email)
        user.set_password(password)
        user.save()

        return user


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    institute = InstituteSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = "__all__"


class UserAuthenticationSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(
            username=data.get("username"), password=data.get("password")
        )

        if user and user.is_active:
            return user.profile

        raise serializers.ValidationError("Credenciais inválidas.")


class TokenValidationSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate(self, data):
        request_token = data.get("token")
        token_query = Token.objects.get(key=request_token)

        return token_query
