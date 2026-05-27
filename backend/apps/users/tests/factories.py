"""Factory definitions for user-related test data."""

import factory
from factory.django import DjangoModelFactory

from apps.users.models import User


class UserFactory(DjangoModelFactory):
    """Factory for creating User instances in tests."""

    class Meta:
        model = User

    full_name = factory.Faker("name")
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    avatar = User.AvatarChoices.AVATAR1
    password = factory.PostGenerationMethodCall("set_password", "testpass123")
