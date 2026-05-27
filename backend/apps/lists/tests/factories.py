"""Factory definitions for list-related test data."""

import factory
from factory.django import DjangoModelFactory

from apps.lists.models import HabitList
from apps.users.tests.factories import UserFactory


class HabitListFactory(DjangoModelFactory):
    """Factory for creating HabitList instances in tests."""

    class Meta:
        model = HabitList

    title = factory.Sequence(lambda n: f"List {n}")
    user = factory.SubFactory(UserFactory)
    is_default = False


class DefaultHabitListFactory(HabitListFactory):
    """Factory for the default HabitList."""

    title = "Default"
    is_default = True
