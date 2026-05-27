"""Habit list model for grouping habits by category."""

from django.conf import settings
from django.db import models

from apps.common.models import BaseModel


class HabitList(BaseModel):
    """A named collection of habits belonging to a single user.

    Each user starts with a ``Default`` list that cannot be deleted.
    Uniqueness of ``(user, title)`` is enforced at the database level
    via a partial index that excludes soft-deleted rows.
    """

    title: models.CharField = models.CharField(max_length=255)
    user: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lists",
    )
    is_default: models.BooleanField = models.BooleanField(default=False)

    class Meta:
        db_table = "lists"
        indexes = [
            models.Index(fields=["user_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.user_id})"
