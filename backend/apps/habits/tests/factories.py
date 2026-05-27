"""Factory definitions for habit-related test data."""

import factory
from factory.django import DjangoModelFactory

from apps.habits.models import Habit, HabitLog, PeriodicityChoices
from apps.lists.tests.factories import DefaultHabitListFactory
from apps.users.tests.factories import UserFactory


class HabitFactory(DjangoModelFactory):
    """Factory for creating Habit instances in tests."""

    class Meta:
        model = Habit

    title = factory.Sequence(lambda n: f"Habit {n}")
    periodicity = PeriodicityChoices.DAILY
    user = factory.SubFactory(UserFactory)
    list = factory.SubFactory(DefaultHabitListFactory, user=factory.SelfAttribute("..user"))
    streak_count = 0


class HabitLogFactory(DjangoModelFactory):
    """Factory for creating HabitLog instances in tests."""

    class Meta:
        model = HabitLog

    habit = factory.SubFactory(HabitFactory)
    user = factory.SelfAttribute("habit.user")
    list = factory.SelfAttribute("habit.list")
