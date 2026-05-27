"""Celery application configuration and Beat schedule."""

import os

from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("habit_tracker")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.on_after_finalize.connect
def setup_periodic_tasks(sender: Celery, **kwargs: object) -> None:
    """Register periodic tasks after app is fully loaded."""
    from celery.schedules import crontab  # noqa: F401

    interval_minutes: int = settings.CELERY_BEAT_INTERVAL_MINUTES

    sender.add_periodic_task(
        interval_minutes * 60,
        check_habit_due_dates_task.s(),
        name="check-habit-due-dates",
    )


@app.task
def check_habit_due_dates_task() -> None:
    """Proxy task that delegates to the habits app task."""
    from apps.habits.tasks import check_habit_due_dates

    check_habit_due_dates()
