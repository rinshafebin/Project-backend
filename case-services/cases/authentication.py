from django.contrib.auth import get_user_model
import jwt
from django.conf import settings 
from rest_framework import authentication, exceptions


User = get_user_model()


class CustomJWTAuthentication(authentication.BaseAuthentication):

    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None

        try:
            prefix, token = auth_header.split(' ')
            if prefix.lower() != 'bearer':
                return None
        except ValueError:
            return None

        try:
            payload = jwt.decode(
                token,
                settings.SIMPLE_JWT['JWT_SECRET_KEY'],  # <-- Access JWT secret via settings
                algorithms=[settings.SIMPLE_JWT['ALGORITHM']]
            )
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid token')

        try:
            user_id = payload.get('user_id') 
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('User not found')

        return (user, None)
