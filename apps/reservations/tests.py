"""
Reservation tests.
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.lockers.models import Locker
from apps.reservations.models import Reservation


def make_user(email="user@test.com", role="user"):
    return User.objects.create_user(email=email, name="Test", password="pass", role=role)


def make_locker(number="A1", locker_status=Locker.Status.AVAILABLE):
    return Locker.objects.create(locker_number=number, location="Floor 1", status=locker_status)


class ReservationCreateTests(APITestCase):
    def setUp(self):
        self.user = make_user()
        self.locker = make_locker()
        self.client.force_authenticate(user=self.user)

    def test_create_reservation_success(self):
        response = self.client.post(
            reverse("reservations:reservation-list-create"),
            {"locker_id": str(self.locker.id)},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.locker.refresh_from_db()
        self.assertEqual(self.locker.status, Locker.Status.OCCUPIED)

    def test_double_booking_rejected(self):
        # First reservation
        self.client.post(
            reverse("reservations:reservation-list-create"),
            {"locker_id": str(self.locker.id)},
        )
        # Second reservation attempt on the same locker
        user2 = make_user(email="user2@test.com")
        self.client.force_authenticate(user=user2)
        response = self.client.post(
            reverse("reservations:reservation-list-create"),
            {"locker_id": str(self.locker.id)},
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_cannot_reserve_inactive_locker(self):
        inactive = make_locker("B1", Locker.Status.INACTIVE)
        response = self.client.post(
            reverse("reservations:reservation-list-create"),
            {"locker_id": str(inactive.id)},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ReservationReleaseTests(APITestCase):
    def setUp(self):
        self.user = make_user()
        self.locker = make_locker()
        self.client.force_authenticate(user=self.user)
        # Create an active reservation
        resp = self.client.post(
            reverse("reservations:reservation-list-create"),
            {"locker_id": str(self.locker.id)},
        )
        self.reservation_id = resp.data["data"]["id"]

    def test_release_reservation_success(self):
        response = self.client.put(
            reverse("reservations:reservation-release", kwargs={"pk": self.reservation_id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.locker.refresh_from_db()
        self.assertEqual(self.locker.status, Locker.Status.AVAILABLE)

    def test_cannot_release_already_released(self):
        # Release once
        self.client.put(
            reverse("reservations:reservation-release", kwargs={"pk": self.reservation_id})
        )
        # Try releasing again
        response = self.client.put(
            reverse("reservations:reservation-release", kwargs={"pk": self.reservation_id})
        )
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_other_user_cannot_release(self):
        other = make_user(email="other@test.com")
        self.client.force_authenticate(user=other)
        response = self.client.put(
            reverse("reservations:reservation-release", kwargs={"pk": self.reservation_id})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ReservationListScopeTests(APITestCase):
    def setUp(self):
        self.user1 = make_user("u1@test.com")
        self.user2 = make_user("u2@test.com")
        self.admin = make_user("admin@test.com", role="admin")
        locker1 = make_locker("X1")
        locker2 = make_locker("X2")
        # user1 reserves locker1
        self.client.force_authenticate(user=self.user1)
        self.client.post(
            reverse("reservations:reservation-list-create"),
            {"locker_id": str(locker1.id)},
        )
        # user2 reserves locker2
        self.client.force_authenticate(user=self.user2)
        self.client.post(
            reverse("reservations:reservation-list-create"),
            {"locker_id": str(locker2.id)},
        )

    def test_user_sees_only_own_reservations(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(reverse("reservations:reservation-list-create"))
        self.assertEqual(len(response.data["data"]), 1)

    def test_admin_sees_all_reservations(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(reverse("reservations:reservation-list-create"))
        self.assertEqual(len(response.data["data"]), 2)
