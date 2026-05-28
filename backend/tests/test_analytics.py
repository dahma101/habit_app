"""Unit tests for pure analytics functions."""

from datetime import datetime, timezone

import pytest

from apps.habits.analytics import (
    advance_due_window,
    build_general_report,
    build_habit_history_report,
    calculate_due_window,
    compute_longest_streak,
    find_least_tracked_habit,
    group_habits_by_periodicity,
    is_within_due_window,
)


class FakeHabit:
    """Minimal habit stub for analytics tests."""

    def __init__(self, periodicity: str, streak_count: int, habit_id: str = "abc") -> None:
        self.id = habit_id
        self.periodicity = periodicity
        self.streak_count = streak_count
        self.title = "Test Habit"
        self.due_from = None
        self.due_to = None
        self.last_check_time = None
        self.list_id = None


class FakeLog:
    """Minimal log stub for analytics tests."""

    def __init__(self, created_at: datetime, log_id: str = "log1") -> None:
        self.id = log_id
        self.created_at = created_at


class TestCalculateDueWindow:
    """Tests for calculate_due_window() pure function."""

    def test_daily_spans_one_day(self) -> None:
        ref = datetime(2024, 6, 15, 10, 0, 0, tzinfo=timezone.utc)
        due_from, due_to = calculate_due_window("daily", ref)

        assert due_from.date() == ref.date()
        assert due_to.date() == ref.date()
        assert due_to > due_from

    def test_as_many_as_possible_spans_today(self) -> None:
        ref = datetime(2024, 6, 15, 14, 30, 0, tzinfo=timezone.utc)
        due_from, due_to = calculate_due_window("as_many_as_possible", ref)

        assert due_from.date() == ref.date()
        assert due_to.date() == ref.date()
        assert due_to > due_from

    def test_weekly_starts_on_monday(self) -> None:
        ref = datetime(2024, 6, 19, 10, 0, 0, tzinfo=timezone.utc)  # Wednesday
        due_from, due_to = calculate_due_window("weekly", ref)

        assert due_from.weekday() == 0  # Monday

    def test_monthly_spans_full_month(self) -> None:
        ref = datetime(2024, 6, 15, 10, 0, 0, tzinfo=timezone.utc)
        due_from, due_to = calculate_due_window("monthly", ref)

        assert due_from.day == 1
        assert due_to.month == 6

    def test_twice_monthly_first_half(self) -> None:
        ref = datetime(2024, 6, 10, 10, 0, 0, tzinfo=timezone.utc)
        due_from, due_to = calculate_due_window("twice_monthly", ref)

        assert due_from.day == 1
        assert due_to.day == 15

    def test_twice_monthly_second_half(self) -> None:
        ref = datetime(2024, 6, 20, 10, 0, 0, tzinfo=timezone.utc)
        due_from, _ = calculate_due_window("twice_monthly", ref)

        assert due_from.day == 16


class TestIsWithinDueWindow:
    """Tests for is_within_due_window() pure function."""

    def test_within_window_returns_true(self) -> None:
        now = datetime(2024, 6, 15, 12, 0, tzinfo=timezone.utc)
        due_from = datetime(2024, 6, 15, 0, 0, tzinfo=timezone.utc)
        due_to = datetime(2024, 6, 15, 23, 59, tzinfo=timezone.utc)

        assert is_within_due_window(due_from, due_to, now) is True

    def test_outside_window_returns_false(self) -> None:
        now = datetime(2024, 6, 16, 12, 0, tzinfo=timezone.utc)
        due_from = datetime(2024, 6, 15, 0, 0, tzinfo=timezone.utc)
        due_to = datetime(2024, 6, 15, 23, 59, tzinfo=timezone.utc)

        assert is_within_due_window(due_from, due_to, now) is False

    def test_none_window_returns_false(self) -> None:
        now = datetime(2024, 6, 15, 12, 0, tzinfo=timezone.utc)

        assert is_within_due_window(None, None, now) is False


class TestComputeLongestStreak:
    """Tests for compute_longest_streak() pure function."""

    def test_empty_list_returns_zero(self) -> None:
        assert compute_longest_streak([]) == 0

    def test_returns_max_streak(self) -> None:
        habits = [FakeHabit("daily", 3), FakeHabit("weekly", 10), FakeHabit("monthly", 5)]
        assert compute_longest_streak(habits) == 10


class TestGroupHabitsByPeriodicity:
    """Tests for group_habits_by_periodicity() pure function."""

    def test_groups_correctly(self) -> None:
        habits = [
            FakeHabit("daily", 1),
            FakeHabit("daily", 2),
            FakeHabit("weekly", 3),
        ]
        result = group_habits_by_periodicity(habits)

        assert len(result["daily"]) == 2
        assert len(result["weekly"]) == 1


class TestFindLeastTrackedHabit:
    """Tests for find_least_tracked_habit() pure function."""

    def test_empty_returns_none(self) -> None:
        assert find_least_tracked_habit([]) is None

    def test_returns_habit_with_lowest_streak(self) -> None:
        h1 = FakeHabit("daily", 10)
        h2 = FakeHabit("monthly", 1)
        h3 = FakeHabit("weekly", 5)
        assert find_least_tracked_habit([h1, h2, h3]) is h2

    def test_uses_log_count_when_available(self) -> None:
        h1 = FakeHabit("daily", 10)
        h1.log_count = 20  # type: ignore[attr-defined]
        h2 = FakeHabit("monthly", 1)
        h2.log_count = 3  # type: ignore[attr-defined]
        assert find_least_tracked_habit([h1, h2]) is h2


class TestBuildGeneralReport:
    """Tests for build_general_report() pure function."""

    def test_report_structure(self) -> None:
        habits = [FakeHabit("daily", 5), FakeHabit("monthly", 2)]
        report = build_general_report(habits)

        assert "tracked_habits" in report
        assert "habits_by_periodicity" in report
        assert "longest_streak" in report
        assert "least_tracked_habit" in report
        assert report["longest_streak"] == 5
        assert report["least_tracked_habit"] is not None


class TestBuildHabitHistoryReport:
    """Tests for build_habit_history_report() pure function."""

    def test_history_report_structure(self) -> None:
        habit = FakeHabit("daily", 7, "habit-uuid")
        logs = [
            FakeLog(datetime(2024, 6, 14, 10, 0, tzinfo=timezone.utc), "log1"),
            FakeLog(datetime(2024, 6, 13, 10, 0, tzinfo=timezone.utc), "log2"),
        ]
        report = build_habit_history_report(habit, logs)

        assert report["streak_count"] == 7
        assert len(report["log_history"]) == 2
        assert report["log_history"][0]["id"] == "log1"


class TestAdvanceDueWindow:
    """Tests for advance_due_window() pure function."""

    def test_advance_daily_moves_to_next_day(self) -> None:
        current_due_to = datetime(2024, 6, 15, 23, 59, 59, tzinfo=timezone.utc)
        next_from, next_to = advance_due_window("daily", current_due_to)

        assert next_from.date().day == 16
