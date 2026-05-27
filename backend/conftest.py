"""Root pytest configuration and shared fixtures."""

import django
from django.conf import settings


def pytest_configure() -> None:
    """Configure Django settings for the test suite."""
    settings.DATABASES["default"]["NAME"] = "habit_tracker_test"
