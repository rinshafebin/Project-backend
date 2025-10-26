from rest_framework.permissions import BasePermission

class IsAdvocate(BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, 'role', None) == 'advocate'

class IsClient(BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, 'role', None) == 'client'

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, 'role', None) == 'admin'
