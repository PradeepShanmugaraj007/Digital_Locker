"""
Reservation service layer.

Critical: all reservation creation/release operations use
select_for_update() inside a transaction to prevent race conditions
(two users trying to reserve the same locker simultaneously).
"""
import logging
from datetime import datetime, timezone

from django.db import transaction

from apps.lockers.models import Locker
from core.exceptions import (
    LockerAlreadyReservedException,
    LockerInactiveException,
    LockerNotAvailableException,
    ReservationAlreadyReleasedException,
    ReservationNotFoundException,
)

from .models import Reservation

logger = logging.getLogger(__name__)


def create_reservation(user, locker_id: str) -> Reservation:
    """
    Attempt to reserve a locker for a user.

    Steps:
        1. Acquire a row-level lock on the Locker row (select_for_update).
        2. Validate locker is available (not inactive, not occupied).
        3. Check no other active reservation exists for this locker.
        4. Create reservation and set locker status to 'occupied'.

    Raises:
        LockerNotAvailableException  — if locker doesn't exist or is occupied.
        LockerInactiveException      — if locker is deactivated.
        LockerAlreadyReservedException — if a concurrent request already reserved it.
    """
    with transaction.atomic():
        try:
            locker = Locker.objects.select_for_update().get(pk=locker_id)
        except Locker.DoesNotExist:
            raise LockerNotAvailableException(
                message=f"Locker with ID '{locker_id}' does not exist."
            )

        if locker.status == Locker.Status.INACTIVE:
            raise LockerInactiveException()

        if locker.status == Locker.Status.OCCUPIED:
            raise LockerAlreadyReservedException()

        # Extra guard: check for any active reservation row (belt + suspenders)
        if Reservation.objects.filter(locker=locker, status=Reservation.Status.ACTIVE).exists():
            raise LockerAlreadyReservedException()

        reservation = Reservation.objects.create(user=user, locker=locker)
        locker.status = Locker.Status.OCCUPIED
        locker.save(update_fields=["status", "updated_at"])

        logger.info(
            "Reservation created",
            extra={
                "reservation_id": str(reservation.id),
                "locker_id": str(locker.id),
                "locker_number": locker.locker_number,
                "user_id": str(user.id),
            },
        )
        return reservation


def release_reservation(reservation_id: str, requesting_user) -> Reservation:
    """
    Release an active reservation.

    - Marks reservation status as 'released' and sets released_at timestamp.
    - Sets locker status back to 'available'.
    - Cache will expire naturally (TTL-based).

    Raises:
        ReservationNotFoundException       — if reservation doesn't exist.
        ReservationAlreadyReleasedException — if already released/cancelled.
    """
    with transaction.atomic():
        try:
            reservation = (
                Reservation.objects
                .select_for_update()
                .select_related("locker", "user")
                .get(pk=reservation_id)
            )
        except Reservation.DoesNotExist:
            raise ReservationNotFoundException()

        if not reservation.is_active:
            raise ReservationAlreadyReleasedException()

        reservation.status = Reservation.Status.RELEASED
        reservation.released_at = datetime.now(tz=timezone.utc)
        reservation.save(update_fields=["status", "released_at", "updated_at"])

        locker = reservation.locker
        locker.status = Locker.Status.AVAILABLE
        locker.save(update_fields=["status", "updated_at"])

        logger.info(
            "Reservation released",
            extra={
                "reservation_id": str(reservation.id),
                "locker_id": str(locker.id),
                "locker_number": locker.locker_number,
                "user_id": str(reservation.user.id),
                "released_by": str(requesting_user.id),
            },
        )
        return reservation
