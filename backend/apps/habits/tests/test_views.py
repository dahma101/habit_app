"""Integration tests for habit CRUD and check-in endpoints."""

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.habits.models import Habit, HabitLog
from apps.lists.tests.factories import DefaultHabitListFactory
from apps.users.tests.factories import UserFactory

from .factories import HabitFactory


@pytest.fixture
def user(db: object):  # type: ignore[no-untyped-def]
    """Create and return a test user with a default list."""
    u = UserFactory()
    DefaultHabitListFactory(user=u)
    return u


@pytest.fixture
def auth_client(user):  # type: ignore[no-untyped-def]
    """Return an authenticated API client."""
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


@pytest.mark.django_db
class TestHabitCRUD:
    """Tests for habit create, read, update, delete endpoints."""

    def test_get_habits_empty(self, auth_client: APIClient) -> None:
        """GET /habits/ returns empty list when user has no habits."""
        response = auth_client.get(reverse("habit-list"))

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0

    def test_create_habit(self, auth_client: APIClient, user) -> None:  # type: ignore[no-untyped-def]
        """POST /habits/ creates a new habit with due window."""
        from apps.lists.models import HabitList

        habit_list = HabitList.objects.get(user=user, is_default=True)
        payload = {
            "title": "Morning Run",
            "periodicity": "daily",
            "list_id": str(habit_list.id),
        }
        response = auth_client.post(reverse("habit-list"), payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "Morning Run"
        assert response.data["due_from"] is not None

    def test_get_habit_detail(self, auth_client: APIClient, user) -> None:  # type: ignore[no-untyped-def]
        """GET /habits/:id/ returns a single habit."""
        habit = HabitFactory(user=user)
        url = reverse("habit-detail", kwargs={"pk": habit.id})
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == str(habit.id)

    def test_update_habit(self, auth_client: APIClient, user) -> None:  # type: ignore[no-untyped-def]
        """PUT /habits/:id/ updates habit title."""
        habit = HabitFactory(user=user)
        url = reverse("habit-detail", kwargs={"pk": habit.id})
        response = auth_client.put(url, {"title": "Updated Title"}, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Updated Title"

    def test_delete_habit(self, auth_client: APIClient, user) -> None:  # type: ignore[no-untyped-def]
        """DELETE /habits/:id/ soft-deletes the habit."""
        habit = HabitFactory(user=user)
        url = reverse("habit-detail", kwargs={"pk": habit.id})
        response = auth_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        habit.refresh_from_db()
        assert habit.deleted_at is not None

    def test_cannot_access_other_users_habit(self, auth_client: APIClient) -> None:
        """A user cannot read another user's habit."""
        other_habit = HabitFactory()
        url = reverse("habit-detail", kwargs={"pk": other_habit.id})
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestHabitCheckIn:
    """Tests for the habit check-in endpoint."""

    def test_checkin_within_window_succeeds(self, auth_client: APIClient, user) -> None:  # type: ignore[no-untyped-def]
        """Check-in within due window creates a log and increments streak."""
        now = timezone.now()
        habit = HabitFactory(
            user=user,
            due_from=now - timedelta(hours=1),
            due_to=now + timedelta(hours=1),
        )
        url = reverse("habit-checkin", kwargs={"pk": habit.id})
        response = auth_client.post(url)

        assert response.status_code == status.HTTP_201_CREATED
        habit.refresh_from_db()
        assert habit.streak_count == 1
        assert HabitLog.objects.filter(habit=habit).count() == 1

    def test_checkin_outside_window_fails(self, auth_client: APIClient, user) -> None:  # type: ignore[no-untyped-def]
        """Check-in outside due window returns 400."""
        now = timezone.now()
        habit = HabitFactory(
            user=user,
            due_from=now - timedelta(days=2),
            due_to=now - timedelta(days=1),
        )
        url = reverse("habit-checkin", kwargs={"pk": habit.id})
        response = auth_client.post(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestHabitServices:
    """Tests for HabitService streak reset behavior."""

    def test_streak_reset_on_overdue(self) -> None:
        """Celery task resets streak for habits that missed their due window."""
        from apps.habits.tasks import check_habit_due_dates

        now = timezone.now()
        habit = HabitFactory(
            streak_count=5,
            due_from=now - timedelta(days=2),
            due_to=now - timedelta(days=1),
        )

        reset_count = check_habit_due_dates()

        habit.refresh_from_db()
        assert habit.streak_count == 0
        assert reset_count >= 1
