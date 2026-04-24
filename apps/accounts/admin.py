"""Accounts Django admin registrations."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import AdminProxy, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "name", "role", "is_active", "created_at")
    list_filter = ("role", "is_active")
    search_fields = ("email", "name")
    ordering = ("-created_at",)
    readonly_fields = ("id", "created_at", "updated_at")

    fieldsets = (
        (None, {"fields": ("id", "email", "password")}),
        ("Personal Info", {"fields": ("name",)}),
        ("Permissions", {"fields": ("role", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "name", "password1", "password2", "role"),
        }),
    )


@admin.register(AdminProxy)
class AdminProxyAdmin(BaseUserAdmin):
    """Separate Django admin view for admin-role users."""
    list_display = ("email", "name", "is_active", "created_at")
    search_fields = ("email", "name")
    ordering = ("email",)  # Override BaseUserAdmin default which uses 'username'
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("name",)}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "name", "password1", "password2"),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).filter(role="admin")
