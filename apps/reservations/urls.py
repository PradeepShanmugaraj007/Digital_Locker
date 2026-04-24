"""Reservations URL configuration."""
from django.urls import path

from .views import ReleaseReservationView, ReservationDetailView, ReservationListCreateView

app_name = "reservations"

urlpatterns = [
    path("", ReservationListCreateView.as_view(), name="reservation-list-create"),
    path("<uuid:pk>/", ReservationDetailView.as_view(), name="reservation-detail"),
    path("<uuid:pk>/release/", ReleaseReservationView.as_view(), name="reservation-release"),
]
