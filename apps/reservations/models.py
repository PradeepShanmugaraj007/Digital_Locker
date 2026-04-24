"""
Reservation model.

Key constraint: only ONE active reservation per locker at any time.
Enforced at both the DB layer (unique_together) and service layer (select_for_update).
"""
import uuid

from django.conf import settings
from django.db import models


class Reservation(models.Model):
    """Tracks a user's reservation of a locker."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        RELEASED = "released", "Released"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="reservations",
    )
    locker = models.ForeignKey(
        "lockers.Locker",
        on_delete=models.PROTECT,
        related_name="reservations",
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
    )
    reserved_at = models.DateTimeField(auto_now_add=True)
    released_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "reservations"
        ordering = ["-reserved_at"]
        verbose_name = "Reservation"
        verbose_name_plural = "Reservations"
        # DB-level constraint: a locker can have at most one active reservation
        constraints = [
            models.UniqueConstraint(
                fields=["locker"],
                condition=models.Q(status="active"),
                name="unique_active_reservation_per_locker",
            )
        ]

    def __str__(self) -> str:
        return f"Reservation {self.id} — Locker {self.locker.locker_number} by {self.user.email} [{self.status}]"

    @property
    def is_active(self) -> bool:
        return self.status == self.Status.ACTIVE
