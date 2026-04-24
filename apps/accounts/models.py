"""
User model with role-based access control.

A single User model handles both 'user' and 'admin' roles.
An AdminProxy model is registered in Django admin for
separate admin-panel management.
"""
import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    """Custom manager for User model using email as the unique identifier."""

    def create_user(self, email: str, name: str, password: str = None, **extra_fields):
        if not email:
            raise ValueError("Email address is required.")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, name: str, password: str, **extra_fields):
        extra_fields.setdefault("role", User.Role.ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Core user model.

    Fields required by the spec:
        id, name, created_at, updated_at

    Additional fields added:
        email (login identifier), role, is_active, is_staff
    """

    class Role(models.TextChoices):
        USER = "user", "User"
        ADMIN = "admin", "Admin"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True, db_index=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.USER)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # required for Django admin access
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self) -> str:
        return f"{self.name} <{self.email}> [{self.role}]"

    @property
    def is_admin(self) -> bool:
        return self.role == self.Role.ADMIN


class AdminProxy(User):
    """
    Proxy model so admins can be managed separately in Django's
    admin panel without a separate DB table.
    """

    class Meta:
        proxy = True
        verbose_name = "Admin"
        verbose_name_plural = "Admins"
