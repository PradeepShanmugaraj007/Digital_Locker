"""
Locker tests.
"""
from unittest.mock import patch

from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.lockers.models import Locker


def make_user(email="user@test.com", role="user"):
    return User.objects.create_user(email=email, name="Test", password="pass", role=role)


def make_locker(number="A1", loc="Floor 1", status=Locker.Status.AVAILABLE):
    return Locker.objects.create(locker_number=number, location=loc, status=status)


class LockerCRUDTests(APITestCase):
    def setUp(self):
        self.admin = make_user("admin@test.com", role="admin")
        self.user = make_user("user@test.com", role="user")

    def _auth(self, user):
        self.client.force_authenticate(user=user)

    def test_admin_can_create_locker(self):
        self._auth(self.admin)
        response = self.client.post(
            reverse("lockers:locker-list-create"),
            {"locker_number": "B1", "location": "Floor 2"},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_cannot_create_locker(self):
        self._auth(self.user)
        response = self.client.post(
            reverse("lockers:locker-list-create"),
            {"locker_number": "B2", "location": "Floor 2"},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_lockers(self):
        make_locker("C1")
        self._auth(self.user)
        response = self.client.get(reverse("lockers:locker-list-create"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_deactivate_locker(self):
        locker = make_locker("D1")
        self._auth(self.admin)
        response = self.client.delete(
            reverse("lockers:locker-detail", kwargs={"pk": locker.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        locker.refresh_from_db()
        self.assertEqual(locker.status, Locker.Status.INACTIVE)


class AvailableLockerCacheTests(APITestCase):
    def setUp(self):
        self.user = make_user()
        self.client.force_authenticate(user=self.user)
        cache.clear()

    def test_cache_miss_hits_db(self):
        make_locker("E1")
        response = self.client.get(reverse("lockers:available-lockers"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["data"]), 1)

    def test_cache_hit_returns_cached_data(self):
        make_locker("F1")
        # First request populates cache
        self.client.get(reverse("lockers:available-lockers"))
        # Add another locker — should NOT appear (cache still has old data)
        make_locker("F2")
        response = self.client.get(reverse("lockers:available-lockers"))
        self.assertEqual(len(response.data["data"]), 1)
