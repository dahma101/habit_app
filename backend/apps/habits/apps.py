"""Habits application configuration."""

from django.apps import AppConfig


class HabitsConfig(AppConfig):
    """Configuration for the habits application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.habits"
    label = "habits"
