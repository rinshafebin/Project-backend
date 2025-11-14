# advocates/tasks.py
from celery import shared_task
from django.conf import settings
from .models import AdvocateProfile, Specialization, User

@shared_task(name="advocate_service.tasks.create_advocate_profile")
def create_advocate_profile(user_id, profile_payload=None):
    """
    This task is the consumer for events emitted by user-service.
    Called with:
        send_task("advocate_service.tasks.create_advocate_profile", args=[user_id, payload])
    payload example: {"phone_number":"...", "bar_council_number":"...","full_name":"..."}
    """
    profile_payload = profile_payload or {}
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        # user not found — nothing to do
        return {"error": "user_not_found", "user_id": user_id}

    # If profile already exists, update minimal fields
    profile, created = AdvocateProfile.objects.get_or_create(user=user,
        defaults={
            "full_name": profile_payload.get("full_name", user.username),
            "phone": profile_payload.get("phone_number"),
            "bar_council_id": profile_payload.get("bar_council_number", ""),
            "experience_years": profile_payload.get("experience_years", 0),
        }
    )
    if not created:
        # update some fields if provided
        updated = False
        for key, src_key in (("phone", "phone_number"), ("bar_council_id", "bar_council_number"), ("full_name", "full_name")):
            val = profile_payload.get(src_key)
            if val:
                setattr(profile, key, val)
                updated = True
        if updated:
            profile.save()
    return {"created": created, "profile_id": profile.id}
