"""API views for user registration, login, token refresh, and profile."""

import logging
from typing import Any

from django.contrib.auth import authenticate
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import LoginSerializer, RegisterSerializer, UserSerializer
from .services import UserService

logger = logging.getLogger(__name__)


class RegisterView(APIView):
    """Register a new user and return JWT tokens."""

    permission_classes = [AllowAny]
    _service = UserService()

    @extend_schema(
        request=RegisterSerializer,
        responses={201: UserSerializer},
        tags=["auth"],
    )
    def post(self, request: Request) -> Response:
        """Handle user registration."""
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        user = self._service.register(
            full_name=data["full_name"],
            email=data["email"],
            avatar=data["avatar"],
            password=data["password"],
        )

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserSerializer(user).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """Authenticate a user and return JWT tokens."""

    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginSerializer,
        tags=["auth"],
    )
    def post(self, request: Request) -> Response:
        """Handle user login."""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request,
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )

        if user is None:
            return Response(
                {"detail": "Invalid email or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)
        logger.info("User logged in: %s", user.email)
        return Response(
            {
                "user": UserSerializer(user).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }
        )


class RefreshView(APIView):
    """Exchange a refresh token for a new access and refresh token pair."""

    permission_classes = [AllowAny]

    @extend_schema(tags=["auth"])
    def post(self, request: Request) -> Response:
        """Handle token refresh."""
        refresh_token = request.headers.get("Authorization", "").replace("Bearer ", "")

        if not refresh_token:
            return Response(
                {"detail": "Refresh token is required in Authorization header."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            refresh = RefreshToken(refresh_token)
            return Response(
                {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                }
            )
        except TokenError as e:
            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)


class MeView(APIView):
    """Return the authenticated user's profile."""

    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: UserSerializer}, tags=["auth"])
    def get(self, request: Request) -> Response:
        """Return the current user's data."""
        return Response(UserSerializer(request.user).data)
