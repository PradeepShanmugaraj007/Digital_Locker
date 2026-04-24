"""
Custom permission classes for role-based access control.
"""
from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    """
    Allows access only to users with role='admin'.
    """
    message = "You must be an admin to perform this action."

    def has_permission(self, request, view) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "admin"
        )


class IsRegularUser(BasePermission):
    """
    Allows access only to users with role='user'.
    """
    message = "This action is restricted to regular users."

    def has_permission(self, request, view) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "user"
        )


class IsOwnerOrAdmin(BasePermission):
    """
    Object-level permission: allows access to the object owner
    or any admin user.
    """
    message = "You do not have permission to access this resource."

    def has_object_permission(self, request, view, obj) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.role == "admin":
            return True
        # obj must have a `user` FK attribute
        return getattr(obj, "user", None) == request.user
