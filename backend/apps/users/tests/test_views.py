"""Integration tests for user authentication endpoints."""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User

from .factories import UserFactory


@pytest.fixture
def client() -> APIClient:
    """Return an unauthenticated API client."""
    return APIClient()


@pytest.fixture
def user(db: object) -> User:
    """Create and return a test user."""
    return UserFactory()


@pytest.fixture
def auth_client(client: APIClient, user: User) -> APIClient:
    """Return an authenticated API client."""
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


@pytest.mark.django_db
class TestRegister:
    """Tests for POST /api/v1/auth/register/."""

    def test_register_returns_tokens(self, client: APIClient) -> None:
        """Successful registration returns access and refresh tokens."""
        payload = {
            "full_name": "Test User",
            "email": "test@example.com",
            "avatar": "avatar1",
            "password": "securepass123",
        }
        response = client.post(reverse("auth-register"), payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert "access" in response.data
        assert "refresh" in response.data
        assert response.data["user"]["email"] == "test@example.com"

    def test_register_duplicate_email_fails(self, client: APIClient, user: User) -> None:
        """Registering with an existing email returns 400."""
        payload = {
            "full_name": "Another User",
            "email": user.email,
            "avatar": "avatar1",
            "password": "securepass123",
        }
        response = client.post(reverse("auth-register"), payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_short_password_fails(self, client: APIClient) -> None:
        """Password shorter than 8 characters is rejected."""
        payload = {
            "full_name": "Test User",
            "email": "new@example.com",
            "avatar": "avatar1",
            "password": "short",
        }
        response = client.post(reverse("auth-register"), payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLogin:
    """Tests for POST /api/v1/auth/login/."""

    def test_login_valid_credentials(self, client: APIClient, user: User) -> None:
        """Valid credentials return access and refresh tokens."""
        response = client.post(
            reverse("auth-login"),
            {"email": user.email, "password": "testpass123"},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data

    def test_login_wrong_password(self, client: APIClient, user: User) -> None:
        """Wrong password returns 401."""
        response = client.post(
            reverse("auth-login"),
            {"email": user.email, "password": "wrongpassword"},
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestMe:
    """Tests for GET /api/v1/auth/me/."""

    def test_me_authenticated(self, auth_client: APIClient, user: User) -> None:
        """Authenticated request returns user profile."""
        response = auth_client.get(reverse("auth-me"))

        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == user.email

    def test_me_unauthenticated(self, client: APIClient) -> None:
        """Unauthenticated request returns 401."""
        response = client.get(reverse("auth-me"))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
