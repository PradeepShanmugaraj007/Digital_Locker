"""
Accounts app tests.
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User


class UserRegistrationTests(APITestCase):
    """Tests for POST /api/auth/register/"""

    url = reverse("accounts:register")

    def test_register_success(self):
        payload = {
            "name": "Test User",
            "email": "testuser@example.com",
            "password": "StrongPass@123",
            "password_confirm": "StrongPass@123",
        }
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertTrue(User.objects.filter(email="testuser@example.com").exists())

    def test_register_duplicate_email(self):
        User.objects.create_user(
            email="existing@example.com", name="Existing", password="pass"
        )
        payload = {
            "name": "Another",
            "email": "existing@example.com",
            "password": "StrongPass@123",
            "password_confirm": "StrongPass@123",
        }
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_password_mismatch(self):
        payload = {
            "name": "Test",
            "email": "new@example.com",
            "password": "StrongPass@123",
            "password_confirm": "WrongPass@123",
        }
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLoginTests(APITestCase):
    """Tests for POST /api/auth/login/"""

    url = reverse("accounts:login")

    def setUp(self):
        self.user = User.objects.create_user(
            email="loginuser@example.com",
            name="Login User",
            password="StrongPass@123",
        )

    def test_login_success(self):
        response = self.client.post(
            self.url, {"email": "loginuser@example.com", "password": "StrongPass@123"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data["data"])
        self.assertIn("refresh", response.data["data"])

    def test_login_wrong_password(self):
        response = self.client.post(
            self.url, {"email": "loginuser@example.com", "password": "WrongPassword"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
