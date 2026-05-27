"""Celery tasks for scheduled habit maintenance."""

import logging

from celery import shared_task
from django.utils import timezone

from .analytics import advance_due_window
from .models import Habit, HabitLog

logger = logging.getLogger(__name__)


@shared_task
def check_habit_due_dates() -> int:
    """Reset streak counters for overdue habits and advance their due windows.

    Runs on the Celery Beat schedule (default: every 10 minutes). For each
    active habit where ``due_to`` has passed and no check-in occurred in the
    window, the streak is reset to zero and the due window is advanced.

    Returns:
        Number of habits whose streaks were reset.
    """
    now = timezone.now()
    reset_count = 0

    overdue_habits = Habit.objects.filter(
        due_to__lt=now,
        deleted_at__isnull=True,
    ).select_related("user")

    for habit in overdue_habits:
        if habit.due_from is None or habit.due_to is None:
            continue

        # Check if there is any log within the expired due window
        has_log = HabitLog.objects.filter(
            habit=habit,
            created_at__gte=habit.due_from,
            created_at__lte=habit.due_to,
            deleted_at__isnull=True,
        ).exists()

        if not has_log and habit.streak_count > 0:
            habit.streak_count = 0
            logger.info("Streak reset for habit %s (overdue, no check-in)", habit.id)
            reset_count += 1

        # Always advance the due window past expiry and reset check flag
        next_from, next_to = advance_due_window(habit.periodicity, habit.due_to)
        habit.due_from = next_from
        habit.due_to = next_to
        habit.is_checked = False
        habit.save(update_fields=["streak_count", "is_checked", "due_from", "due_to", "updated_at"])

    logger.info("check_habit_due_dates: reset %d habit streaks", reset_count)
    return reset_count
