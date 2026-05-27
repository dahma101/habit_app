"""Custom DRF permission classes."""

from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView


class IsOwner(permissions.BasePermission):
    """Allow access only to the owner of the object.

    Expects the object to have a ``user_id`` attribute that matches
    the authenticated request user's id.
    """

    message: str = "You do not have permission to access this resource."

    def has_object_permission(self, request: Request, view: APIView, obj: object) -> bool:
        """Return True if the request user owns the object."""
        return bool(getattr(obj, "user_id", None) == request.user.id)
