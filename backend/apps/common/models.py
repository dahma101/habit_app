"""Base model classes with UUID primary keys and soft-delete support."""

import uuid
from typing import Any

from django.db import models
from django.utils import timezone

from .managers import AllObjectsManager, SoftDeleteManager


class BaseModel(models.Model):
    """Abstract base model with UUID PK and timestamp fields.

    All domain models inherit from this class to ensure consistent
    identification and audit trail fields across the application.
    """

    id: models.UUIDField = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)
    deleted_at: models.DateTimeField = models.DateTimeField(null=True, blank=True, db_index=True)

    objects = SoftDeleteManager()
    all_objects = AllObjectsManager()

    class Meta:
        abstract = True

    def delete(self, using: Any = None, keep_parents: bool = False) -> tuple[int, dict[str, int]]:
        """Soft-delete by setting deleted_at timestamp instead of removing the row."""
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at", "updated_at"])
        return 1, {self.__class__.__name__: 1}

    def hard_delete(self, using: Any = None, keep_parents: bool = False) -> tuple[int, dict[str, int]]:
        """Permanently remove the record from the database."""
        return super().delete(using=using, keep_parents=keep_parents)

    @property
    def is_deleted(self) -> bool:
        """Return True if this record has been soft-deleted."""
        return self.deleted_at is not None

    def restore(self) -> None:
        """Restore a soft-deleted record."""
        self.deleted_at = None
        self.save(update_fields=["deleted_at", "updated_at"])
