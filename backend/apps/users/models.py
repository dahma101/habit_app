"""User model with custom authentication fields."""

import uuid
from typing import ClassVar

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

from apps.common.managers import AllObjectsManager, SoftDeleteManager


class UserManager(BaseUserManager["User"]):
    """Custom manager for User model that uses email as the unique identifier."""

    def create_user(self, email: str, password: str, **extra_fields: object) -> "User":
        """Create and return a regular user with the given email and password."""
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user: User = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str, **extra_fields: object) -> "User":
        """Create and return a superuser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Application user model.

    Uses email as the primary identifier instead of username.
    Supports soft deletion via the ``deleted_at`` timestamp field.
    """

    class AvatarChoices(models.TextChoices):
        """Available avatar options for user profiles."""

        AVATAR1 = "avatar1", "Avatar 1"
        AVATAR2 = "avatar2", "Avatar 2"
        AVATAR3 = "avatar3", "Avatar 3"
        AVATAR4 = "avatar4", "Avatar 4"
        AVATAR5 = "avatar5", "Avatar 5"

    id: models.UUIDField = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name: models.CharField = models.CharField(max_length=255)
    email: models.EmailField = models.EmailField(unique=True)
    avatar: models.CharField = models.CharField(
        max_length=10,
        choices=AvatarChoices.choices,
        default=AvatarChoices.AVATAR1,
    )
    is_active: models.BooleanField = models.BooleanField(default=True)
    is_staff: models.BooleanField = models.BooleanField(default=False)
    created_at: models.DateTimeField = models.DateTimeField(default=timezone.now)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)
    deleted_at: models.DateTimeField = models.DateTimeField(null=True, blank=True, db_index=True)

    objects: ClassVar[UserManager] = UserManager()  # type: ignore[assignment]
    all_objects: ClassVar[AllObjectsManager] = AllObjectsManager()  # type: ignore[assignment]

    USERNAME_FIELD: str = "email"
    REQUIRED_FIELDS: list[str] = ["full_name"]

    class Meta:
        db_table = "users"

    def __str__(self) -> str:
        return self.email

    def delete(self, using: object = None, keep_parents: bool = False) -> tuple[int, dict[str, int]]:
        """Soft-delete by setting deleted_at timestamp."""
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at", "updated_at"])
        return 1, {"User": 1}
