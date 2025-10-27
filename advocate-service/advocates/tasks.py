from celery import shared_task
import time

@shared_task
def test_celery_task(name):
    print(f"Starting task for {name}...")
    time.sleep(5)
    print(f"Task finished for {name}")
    return f"Done processing {name}"
