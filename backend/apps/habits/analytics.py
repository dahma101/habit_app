"""Pure functional analytics for habit tracking data.

All functions are pure (no side effects, deterministic output) and operate
on data passed in rather than querying the database directly. This enables
easy unit testing and composable data transformation pipelines.
"""

from datetime import datetime, timedelta
from typing import Any

from django.utils import timezone


def calculate_due_window(periodicity: str, reference_dt: datetime) -> tuple[datetime, datetime]:
    """Compute the due_from and due_to datetimes for a given periodicity.

    Args:
        periodicity: One of daily / twice_weekly / weekly / twice_monthly / monthly.
        reference_dt: The reference datetime (typically now, always UTC).

    Returns:
        A tuple of (due_from, due_to) in UTC.
    """
    start = reference_dt.replace(hour=0, minute=0, second=0, microsecond=0)

    if periodicity in ("daily", "as_many_as_possible"):
        due_from = start
        due_to = start + timedelta(days=1) - timedelta(seconds=1)

    elif periodicity == "twice_weekly":
        # First window: Mon-Wed; second: Thu-Sun
        weekday = start.weekday()  # 0=Mon
        if weekday < 3:
            due_from = start - timedelta(days=weekday)
            due_to = due_from + timedelta(days=3) - timedelta(seconds=1)
        else:
            due_from = start - timedelta(days=weekday - 3)
            due_to = due_from + timedelta(days=4) - timedelta(seconds=1)

    elif periodicity == "weekly":
        due_from = start - timedelta(days=start.weekday())
        due_to = due_from + timedelta(weeks=1) - timedelta(seconds=1)

    elif periodicity == "twice_monthly":
        if start.day <= 15:
            due_from = start.replace(day=1)
            due_to = start.replace(day=15, hour=23, minute=59, second=59, microsecond=0)
        else:
            due_from = start.replace(day=16)
            # Last day of month
            if start.month == 12:
                last_day = start.replace(year=start.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                last_day = start.replace(month=start.month + 1, day=1) - timedelta(days=1)
            due_to = last_day.replace(hour=23, minute=59, second=59, microsecond=0)

    else:  # monthly
        due_from = start.replace(day=1)
        if start.month == 12:
            due_to = start.replace(year=start.year + 1, month=1, day=1) - timedelta(seconds=1)
        else:
            due_to = start.replace(month=start.month + 1, day=1) - timedelta(seconds=1)

    return due_from, due_to


def advance_due_window(periodicity: str, current_due_to: datetime) -> tuple[datetime, datetime]:
    """Calculate the next due window starting after the current one ends.

    Args:
        periodicity: The habit's periodicity string.
        current_due_to: The end of the current due window.

    Returns:
        A tuple of (due_from, due_to) for the next period.
    """
    next_reference = current_due_to + timedelta(seconds=1)
    return calculate_due_window(periodicity, next_reference)


def is_within_due_window(due_from: datetime | None, due_to: datetime | None, now: datetime) -> bool:
    """Return True if ``now`` falls within the given due window.

    Args:
        due_from: Start of the allowed check-in window.
        due_to: End of the allowed check-in window.
        now: The datetime to evaluate (typically UTC now).

    Returns:
        True if the check-in is within the window, False otherwise.
    """
    if due_from is None or due_to is None:
        return False
    return due_from <= now <= due_to


def find_least_tracked_habit(habits: list[Any]) -> Any | None:
    """Return the habit with the fewest check-ins (log_count annotation or streak_count fallback).

    Args:
        habits: List of Habit model instances, optionally annotated with ``log_count``.

    Returns:
        The habit with the minimum log_count, or None if the list is empty.
    """
    if not habits:
        return None
    return min(habits, key=lambda h: getattr(h, "log_count", h.streak_count))


def compute_longest_streak(habits: list[Any]) -> int:
    """Return the highest streak_count across all provided habits.

    Args:
        habits: Iterable of Habit model instances.

    Returns:
        The maximum streak count, or 0 if the list is empty.
    """
    if not habits:
        return 0
    return max(h.streak_count for h in habits)


def group_habits_by_periodicity(habits: list[Any]) -> dict[str, list[Any]]:
    """Organise habits into buckets keyed by their periodicity value.

    Args:
        habits: Iterable of Habit model instances.

    Returns:
        Dictionary mapping periodicity string → list of habits.
    """
    result: dict[str, list[Any]] = {}
    for habit in habits:
        result.setdefault(habit.periodicity, []).append(habit)
    return result


def build_general_report(habits: list[Any]) -> dict[str, Any]:
    """Build a general analytics report for a collection of habits.

    Pure function: operates only on the provided data, makes no DB calls.

    Args:
        habits: List of Habit model instances for a single user.

    Returns:
        Dictionary with tracked_habits, habits_by_periodicity, and longest_streak.
    """
    return {
        "tracked_habits": habits,
        "habits_by_periodicity": group_habits_by_periodicity(habits),
        "longest_streak": compute_longest_streak(habits),
        "least_tracked_habit": find_least_tracked_habit(habits),
    }


def build_habit_history_report(habit: Any, logs: list[Any]) -> dict[str, Any]:
    """Build a detailed history report for a single habit.

    Pure function: operates only on the provided data, makes no DB calls.

    Args:
        habit: A single Habit model instance.
        logs: All HabitLog instances associated with this habit.

    Returns:
        Dictionary with longest_streak and log history.
    """
    return {
        "habit_id": str(habit.id),
        "title": habit.title,
        "streak_count": habit.streak_count,
        "longest_streak": habit.streak_count,
        "log_history": [
            {
                "id": str(log.id),
                "checked_at": log.created_at,
            }
            for log in sorted(logs, key=lambda l: l.created_at, reverse=True)
        ],
    }
