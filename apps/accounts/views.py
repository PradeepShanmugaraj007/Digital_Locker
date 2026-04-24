"""
Authentication & user management views.
"""
import logging

from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from core.mixins import api_response

from .serializers import CustomTokenObtainPairSerializer, UserDetailSerializer, UserRegistrationSerializer

logger = logging.getLogger(__name__)


class RegisterView(APIView):
    """
    POST /api/auth/register/

    Register a new user account. No authentication required.
    """
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["auth"],
        summary="Register a new user",
        request=UserRegistrationSerializer,
        responses={
            201: inline_serializer(
                name="RegisterResponse",
                fields={
                    "success": serializers.BooleanField(),
                    "message": serializers.CharField(),
                    "data": UserDetailSerializer(),
                },
            )
        },
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return api_response(
            data=serializer.data,
            message="Registration successful.",
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    """
    POST /api/auth/login/

    Returns JWT access + refresh tokens with embedded user claims.
    """
    serializer_class = CustomTokenObtainPairSerializer

    @extend_schema(
        tags=["auth"],
        summary="Login and obtain JWT tokens",
        responses={200: CustomTokenObtainPairSerializer},
    )
    def post(self, request, *args, **kwargs):
        email = request.data.get("email", "")
        logger.info(
            "Login attempt",
            extra={"email": email, "ip": request.META.get("REMOTE_ADDR")},
        )
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            response.data = {
                "success": True,
                "message": "Login successful.",
                "data": response.data,
            }
        return response


class RefreshTokenView(TokenRefreshView):
    """
    POST /api/auth/refresh/

    Refresh an expired access token using a valid refresh token.
    """

    @extend_schema(
        tags=["auth"],
        summary="Refresh access token",
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            response.data = {
                "success": True,
                "message": "Token refreshed.",
                "data": response.data,
            }
        return response
