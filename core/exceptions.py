"""
Custom exception handler and application-specific exceptions.

All API responses follow a consistent envelope:
{
    "success": true/false,
    "data": {...} | [...],      # on success
    "error": {                   # on failure
        "code": "ERROR_CODE",
        "message": "Human readable message",
        "detail": {...}          # optional extra context
    }
}
"""
import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


# ─── Custom Exceptions ────────────────────────────────────────────────────────

class LockerException(Exception):
    """Base exception for locker-related errors."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "LOCKER_ERROR"
    default_message = "A locker error occurred."

    def __init__(self, message=None, code=None, detail=None):
        self.message = message or self.default_message
        self.code = code or self.default_code
        self.detail = detail
        super().__init__(self.message)


class LockerAlreadyReservedException(LockerException):
    status_code = status.HTTP_409_CONFLICT
    default_code = "LOCKER_ALREADY_RESERVED"
    default_message = "This locker is already reserved by another user."


class LockerNotAvailableException(LockerException):
    status_code = status.HTTP_409_CONFLICT
    default_code = "LOCKER_NOT_AVAILABLE"
    default_message = "This locker is not available for reservation."


class LockerInactiveException(LockerException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = "LOCKER_INACTIVE"
    default_message = "This locker has been deactivated."


class ReservationNotFoundException(LockerException):
    status_code = status.HTTP_404_NOT_FOUND
    default_code = "RESERVATION_NOT_FOUND"
    default_message = "Reservation not found."


class ReservationAlreadyReleasedException(LockerException):
    status_code = status.HTTP_409_CONFLICT
    default_code = "RESERVATION_ALREADY_RELEASED"
    default_message = "This reservation has already been released."


# ─── Exception Handler ────────────────────────────────────────────────────────

def custom_exception_handler(exc, context):
    """
    Wraps DRF's default exception handler to produce a consistent response
    envelope. Also catches our custom LockerException subclasses.
    """
    view = context.get("view")
    request = context.get("request")

    # Handle our custom exceptions first
    if isinstance(exc, LockerException):
        logger.error(
            "LockerException raised",
            extra={
                "error_code": exc.code,
                "error_message": exc.message,  # 'message' is reserved in LogRecord
                "view": view.__class__.__name__ if view else None,
                "method": request.method if request else None,
                "path": request.path if request else None,
            },
        )
        return Response(
            {
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "detail": exc.detail,
                },
            },
            status=exc.status_code,
        )

    # Fall back to DRF's default handler
    response = exception_handler(exc, context)

    if response is not None:
        logger.warning(
            "DRF exception raised",
            extra={
                "status_code": response.status_code,
                "error_detail": str(exc),
                "view": view.__class__.__name__ if view else None,
                "method": request.method if request else None,
                "path": request.path if request else None,
            },
        )
        original_data = response.data
        response.data = {
            "success": False,
            "error": {
                "code": "API_ERROR",
                "message": "An error occurred processing your request.",
                "detail": original_data,
            },
        }
    else:
        # Unhandled exception — log it
        logger.exception(
            "Unhandled exception",
            extra={
                "view": view.__class__.__name__ if view else None,
                "method": request.method if request else None,
                "path": request.path if request else None,
            },
            exc_info=exc,
        )

    return response
