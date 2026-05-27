"""Serializers for habit list CRUD operations."""

from rest_framework import serializers

from .models import HabitList


class HabitListSerializer(serializers.ModelSerializer["HabitList"]):
    """Full representation of a habit list."""

    class Meta:
        model = HabitList
        fields = ["id", "title", "is_default", "created_at", "updated_at"]
        read_only_fields = ["id", "is_default", "created_at", "updated_at"]


class HabitListCreateSerializer(serializers.Serializer):
    """Validates list creation input."""

    title = serializers.CharField(max_length=255)

    def validate_title(self, value: str) -> str:
        """Ensure list title is not 'Default' (reserved)."""
        if value.strip().lower() == "default":
            raise serializers.ValidationError("'Default' is a reserved list name.")
        return value.strip()


class HabitListUpdateSerializer(serializers.Serializer):
    """Validates list update input."""

    title = serializers.CharField(max_length=255)

    def validate_title(self, value: str) -> str:
        """Ensure list title is not 'Default' (reserved)."""
        if value.strip().lower() == "default":
            raise serializers.ValidationError("'Default' is a reserved list name.")
        return value.strip()
