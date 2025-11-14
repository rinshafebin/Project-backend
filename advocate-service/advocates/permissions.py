# advocates/permissions.py
from rest_framework.permissions import BasePermission

class IsAdvocate(BasePermission):
    """
    Allow only users with role 'advocate'.
    """
    def has_permission(self, request, view):
        user = request.user
        return bool(user and getattr(user, "role", None) == "advocate")
