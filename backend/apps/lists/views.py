"""API views for habit list CRUD operations."""

import logging

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.pagination import StandardResultsPagination

from .models import HabitList
from .serializers import HabitListCreateSerializer, HabitListSerializer, HabitListUpdateSerializer
from .services import ListService

logger = logging.getLogger(__name__)


class ListListView(APIView):
    """List all user lists or create a new one."""

    permission_classes = [IsAuthenticated]
    _service = ListService()

    @extend_schema(responses={200: HabitListSerializer(many=True)}, tags=["lists"])
    def get(self, request: Request) -> Response:
        """Return all lists for the authenticated user."""
        queryset = self._service.get_all(request.user.id)
        paginator = StandardResultsPagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = HabitListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(request=HabitListCreateSerializer, responses={201: HabitListSerializer}, tags=["lists"])
    def post(self, request: Request) -> Response:
        """Create a new list for the authenticated user."""
        serializer = HabitListCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            habit_list = self._service.create(
                user_id=request.user.id,
                title=serializer.validated_data["title"],
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(HabitListSerializer(habit_list).data, status=status.HTTP_201_CREATED)


class ListDetailView(APIView):
    """Update or delete a specific habit list."""

    permission_classes = [IsAuthenticated]
    _service = ListService()

    @extend_schema(request=HabitListUpdateSerializer, responses={200: HabitListSerializer}, tags=["lists"])
    def put(self, request: Request, pk: str) -> Response:
        """Update the title of a list."""
        serializer = HabitListUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            habit_list = self._service.update(
                user_id=request.user.id,
                list_id=pk,
                title=serializer.validated_data["title"],
            )
        except HabitList.DoesNotExist:
            return Response({"detail": "List not found."}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(HabitListSerializer(habit_list).data)

    @extend_schema(responses={204: None}, tags=["lists"])
    def delete(self, request: Request, pk: str) -> Response:
        """Soft-delete a list and reassign its habits to the default list."""
        try:
            self._service.delete(user_id=request.user.id, list_id=pk)
        except HabitList.DoesNotExist:
            return Response({"detail": "List not found."}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)
