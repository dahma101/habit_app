"""Business logic for user registration and profile management."""

import logging
import random
from datetime import timedelta
from typing import Any

from django.db import transaction
from django.utils import timezone

from .models import User

logger = logging.getLogger(__name__)


class UserService:
    """Service layer for user-related operations.

    Encapsulates registration, authentication helpers, and user data
    preloading. Accepts the User queryset via constructor injection
    to allow easy substitution in tests.
    """

    def __init__(self, user_queryset: Any = None) -> None:
        """Initialise with an optional queryset (defaults to User.objects)."""
        self._qs = user_queryset if user_queryset is not None else User.objects

    @transaction.atomic
    def register(self, full_name: str, email: str, avatar: str, password: str) -> User:
        """Create a new user and preload their default lists, habits, and logs.

        Args:
            full_name: The user's display name.
            email: Unique email address used for authentication.
            avatar: Avatar identifier (avatar1–avatar5).
            password: Plaintext password, will be hashed before storage.

        Returns:
            The newly created User instance.
        """
        user = User.objects.create_user(
            email=email,
            password=password,
            full_name=full_name,
            avatar=avatar,
        )
        logger.info("User registered: %s", user.email)
        self._preload_user_data(user)
        return user

    def get_by_id(self, user_id: Any) -> User:
        """Retrieve a user by primary key.

        Args:
            user_id: UUID of the user.

        Returns:
            The User instance.

        Raises:
            User.DoesNotExist: If no active user with the given id exists.
        """
        return self._qs.get(id=user_id)

    def _preload_user_data(self, user: User) -> None:
        """Create default lists, habits, and seed historical logs for a new user."""
        from apps.habits.models import Habit, HabitLog, HabitTemplate, ListTemplate
        from apps.lists.models import HabitList

        list_templates = ListTemplate.objects.all()
        list_map: dict[str, HabitList] = {}

        for template in list_templates:
            is_default = template.title.lower() == "default"
            habit_list = HabitList.objects.create(
                title=template.title,
                user=user,
                is_default=is_default,
            )
            list_map[template.title] = habit_list

        default_list = list_map.get("Default") or HabitList.objects.create(
            title="Default",
            user=user,
            is_default=True,
        )

        habit_templates = HabitTemplate.objects.select_related("list_template").all()
        created_habits: list[Habit] = []

        for habit_template in habit_templates:
            target_list = list_map.get(habit_template.list_template.title, default_list)
            from apps.habits.analytics import calculate_due_window

            due_from, due_to = calculate_due_window(habit_template.periodicity, timezone.now())
            habit = Habit.objects.create(
                title=habit_template.title,
                periodicity=habit_template.periodicity,
                list=target_list,
                user=user,
                due_from=due_from,
                due_to=due_to,
            )
            created_habits.append(habit)

        self._seed_habit_logs(user, created_habits, default_list)
        logger.info("Preloaded data for user: %s", user.email)

    def _seed_habit_logs(self, user: User, habits: list["Any"], default_list: "Any") -> None:
        """Create 70 historical habit logs spread across the past 3 months.

        Ensures at least one log for a monthly habit and one for a daily habit.
        Spreads logs evenly across the 90-day window for realistic history.
        """
        from apps.habits.models import HabitLog

        now = timezone.now()
        logs_to_create: list[HabitLog] = []
        log_count = 0
        target_count = 70
        window_days = 90

        daily_habits = [h for h in habits if h.periodicity == "daily"]
        monthly_habits = [h for h in habits if h.periodicity == "monthly"]
        all_habits = habits[:]

        # Guarantee at least 1 daily log
        if daily_habits:
            habit = daily_habits[0]
            days_ago = random.randint(1, window_days - 1)
            log_time = now - timedelta(days=days_ago)
            logs_to_create.append(
                HabitLog(
                    habit=habit,
                    user=user,
                    list=habit.list,
                    created_at=log_time,
                    updated_at=log_time,
                )
            )
            log_count += 1

        # Guarantee at least 1 monthly log
        if monthly_habits:
            habit = monthly_habits[0]
            days_ago = random.randint(5, window_days - 1)
            log_time = now - timedelta(days=days_ago)
            logs_to_create.append(
                HabitLog(
                    habit=habit,
                    user=user,
                    list=habit.list,
                    created_at=log_time,
                    updated_at=log_time,
                )
            )
            log_count += 1

        # Fill remaining logs randomly spread across the full 3-month window
        while log_count < target_count and all_habits:
            habit = random.choice(all_habits)
            days_ago = random.randint(1, window_days)
            # Add some hour/minute variation to avoid clustering at midnight
            hours_offset = random.randint(6, 22)
            log_time = (now - timedelta(days=days_ago)).replace(
                hour=hours_offset, minute=random.randint(0, 59), second=0, microsecond=0
            )
            logs_to_create.append(
                HabitLog(
                    habit=habit,
                    user=user,
                    list=habit.list,
                    created_at=log_time,
                    updated_at=log_time,
                )
            )
            log_count += 1

        HabitLog.objects.bulk_create(logs_to_create)
