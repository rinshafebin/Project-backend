from rest_framework import permissions
from chat.utils.auth import validate_token 

class IsAuthenticatedViaUserService(permissions.BasePermission):

    def has_permission(self, request, view):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            print("No Authorization header or wrong format")
            return False
        
        token = auth_header.split(" ")[1]
        print("Token received:", token)
        user_data = validate_token(token)
        if not user_data:
            print("Token validation failed")
            return False
        
        print("Token valid, user data:", user_data)
        request.user_data = user_data
        return True
