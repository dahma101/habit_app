"""API views for habit analytics and reporting."""

import logging

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.pagination import StandardResultsPagination

from django.db.models import Count

from .analytics import build_general_report, build_habit_history_report
from .models import Habit, HabitLog
from .serializers import HabitSerializer

logger = logging.getLogger(__name__)


class GeneralReportView(APIView):
    """Return aggregated analytics for all habits of the authenticated user."""

    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["reports"])
    def get(self, request: Request) -> Response:
        """Return tracked habits, habits by periodicity, and longest streak."""
        habits = list(
            Habit.objects.filter(user_id=request.user.id)
            .select_related("list")
            .annotate(log_count=Count("logs"))
        )
        report = build_general_report(habits)
        least = report["least_tracked_habit"]

        return Response(
            {
                "tracked_habits": HabitSerializer(report["tracked_habits"], many=True).data,
                "habits_by_periodicity": {
                    k: HabitSerializer(v, many=True).data
                    for k, v in report["habits_by_periodicity"].items()
                },
                "longest_streak": report["longest_streak"],
                "least_tracked_habit": HabitSerializer(least).data if least else None,
            }
        )


class AllHabitsReportView(APIView):
    """Return all habits for the authenticated user (paginated)."""

    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: HabitSerializer(many=True)}, tags=["reports"])
    def get(self, request: Request) -> Response:
        """Return all user habits."""
        queryset = Habit.objects.filter(user_id=request.user.id).select_related("list").order_by("-created_at")
        paginator = StandardResultsPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = HabitSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class HabitReportView(APIView):
    """Return streak and log history for a specific habit."""

    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["reports"])
    def get(self, request: Request, pk: str) -> Response:
        """Return the longest streak and check-in history for one habit."""
        try:
            habit = Habit.objects.get(id=pk, user_id=request.user.id)
        except Habit.DoesNotExist:
            return Response({"detail": "Habit not found."}, status=status.HTTP_404_NOT_FOUND)

        logs = list(
            HabitLog.objects.filter(
                habit=habit,
                deleted_at__isnull=True,
            ).order_by("-created_at")
        )

        report = build_habit_history_report(habit, logs)
        return Response(report)
