import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE","client_service.settings")
app = Celery("client_service")

app.conf.broker_url = "amqp://guest:guest@localhost:5672//"
app.conf.result_backend ="rpc://"

app.autodiscover_tasks()

