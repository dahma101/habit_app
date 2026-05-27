"""Serializers for user registration, authentication, and profile."""

from rest_framework import serializers

from .models import User


class RegisterSerializer(serializers.Serializer):
    """Validates user registration input.

    Enforces minimum password length and unique email constraint.
    """

    full_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    avatar = serializers.ChoiceField(choices=User.AvatarChoices.choices)
    password = serializers.CharField(min_length=8, write_only=True)

    def validate_email(self, value: str) -> str:
        """Ensure the email is not already in use by an active user."""
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()


class LoginSerializer(serializers.Serializer):
    """Validates user login credentials."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserSerializer(serializers.ModelSerializer["User"]):
    """Read-only representation of the authenticated user."""

    class Meta:
        model = User
        fields = ["id", "full_name", "email", "avatar", "created_at"]
        read_only_fields = fields
