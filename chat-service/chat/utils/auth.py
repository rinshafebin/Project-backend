import requests
from django.conf import settings

def validate_token(token):
    """
    Sends JWT token to user-service to verify.
    """
    try:
        response = requests.get(
            f"{settings.USER_SERVICE_URL}/auth/validate-token/",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("valid"):
                return data  
        return None
    except Exception as e:
        print("Error validating token:", e)
        return None
