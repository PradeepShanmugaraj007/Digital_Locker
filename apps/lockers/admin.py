"""Locker Django admin."""
from django.contrib import admin

from .models import Locker


@admin.register(Locker)
class LockerAdmin(admin.ModelAdmin):
    list_display = ("locker_number", "location", "status", "created_at", "updated_at")
    list_filter = ("status", "location")
    search_fields = ("locker_number", "location")
    readonly_fields = ("id", "created_at", "updated_at")
    ordering = ("locker_number",)

    actions = ["deactivate_lockers"]

    def deactivate_lockers(self, request, queryset):
        queryset.update(status=Locker.Status.INACTIVE)
        self.message_user(request, f"{queryset.count()} locker(s) deactivated.")
    deactivate_lockers.short_description = "Deactivate selected lockers"
