"""Unit tests for UserService."""

import pytest

from apps.users.models import User
from apps.users.services import UserService


@pytest.mark.django_db
class TestUserService:
    """Tests for UserService registration and preload logic."""

    def test_register_creates_user(self) -> None:
        """register() creates a User with the provided attributes."""
        service = UserService()
        user = service.register(
            full_name="Alice Smith",
            email="alice@example.com",
            avatar="avatar2",
            password="securepass123",
        )

        assert User.objects.filter(email="alice@example.com").exists()
        assert user.full_name == "Alice Smith"
        assert user.avatar == "avatar2"

    def test_register_hashes_password(self) -> None:
        """The stored password is a hash, not plaintext."""
        service = UserService()
        user = service.register(
            full_name="Bob Jones",
            email="bob@example.com",
            avatar="avatar1",
            password="mypassword123",
        )

        assert user.password != "mypassword123"
        assert user.check_password("mypassword123")

    def test_register_creates_default_list(self) -> None:
        """Registering a user creates a Default list."""
        from apps.lists.models import HabitList

        service = UserService()
        user = service.register(
            full_name="Carol White",
            email="carol@example.com",
            avatar="avatar3",
            password="securepass123",
        )

        assert HabitList.objects.filter(user=user, is_default=True).exists()

    def test_register_preloads_habits(self) -> None:
        """Registering a user creates habits from templates."""
        from apps.habits.models import Habit

        service = UserService()
        user = service.register(
            full_name="Dave Brown",
            email="dave@example.com",
            avatar="avatar1",
            password="securepass123",
        )

        assert Habit.objects.filter(user=user).count() > 0

    def test_register_creates_habit_logs(self) -> None:
        """Registering a user creates 70 historical habit logs over 3 months."""
        from apps.habits.models import HabitLog

        service = UserService()
        user = service.register(
            full_name="Eve Davis",
            email="eve@example.com",
            avatar="avatar1",
            password="securepass123",
        )

        assert HabitLog.objects.filter(user=user).count() == 70
