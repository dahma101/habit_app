"""API views for habit CRUD and check-in endpoints."""

import logging

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.pagination import StandardResultsPagination

from .models import Habit, HabitLog
from .serializers import (
    HabitCreateSerializer,
    HabitLogSerializer,
    HabitSerializer,
    HabitUpdateSerializer,
)
from .services import HabitService

logger = logging.getLogger(__name__)


class HabitListView(APIView):
    """List all user habits or create a new one."""

    permission_classes = [IsAuthenticated]
    _service = HabitService()

    @extend_schema(responses={200: HabitSerializer(many=True)}, tags=["habits"])
    def get(self, request: Request) -> Response:
        """Return all active habits for the authenticated user."""
        queryset = self._service.get_all(request.user.id)
        paginator = StandardResultsPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = HabitSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(request=HabitCreateSerializer, responses={201: HabitSerializer}, tags=["habits"])
    def post(self, request: Request) -> Response:
        """Create a new habit for the authenticated user."""
        serializer = HabitCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        habit = self._service.create(
            user_id=request.user.id,
            data=serializer.validated_data,
        )
        return Response(HabitSerializer(habit).data, status=status.HTTP_201_CREATED)


class HabitDetailView(APIView):
    """Retrieve, update, or delete a specific habit."""

    permission_classes = [IsAuthenticated]
    _service = HabitService()

    @extend_schema(responses={200: HabitSerializer}, tags=["habits"])
    def get(self, request: Request, pk: str) -> Response:
        """Return a single habit."""
        try:
            habit = self._service.get_by_id(request.user.id, pk)
        except Habit.DoesNotExist:
            return Response({"detail": "Habit not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(HabitSerializer(habit).data)

    @extend_schema(request=HabitUpdateSerializer, responses={200: HabitSerializer}, tags=["habits"])
    def put(self, request: Request, pk: str) -> Response:
        """Update a habit."""
        serializer = HabitUpdateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        try:
            habit = self._service.update(
                user_id=request.user.id,
                habit_id=pk,
                data=serializer.validated_data,
            )
        except Habit.DoesNotExist:
            return Response({"detail": "Habit not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(HabitSerializer(habit).data)

    @extend_schema(responses={204: None}, tags=["habits"])
    def delete(self, request: Request, pk: str) -> Response:
        """Soft-delete a habit."""
        try:
            self._service.delete(request.user.id, pk)
        except Habit.DoesNotExist:
            return Response({"detail": "Habit not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)


class HabitCheckInView(APIView):
    """Record a check-in for a specific habit."""

    permission_classes = [IsAuthenticated]
    _service = HabitService()

    @extend_schema(responses={201: HabitLogSerializer}, tags=["habits"])
    def post(self, request: Request, pk: str) -> Response:
        """Check in a habit within its active due window."""
        try:
            log = self._service.check_in(user_id=request.user.id, habit_id=pk)
        except Habit.DoesNotExist:
            return Response({"detail": "Habit not found."}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(HabitLogSerializer(log).data, status=status.HTTP_201_CREATED)
