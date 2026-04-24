"""Reservation serializers."""
from rest_framework import serializers

from apps.accounts.serializers import UserDetailSerializer
from apps.lockers.serializers import LockerSerializer

from .models import Reservation


class ReservationSerializer(serializers.ModelSerializer):
    """Full reservation representation with nested user and locker details."""

    user = UserDetailSerializer(read_only=True)
    locker = LockerSerializer(read_only=True)

    class Meta:
        model = Reservation
        fields = (
            "id",
            "user",
            "locker",
            "status",
            "reserved_at",
            "released_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class ReservationCreateSerializer(serializers.Serializer):
    """Input serializer for creating a reservation. Only locker_id is needed."""

    locker_id = serializers.UUIDField(required=True)
