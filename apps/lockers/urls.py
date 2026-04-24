"""Lockers URL configuration."""
from django.urls import path

from .views import AvailableLockerListView, LockerDetailView, LockerListCreateView

app_name = "lockers"

urlpatterns = [
    # IMPORTANT: 'available/' must come BEFORE '<pk>/' to avoid UUID match conflict
    path("available/", AvailableLockerListView.as_view(), name="available-lockers"),
    path("", LockerListCreateView.as_view(), name="locker-list-create"),
    path("<uuid:pk>/", LockerDetailView.as_view(), name="locker-detail"),
]
