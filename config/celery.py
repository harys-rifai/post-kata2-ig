import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.beat_schedule = {
    "publish_scheduled_posts": {
        "task": "posts.tasks.auto_publish_post",
        "schedule": crontab(minute="*/5"),
    },
    "retry_failed_posts": {
        "task": "posts.tasks.retry_failed_posts",
        "schedule": crontab(minute="*/10"),
    },
}

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
