"""Business logic for habit list management."""

import logging
from typing import Any

from django.db import transaction
from django.db.models import QuerySet

from .models import HabitList

logger = logging.getLogger(__name__)


class ListService:
    """Service layer for managing habit lists.

    Enforces ownership checks, default-list protection, and habit
    reassignment on list deletion. The queryset is injected via the
    constructor to support testing with mock data.
    """

    def __init__(self, list_queryset: Any = None) -> None:
        """Initialise with an optional queryset (defaults to HabitList.objects)."""
        self._qs = list_queryset if list_queryset is not None else HabitList.objects

    def get_all(self, user_id: Any) -> QuerySet[HabitList]:
        """Return all active lists belonging to the given user."""
        return self._qs.filter(user_id=user_id).order_by("created_at")

    def get_by_id(self, user_id: Any, list_id: Any) -> HabitList:
        """Retrieve a single list, validating ownership.

        Raises:
            HabitList.DoesNotExist: If not found or not owned by user.
        """
        return self._qs.get(id=list_id, user_id=user_id)

    def create(self, user_id: Any, title: str) -> HabitList:
        """Create a new list for the given user.

        Args:
            user_id: UUID of the owning user.
            title: Display name for the list.

        Returns:
            The newly created HabitList.

        Raises:
            ValueError: If a list with the same title already exists for this user.
        """
        if self._qs.filter(user_id=user_id, title__iexact=title).exists():
            raise ValueError(f"A list named '{title}' already exists.")
        habit_list = HabitList.objects.create(user_id=user_id, title=title)
        logger.info("List created: %s for user %s", title, user_id)
        return habit_list

    def update(self, user_id: Any, list_id: Any, title: str) -> HabitList:
        """Update the title of an existing list.

        Args:
            user_id: UUID of the owning user.
            list_id: UUID of the list to update.
            title: New display name.

        Returns:
            The updated HabitList.

        Raises:
            HabitList.DoesNotExist: If not found or not owned by user.
            ValueError: If the new title conflicts with another list.
        """
        habit_list = self.get_by_id(user_id, list_id)

        if self._qs.filter(user_id=user_id, title__iexact=title).exclude(id=list_id).exists():
            raise ValueError(f"A list named '{title}' already exists.")

        habit_list.title = title
        habit_list.save(update_fields=["title", "updated_at"])
        logger.info("List updated: %s", list_id)
        return habit_list

    @transaction.atomic
    def delete(self, user_id: Any, list_id: Any) -> None:
        """Soft-delete a list, reassigning its habits to the user's default list.

        Args:
            user_id: UUID of the owning user.
            list_id: UUID of the list to delete.

        Raises:
            HabitList.DoesNotExist: If not found or not owned by user.
            ValueError: If attempting to delete the default list.
        """
        habit_list = self.get_by_id(user_id, list_id)

        if habit_list.is_default:
            raise ValueError("The default list cannot be deleted.")

        default_list = self._qs.get(user_id=user_id, is_default=True)

        # Reassign habits to default list before soft-deleting
        from apps.habits.models import Habit

        Habit.objects.filter(user_id=user_id, list_id=list_id).update(list=default_list)

        habit_list.delete()
        logger.info("List soft-deleted: %s, habits reassigned to default", list_id)
