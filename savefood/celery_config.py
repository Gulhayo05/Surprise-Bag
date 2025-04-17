# celery_config.py
from celery import Celery
import os

# Celery configuration
celery_app = Celery(
    'surprise_bags',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
    include=['tasks']
)

# Celery configuration settings
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour timeout
    task_soft_time_limit=3300,  # 55 minutes soft timeout
)

# Optional: Configure periodic tasks
celery_app.conf.beat_schedule = {
    'check-expiring-bags': {
        'task': 'tasks.check_expiring_bags',
        'schedule': 3600.0,  # Every hour
    },
}

