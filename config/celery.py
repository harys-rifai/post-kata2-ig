import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.beat_schedule = {
    "morning_post": {
        "task": "posts.tasks.auto_publish_post",
        "schedule": crontab(hour=8, minute=0),
    },
    "afternoon_post": {
        "task": "posts.tasks.auto_publish_post",
        "schedule": crontab(hour=13, minute=0),
    },
    "night_post": {
        "task": "posts.tasks.auto_publish_post",
        "schedule": crontab(hour=20, minute=0),
    },
    "generate_morning_content": {
        "task": "scheduler.tasks.generate_daily_content",
        "schedule": crontab(hour=7, minute=30),
    },
    "retry_failed_posts": {
        "task": "posts.tasks.retry_failed_posts",
        "schedule": crontab(hour=6, minute=0),
    },
}

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
