"""API views for the habit dashboard (sorted by due date)."""

import logging
from datetime import timedelta

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from django.utils import timezone

from apps.common.pagination import StandardResultsPagination

from .models import Habit
from .serializers import HabitSerializer

logger = logging.getLogger(__name__)


class DashboardView(APIView):
    """Return habits sorted by due date from today to 30 days ahead."""

    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: HabitSerializer(many=True)}, tags=["dashboard"])
    def get(self, request: Request) -> Response:
        """Return all habits sorted by due_from within the next 30 days."""
        now = timezone.now()
        thirty_days = now + timedelta(days=30)

        queryset = (
            Habit.objects.filter(
                user_id=request.user.id,
                due_from__gte=now,
                due_from__lte=thirty_days,
            )
            .select_related("list")
            .order_by("due_from")
        )

        paginator = StandardResultsPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = HabitSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class DashboardListView(APIView):
    """Return habits for a specific list, sorted by due date."""

    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: HabitSerializer(many=True)}, tags=["dashboard"])
    def get(self, request: Request, list_id: str) -> Response:
        """Return habits in the given list, sorted by due_from."""
        now = timezone.now()
        thirty_days = now + timedelta(days=30)

        queryset = (
            Habit.objects.filter(
                user_id=request.user.id,
                list_id=list_id,
                due_from__gte=now,
                due_from__lte=thirty_days,
            )
            .select_related("list")
            .order_by("due_from")
        )

        paginator = StandardResultsPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = HabitSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
