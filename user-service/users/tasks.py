# users/tasks.py
from celery import shared_task, Celery
from django.core.mail import send_mail
from django.conf import settings

# local tasks inside user-service
@shared_task
def send_welcome_email(email, username=None):
    subject = "Welcome"
    message = f"Hello {username or ''}, welcome!"
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
    except Exception as e:
        # log and continue
        print("Failed to send email:", e)
    return True

# A Celery app instance for sending cross-service tasks by name.
# We can use the same broker URL (this creates a lightweight client)
cross_service_client = Celery(broker="amqp://guest:guest@localhost:5672//")

def emit_user_created_event(user_id, role, profile_payload=None):
    """
    Emit an event for other services to consume.
    - For client: task name "client_service.tasks.create_client_profile"
    - For advocate: task name "advocate_service.tasks.create_advocate_profile"
    profile_payload is a dict (phone_number, bar_council_number etc)
    """
    if role == "client":
        cross_service_client.send_task(
            "client_service.tasks.create_client_profile",
            args=[user_id],
        )
    elif role == "advocate":
        # keep profile payload minimal and safe
        payload = profile_payload or {}
        cross_service_client.send_task(
            "advocate_service.tasks.create_advocate_profile",
            args=[user_id, payload],
        )
