"""
Locker views.
"""
import logging

from django.conf import settings
from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.accounts.permissions import IsAdminUser
from core.mixins import api_response

from .models import Locker
from .serializers import LockerCreateSerializer, LockerSerializer, LockerUpdateSerializer
from .services import deactivate_locker, get_available_lockers_cached

logger = logging.getLogger(__name__)


class LockerListCreateView(APIView):
    """
    GET  /api/lockers/  — List all lockers (any authenticated user)
    POST /api/lockers/  — Create a locker (admin only)
    """

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUser()]
        return [IsAuthenticated()]

    @extend_schema(
        tags=["lockers"],
        summary="List all lockers",
        responses={200: LockerSerializer(many=True)},
    )
    def get(self, request):
        lockers = Locker.objects.all()
        serializer = LockerSerializer(lockers, many=True)
        return api_response(data=serializer.data)

    @extend_schema(
        tags=["lockers"],
        summary="Create a locker (Admin only)",
        request=LockerCreateSerializer,
        responses={201: LockerSerializer},
    )
    def post(self, request):
        serializer = LockerCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        locker = serializer.save()
        logger.info(
            "Locker created",
            extra={
                "locker_id": str(locker.id),
                "locker_number": locker.locker_number,
                "admin_id": str(request.user.id),
            },
        )
        return api_response(
            data=LockerSerializer(locker).data,
            message="Locker created successfully.",
            status=status.HTTP_201_CREATED,
        )


class LockerDetailView(APIView):
    """
    GET    /api/lockers/<id>/  — Get locker details
    PUT    /api/lockers/<id>/  — Update locker (admin only)
    DELETE /api/lockers/<id>/  — Deactivate locker (admin only)
    """

    def get_permissions(self):
        if self.request.method in ("PUT", "DELETE"):
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def _get_locker(self, pk):
        return get_object_or_404(Locker, pk=pk)

    @extend_schema(
        tags=["lockers"],
        summary="Get locker details",
        responses={200: LockerSerializer},
    )
    def get(self, request, pk):
        locker = self._get_locker(pk)
        return api_response(data=LockerSerializer(locker).data)

    @extend_schema(
        tags=["lockers"],
        summary="Update a locker (Admin only)",
        request=LockerUpdateSerializer,
        responses={200: LockerSerializer},
    )
    def put(self, request, pk):
        locker = self._get_locker(pk)
        serializer = LockerUpdateSerializer(locker, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        locker = serializer.save()
        logger.info(
            "Locker updated",
            extra={
                "locker_id": str(locker.id),
                "admin_id": str(request.user.id),
                "new_status": locker.status,
            },
        )
        return api_response(
            data=LockerSerializer(locker).data,
            message="Locker updated successfully.",
        )

    @extend_schema(
        tags=["lockers"],
        summary="Deactivate a locker (Admin only)",
        responses={
            200: inline_serializer(
                name="DeactivateResponse",
                fields={
                    "success": serializers.BooleanField(),
                    "message": serializers.CharField(),
                },
            )
        },
    )
    def delete(self, request, pk):
        locker = self._get_locker(pk)
        deactivate_locker(locker)
        logger.info(
            "Locker deactivated via DELETE",
            extra={"locker_id": str(locker.id), "admin_id": str(request.user.id)},
        )
        return api_response(message="Locker deactivated successfully.")


class AvailableLockerListView(APIView):
    """
    GET /api/lockers/available/

    Returns available lockers served from Redis cache (TTL=60s).
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["lockers"],
        summary="List available lockers (Redis cached, TTL=60s)",
        responses={200: LockerSerializer(many=True)},
    )
    def get(self, request):
        cache_ttl = getattr(settings, "CACHE_TTL", 60)
        data = get_available_lockers_cached(cache_ttl=cache_ttl)
        return api_response(data=data)
