"""Business logic for habit management and check-ins."""

import logging
from typing import Any

from django.db import transaction
from django.db.models import QuerySet
from django.utils import timezone

from .analytics import advance_due_window, calculate_due_window, is_within_due_window
from .models import Habit, HabitLog

logger = logging.getLogger(__name__)


class HabitService:
    """Service layer for habit CRUD and check-in operations.

    The HabitLog queryset is injected via the constructor so that tests
    can substitute mock data without hitting the database.
    """

    def __init__(self, habit_queryset: Any = None, log_queryset: Any = None) -> None:
        """Initialise with optional querysets (default to ORM managers)."""
        self._qs = habit_queryset if habit_queryset is not None else Habit.objects
        self._log_qs = log_queryset if log_queryset is not None else HabitLog.objects

    def get_all(self, user_id: Any) -> QuerySet[Habit]:
        """Return all active habits for the given user."""
        return self._qs.filter(user_id=user_id).select_related("list").order_by("-created_at")

    def get_by_id(self, user_id: Any, habit_id: Any) -> Habit:
        """Retrieve a single habit, validating ownership.

        Raises:
            Habit.DoesNotExist: If not found or not owned by user.
        """
        return self._qs.get(id=habit_id, user_id=user_id)

    def create(self, user_id: Any, data: dict[str, Any]) -> Habit:
        """Create a new habit and compute its initial due window.

        Args:
            user_id: UUID of the owning user.
            data: Validated serializer data (title, periodicity, list_id).

        Returns:
            The newly created Habit instance.
        """
        due_from, due_to = calculate_due_window(data["periodicity"], timezone.now())
        habit = Habit.objects.create(
            user_id=user_id,
            title=data["title"],
            periodicity=data["periodicity"],
            list_id=data["list_id"],
            due_from=due_from,
            due_to=due_to,
            is_checked=False,
        )
        logger.info("Habit created: %s for user %s", habit.id, user_id)
        return habit

    def update(self, user_id: Any, habit_id: Any, data: dict[str, Any]) -> Habit:
        """Update habit fields.

        Args:
            user_id: UUID of the owning user.
            habit_id: UUID of the habit.
            data: Validated partial update data.

        Returns:
            The updated Habit instance.
        """
        habit = self.get_by_id(user_id, habit_id)

        for field, value in data.items():
            setattr(habit, field, value)

        # Recalculate due window if periodicity changed
        if "periodicity" in data:
            due_from, due_to = calculate_due_window(data["periodicity"], timezone.now())
            habit.due_from = due_from
            habit.due_to = due_to

        habit.save()
        logger.info("Habit updated: %s", habit_id)
        return habit

    def delete(self, user_id: Any, habit_id: Any) -> None:
        """Soft-delete a habit.

        Args:
            user_id: UUID of the owning user.
            habit_id: UUID of the habit.

        Raises:
            Habit.DoesNotExist: If not found or not owned by user.
        """
        habit = self.get_by_id(user_id, habit_id)
        habit.delete()
        logger.info("Habit soft-deleted: %s", habit_id)

    @transaction.atomic
    def check_in(self, user_id: Any, habit_id: Any) -> HabitLog:
        """Record a habit check-in and update streak and due window.

        A check-in is only valid when the current time falls within the
        habit's active due window. On success, the streak counter is
        incremented and the next due window is calculated.

        Args:
            user_id: UUID of the owning user.
            habit_id: UUID of the habit to check in.

        Returns:
            The newly created HabitLog.

        Raises:
            Habit.DoesNotExist: If not found or not owned by user.
            ValueError: If the check-in is outside the due window.
        """
        now = timezone.now()
        habit = self.get_by_id(user_id, habit_id)

        if not is_within_due_window(habit.due_from, habit.due_to, now):
            raise ValueError("Check-in is outside the current due window.")

        log = HabitLog.objects.create(
            habit=habit,
            user_id=user_id,
            list=habit.list,
        )

        habit.last_check_time = now
        habit.streak_count += 1
        habit.is_checked = True

        # For as_many_as_possible, reschedule for today so the user can check in again.
        # For all other periodicities, advance to the next period.
        if habit.periodicity == "as_many_as_possible":
            next_from, next_to = calculate_due_window("as_many_as_possible", now)
        elif habit.due_to:
            next_from, next_to = advance_due_window(habit.periodicity, habit.due_to)
        else:
            next_from, next_to = calculate_due_window(habit.periodicity, now)

        habit.due_from = next_from
        habit.due_to = next_to
        habit.is_checked = False  # New period starts unchecked

        habit.save(update_fields=["last_check_time", "streak_count", "is_checked", "due_from", "due_to", "updated_at"])
        logger.info("Habit checked in: %s (streak: %d)", habit_id, habit.streak_count)
        return log
