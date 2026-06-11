import os
from celery import Celery

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery("chatbot",
  broker=REDIS_URL,
  backend=REDIS_URL,
  include=["worker_tasks"]
)
celery_app.conf.task_routes = {"worker_tasks.*": {"queue": "ml"}}
