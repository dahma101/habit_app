"""Integration tests for habit list endpoints."""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.tests.factories import UserFactory

from .factories import DefaultHabitListFactory, HabitListFactory


@pytest.fixture
def user(db: object):  # type: ignore[no-untyped-def]
    """Create and return a test user."""
    return UserFactory()


@pytest.fixture
def auth_client(user):  # type: ignore[no-untyped-def]
    """Return an authenticated API client."""
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


@pytest.mark.django_db
class TestListCRUD:
    """Tests for list create, read, update, delete."""

    def test_get_lists(self, auth_client: APIClient, user) -> None:  # type: ignore[no-untyped-def]
        """GET /lists/ returns all lists for the user."""
        HabitListFactory.create_batch(3, user=user)
        response = auth_client.get(reverse("list-list"))

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 3

    def test_create_list(self, auth_client: APIClient, user) -> None:  # type: ignore[no-untyped-def]
        """POST /lists/ creates a new list."""
        response = auth_client.post(reverse("list-list"), {"title": "My List"}, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "My List"

    def test_create_default_name_rejected(self, auth_client: APIClient) -> None:
        """Creating a list named 'Default' is rejected."""
        response = auth_client.post(reverse("list-list"), {"title": "Default"}, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_list(self, auth_client: APIClient, user) -> None:  # type: ignore[no-untyped-def]
        """PUT /lists/:id/ updates the list title."""
        habit_list = HabitListFactory(user=user, title="Old Title")
        url = reverse("list-detail", kwargs={"pk": habit_list.id})
        response = auth_client.put(url, {"title": "New Title"}, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "New Title"

    def test_delete_list(self, auth_client: APIClient, user) -> None:  # type: ignore[no-untyped-def]
        """DELETE /lists/:id/ soft-deletes the list."""
        DefaultHabitListFactory(user=user)
        habit_list = HabitListFactory(user=user)
        url = reverse("list-detail", kwargs={"pk": habit_list.id})
        response = auth_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        habit_list.refresh_from_db()
        assert habit_list.deleted_at is not None

    def test_delete_default_list_rejected(self, auth_client: APIClient, user) -> None:  # type: ignore[no-untyped-def]
        """Deleting the default list returns 400."""
        default_list = DefaultHabitListFactory(user=user)
        url = reverse("list-detail", kwargs={"pk": default_list.id})
        response = auth_client.delete(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_cannot_access_other_users_list(self, auth_client: APIClient) -> None:
        """A user cannot update another user's list."""
        other_user = UserFactory()
        other_list = HabitListFactory(user=other_user)
        url = reverse("list-detail", kwargs={"pk": other_list.id})
        response = auth_client.put(url, {"title": "Hacked"}, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND
