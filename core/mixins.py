"""
Shared DRF response helpers and mixins.
"""
from rest_framework.response import Response


def api_response(data=None, message=None, status=200):
    """
    Returns a consistent success response envelope.

    Shape:
        {
            "success": true,
            "message": "...",   # optional
            "data": {...}
        }
    """
    payload = {"success": True}
    if message:
        payload["message"] = message
    if data is not None:
        payload["data"] = data
    return Response(payload, status=status)


class SerializerErrorMixin:
    """
    Mixin that raises a ValidationError with a consistent format
    when serializer validation fails.
    """

    def get_valid_serializer(self, *args, **kwargs):
        serializer = self.get_serializer(*args, **kwargs)
        serializer.is_valid(raise_exception=True)
        return serializer
