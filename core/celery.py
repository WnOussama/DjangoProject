import os
from pathlib import Path
from kombu import Exchange, Queue
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("core")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# QUEUE DEFINITIONS
default_ex = Exchange("default", type="direct")

app.conf.task_queues = (
    Queue("debug",         default_ex, routing_key="debug"),
)

#GLOBAL ROUTER TABLE
app.conf.task_routes = {
    #  debug
    "core.celery.debug_task":{"queue": "debug"},
}

# Celery create queues 
app.conf.task_create_missing_queues = True

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
