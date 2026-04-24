"""
Locker service layer.

Contains all business logic and the Redis caching strategy
for the available lockers list.
"""
import logging

from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder
import json

from .models import Locker
from .serializers import LockerSerializer

logger = logging.getLogger(__name__)

AVAILABLE_LOCKERS_CACHE_KEY = "lockers:available"


def get_available_lockers_cached(cache_ttl: int = 60) -> list:
    """
    Returns the list of available lockers.

    Flow:
        1. Check Redis for cached data under AVAILABLE_LOCKERS_CACHE_KEY.
        2. Cache HIT  → return cached list immediately.
        3. Cache MISS → query DB, serialize, store in Redis with TTL, return.

    Cache invalidation:
        Natural TTL expiry only (no manual invalidation on reserve/release).
    """
    cached = cache.get(AVAILABLE_LOCKERS_CACHE_KEY)
    if cached is not None:
        logger.debug(
            "Cache HIT for available lockers",
            extra={"cache_key": AVAILABLE_LOCKERS_CACHE_KEY},
        )
        return cached

    logger.debug(
        "Cache MISS for available lockers — querying database",
        extra={"cache_key": AVAILABLE_LOCKERS_CACHE_KEY},
    )
    queryset = Locker.objects.filter(status=Locker.Status.AVAILABLE).order_by("locker_number")
    data = LockerSerializer(queryset, many=True).data
    # Convert to plain list for safe serialization
    serializable_data = list(data)
    cache.set(AVAILABLE_LOCKERS_CACHE_KEY, serializable_data, cache_ttl)
    logger.info(
        "Available lockers cached",
        extra={
            "cache_key": AVAILABLE_LOCKERS_CACHE_KEY,
            "count": len(serializable_data),
            "ttl": cache_ttl,
        },
    )
    return serializable_data


def deactivate_locker(locker: Locker) -> Locker:
    """
    Soft-deletes a locker by setting its status to 'inactive'.
    Does NOT hard-delete the DB row so reservation history is preserved.
    """
    locker.status = Locker.Status.INACTIVE
    locker.save(update_fields=["status", "updated_at"])
    logger.info(
        "Locker deactivated",
        extra={"locker_id": str(locker.id), "locker_number": locker.locker_number},
    )
    return locker
