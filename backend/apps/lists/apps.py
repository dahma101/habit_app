"""Lists application configuration."""

from django.apps import AppConfig


class ListsConfig(AppConfig):
    """Configuration for the lists application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.lists"
    label = "lists"
