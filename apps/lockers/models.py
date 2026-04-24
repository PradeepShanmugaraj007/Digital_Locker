"""
Locker model.
"""
import uuid

from django.db import models


class Locker(models.Model):
    """
    Represents a physical storage locker unit.

    Fields required by spec:
        id, locker_number, location, status, created_at, updated_at
    """

    class Status(models.TextChoices):
        AVAILABLE = "available", "Available"
        OCCUPIED = "occupied", "Occupied"
        INACTIVE = "inactive", "Inactive"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    locker_number = models.CharField(max_length=50, unique=True, db_index=True)
    location = models.CharField(max_length=255)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.AVAILABLE,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "lockers"
        ordering = ["locker_number"]
        verbose_name = "Locker"
        verbose_name_plural = "Lockers"

    def __str__(self) -> str:
        return f"Locker #{self.locker_number} [{self.status}] @ {self.location}"

    @property
    def is_available(self) -> bool:
        return self.status == self.Status.AVAILABLE
