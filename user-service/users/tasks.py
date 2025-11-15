from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_welcome_email_task(email, username):
    try:
        send_mail(
            subject="Welcome to Our Platform",
            message=f"Hello {username},\n\nThank you for registering!",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False
        )
    except Exception as e:
        print(f"Failed to send welcome email: {e}")
