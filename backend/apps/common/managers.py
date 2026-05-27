"""Custom model managers for soft-delete support."""

from django.db import models
from django.db.models import QuerySet


class SoftDeleteManager(models.Manager["models.Model"]):
    """Default manager that excludes soft-deleted records."""

    def get_queryset(self) -> QuerySet["models.Model"]:
        """Return only non-deleted records."""
        return super().get_queryset().filter(deleted_at__isnull=True)


class AllObjectsManager(models.Manager["models.Model"]):
    """Manager that includes soft-deleted records."""

    def get_queryset(self) -> QuerySet["models.Model"]:
        """Return all records including soft-deleted."""
        return super().get_queryset()
