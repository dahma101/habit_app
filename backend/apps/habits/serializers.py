"""Serializers for habit CRUD and check-in endpoints."""

from rest_framework import serializers

from apps.lists.models import HabitList

from .models import Habit, HabitLog, PeriodicityChoices


class HabitSerializer(serializers.ModelSerializer["Habit"]):
    """Full representation of a habit, including its list title."""

    list_title = serializers.CharField(source="list.title", read_only=True, allow_null=True)

    class Meta:
        model = Habit
        fields = [
            "id",
            "title",
            "periodicity",
            "list_id",
            "list_title",
            "last_check_time",
            "is_checked",
            "due_from",
            "due_to",
            "streak_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "last_check_time", "is_checked", "streak_count", "created_at", "updated_at"]


class HabitCreateSerializer(serializers.Serializer):
    """Validates habit creation input."""

    title = serializers.CharField(max_length=500)
    periodicity = serializers.ChoiceField(choices=PeriodicityChoices.choices)
    list_id = serializers.UUIDField()

    def validate_list_id(self, value: object) -> object:
        """Ensure the list exists and belongs to the requesting user."""
        request = self.context.get("request")
        if request and not HabitList.objects.filter(id=value, user=request.user).exists():
            raise serializers.ValidationError("List not found.")
        return value


class HabitUpdateSerializer(serializers.Serializer):
    """Validates habit update input (all fields optional)."""

    title = serializers.CharField(max_length=500, required=False)
    periodicity = serializers.ChoiceField(choices=PeriodicityChoices.choices, required=False)
    list_id = serializers.UUIDField(required=False)

    def validate_list_id(self, value: object) -> object:
        """Ensure the list exists and belongs to the requesting user."""
        request = self.context.get("request")
        if request and not HabitList.objects.filter(id=value, user=request.user).exists():
            raise serializers.ValidationError("List not found.")
        return value


class HabitLogSerializer(serializers.ModelSerializer["HabitLog"]):
    """Representation of a habit check-in log entry."""

    class Meta:
        model = HabitLog
        fields = ["id", "habit_id", "list_id", "created_at"]
        read_only_fields = fields
