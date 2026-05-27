"""Habit, HabitLog, ListTemplate, and HabitTemplate models."""

from django.conf import settings
from django.db import models

from apps.common.models import BaseModel


class PeriodicityChoices(models.TextChoices):
    """Available periodicity options for habit scheduling."""

    AS_MANY_AS_POSSIBLE = "as_many_as_possible", "As Many As Possible"
    DAILY = "daily", "Daily"
    TWICE_WEEKLY = "twice_weekly", "Twice Weekly"
    WEEKLY = "weekly", "Weekly"
    TWICE_MONTHLY = "twice_monthly", "Twice Monthly"
    MONTHLY = "monthly", "Monthly"


class ListTemplate(BaseModel):
    """Template for a habit list category used to seed new users.

    These are read-only fixtures loaded during database seeding.
    """

    title: models.CharField = models.CharField(max_length=255)

    class Meta:
        db_table = "list_templates"

    def __str__(self) -> str:
        return self.title


class HabitTemplate(BaseModel):
    """Template for an individual habit used to seed new users.

    Each template is associated with a ListTemplate to determine
    which list the habit is created under for new users.
    """

    title: models.CharField = models.CharField(max_length=500)
    periodicity: models.CharField = models.CharField(
        max_length=20,
        choices=PeriodicityChoices.choices,
    )
    list_template: models.ForeignKey = models.ForeignKey(
        ListTemplate,
        on_delete=models.CASCADE,
        related_name="habit_templates",
    )

    class Meta:
        db_table = "habit_templates"

    def __str__(self) -> str:
        return self.title


class Habit(BaseModel):
    """A recurring activity that a user tracks.

    Due windows (``due_from``/``due_to``) define when the habit must be
    completed. Missing a window resets the streak counter to zero.
    """

    title: models.TextField = models.TextField()
    periodicity: models.CharField = models.CharField(
        max_length=20,
        choices=PeriodicityChoices.choices,
        db_index=True,
    )
    list: models.ForeignKey = models.ForeignKey(
        "lists.HabitList",
        on_delete=models.SET_NULL,
        null=True,
        related_name="habits",
    )
    user: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="habits",
    )
    last_check_time: models.DateTimeField = models.DateTimeField(null=True, blank=True)
    is_checked: models.BooleanField = models.BooleanField(default=False)
    due_from: models.DateTimeField = models.DateTimeField(null=True, blank=True, db_index=True)
    due_to: models.DateTimeField = models.DateTimeField(null=True, blank=True, db_index=True)
    streak_count: models.IntegerField = models.IntegerField(default=0)

    class Meta:
        db_table = "habits"
        indexes = [
            models.Index(fields=["user_id"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return self.title


class HabitLog(BaseModel):
    """A record of a single habit check-in event.

    Created each time a user marks a habit as completed. Stores a
    snapshot of the list at check-in time to preserve historical context.
    """

    habit: models.ForeignKey = models.ForeignKey(
        Habit,
        on_delete=models.CASCADE,
        related_name="logs",
    )
    user: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="habit_logs",
    )
    list: models.ForeignKey = models.ForeignKey(
        "lists.HabitList",
        on_delete=models.SET_NULL,
        null=True,
        related_name="habit_logs",
    )

    class Meta:
        db_table = "habit_logs"
        indexes = [
            models.Index(fields=["user_id"]),
            models.Index(fields=["habit_id"]),
        ]

    def __str__(self) -> str:
        return f"Log: {self.habit_id} at {self.created_at}"
