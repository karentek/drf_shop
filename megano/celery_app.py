import os
import time
from celery import Celery
from django.conf import settings
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'megano.settings')

app = Celery('megano')

app.config_from_object('django.conf:settings')
app.conf.broker_url = settings.CELERY_BROKER_URL
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "task_store_loader":
        {
            "schedule": crontab(minute=1, hour=0),
        }
}