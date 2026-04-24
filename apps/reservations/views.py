"""
Reservation views.
"""
import logging

from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.accounts.permissions import IsAdminUser
from core.mixins import api_response

from .models import Reservation
from .serializers import ReservationCreateSerializer, ReservationSerializer
from .services import create_reservation, release_reservation

logger = logging.getLogger(__name__)


class ReservationListCreateView(APIView):
    """
    GET  /api/reservations/  — User sees own / Admin sees all
    POST /api/reservations/  — Create a reservation
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["reservations"],
        summary="List reservations (User: own | Admin: all)",
        responses={200: ReservationSerializer(many=True)},
    )
    def get(self, request):
        if request.user.role == "admin":
            reservations = Reservation.objects.select_related("user", "locker").all()
        else:
            reservations = Reservation.objects.select_related("user", "locker").filter(
                user=request.user
            )
        serializer = ReservationSerializer(reservations, many=True)
        return api_response(data=serializer.data)

    @extend_schema(
        tags=["reservations"],
        summary="Reserve a locker",
        request=ReservationCreateSerializer,
        responses={201: ReservationSerializer},
    )
    def post(self, request):
        serializer = ReservationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        locker_id = str(serializer.validated_data["locker_id"])

        reservation = create_reservation(user=request.user, locker_id=locker_id)
        return api_response(
            data=ReservationSerializer(reservation).data,
            message="Locker reserved successfully.",
            status=status.HTTP_201_CREATED,
        )


class ReservationDetailView(APIView):
    """
    GET /api/reservations/<id>/  — Owner or Admin only
    """
    permission_classes = [IsAuthenticated]

    def _get_reservation(self, pk):
        try:
            return Reservation.objects.select_related("user", "locker").get(pk=pk)
        except Reservation.DoesNotExist:
            from core.exceptions import ReservationNotFoundException
            raise ReservationNotFoundException()

    @extend_schema(
        tags=["reservations"],
        summary="Get reservation details (Owner or Admin)",
        responses={200: ReservationSerializer},
    )
    def get(self, request, pk):
        reservation = self._get_reservation(pk)
        if request.user.role != "admin" and reservation.user != request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied()
        return api_response(data=ReservationSerializer(reservation).data)


class ReleaseReservationView(APIView):
    """
    PUT /api/reservations/<id>/release/  — Owner or Admin releases a locker
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["reservations"],
        summary="Release a locker (Owner or Admin)",
        request=None,
        responses={200: ReservationSerializer},
    )
    def put(self, request, pk):
        try:
            reservation = Reservation.objects.select_related("user", "locker").get(pk=pk)
        except Reservation.DoesNotExist:
            from core.exceptions import ReservationNotFoundException
            raise ReservationNotFoundException()

        if request.user.role != "admin" and reservation.user != request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied()

        released = release_reservation(
            reservation_id=str(pk),
            requesting_user=request.user,
        )
        return api_response(
            data=ReservationSerializer(released).data,
            message="Locker released successfully.",
        )
