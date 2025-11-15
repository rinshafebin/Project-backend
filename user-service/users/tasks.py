# user_service/tasks.py
from celery import Celery, shared_task
from django.core.mail import send_mail
from django.conf import settings

from .models import User
from .serializers import UserSerializer


cross_service_client = Celery(
    broker="amqp://guest:guest@localhost:5672//",
    backend="rpc://",
)


@shared_task(bind=True, name="user_service.tasks.send_welcome_email", max_retries=3)
def send_welcome_email(self, email, role):
    subject = "Welcome to Our Platform"
    message = f"Hello! Your account as a '{role}' has been successfully created."
    from_email = settings.DEFAULT_FROM_EMAIL

    try:
        send_mail(subject, message, from_email, [email])
        return {"status": "sent", "email": email}

    except Exception as e:
        # Retry after 10 seconds
        raise self.retry(exc=e, countdown=10)



def emit_user_created_event(user_id, role, profile_payload=None):
    if role == "client":
        cross_service_client.send_task(
            "client_service.tasks.create_client_profile",
            args=[user_id],
        )

    elif role == "advocate":
        payload = profile_payload or {}
        cross_service_client.send_task(
            "advocate_service.tasks.create_advocate_profile",
            args=[user_id, payload],
        )



@shared_task(name="user_service.tasks.get_user_info")
def get_user_info(user_id):
    try:
        user = User.objects.get(id=user_id)
        return UserSerializer(user).data
    except User.DoesNotExist:
        return None


@shared_task(name="user_service.tasks.user_created_event")
def user_created_event(user_id, role):
    if role == "advocate":
        cross_service_client.send_task(
            "advocate_service.tasks.create_advocate_profile",
            args=[user_id],
        )


@shared_task(name="user_service.tasks.send_email")
def send_email_task(subject, message, to_email):
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [to_email])
        return "Email sent"
    except Exception as e:
        return f"Failed to send email: {e}"
