"""
Accounts serializers: registration, user profile, and custom JWT token.
"""
import logging

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User

logger = logging.getLogger(__name__)


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Handles new user registration. Writes only."""

    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = ("id", "name", "email", "password", "password_confirm", "created_at")
        read_only_fields = ("id", "created_at")

    def validate_email(self, value: str) -> str:
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()

    def validate(self, attrs: dict) -> dict:
        if attrs["password"] != attrs.pop("password_confirm"):
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        validate_password(attrs["password"])
        return attrs

    def create(self, validated_data: dict) -> User:
        user = User.objects.create_user(
            email=validated_data["email"],
            name=validated_data["name"],
            password=validated_data["password"],
        )
        logger.info(
            "New user registered",
            extra={"user_id": str(user.id), "email": user.email},
        )
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    """Read-only user profile serializer."""

    class Meta:
        model = User
        fields = ("id", "name", "email", "role", "is_active", "created_at", "updated_at")
        read_only_fields = fields


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Extends the standard JWT serializer to embed user claims
    (user_id, email, role) directly into the token payload.
    """

    @classmethod
    def get_token(cls, user: User):
        token = super().get_token(user)
        token["user_id"] = str(user.id)
        token["email"] = user.email
        token["role"] = user.role
        token["name"] = user.name
        return token

    def validate(self, attrs: dict) -> dict:
        data = super().validate(attrs)
        user = self.user
        logger.info(
            "User login successful",
            extra={"user_id": str(user.id), "email": user.email, "role": user.role},
        )
        # Append user info to the token response
        data["user"] = {
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "role": user.role,
        }
        return data
