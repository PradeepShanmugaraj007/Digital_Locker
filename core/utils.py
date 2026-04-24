"""Shared utility functions."""
import uuid


def generate_uuid() -> str:
    """Return a new UUID4 string."""
    return str(uuid.uuid4())
