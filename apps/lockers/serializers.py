"""Locker serializers."""
from rest_framework import serializers

from .models import Locker


class LockerSerializer(serializers.ModelSerializer):
    """Full locker representation (read + write)."""

    class Meta:
        model = Locker
        fields = (
            "id",
            "locker_number",
            "location",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_locker_number(self, value: str) -> str:
        # On update, exclude the current instance from uniqueness check
        qs = Locker.objects.filter(locker_number=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                f"A locker with number '{value}' already exists."
            )
        return value


class LockerCreateSerializer(LockerSerializer):
    """Used when admin creates a new locker. Status defaults to 'available'."""

    class Meta(LockerSerializer.Meta):
        read_only_fields = ("id", "status", "created_at", "updated_at")


class LockerUpdateSerializer(LockerSerializer):
    """Used when admin updates a locker. All writable fields allowed."""

    class Meta(LockerSerializer.Meta):
        read_only_fields = ("id", "created_at", "updated_at")
