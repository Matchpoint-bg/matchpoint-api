from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from dj_rest_auth.registration.serializers import RegisterSerializer
from django.contrib.auth import get_user_model
from .models import CustomUser
from dj_rest_auth.serializers import LoginSerializer


class UserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "preferred_language",
            "is_staff",
        ]

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)


class EmailLoginSerializer(LoginSerializer):
    username = None
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        attrs["username"] = attrs.get("email")
        return super().validate(attrs)


class UserListSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name"]


class UserRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    phone_number = serializers.CharField(max_length=12, required=False)

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data["first_name"] = self.validated_data.get("first_name", "")
        data["last_name"] = self.validated_data.get("last_name", "")
        data["phone_number"] = self.validated_data.get("phone_number", "")
        return data

    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.phone_number = self.cleaned_data["phone_number"]

        user.save()

        return user

    def get_fields(self) -> dict:
        fields = super().get_fields()
        fields.pop("username", None)
        return fields
