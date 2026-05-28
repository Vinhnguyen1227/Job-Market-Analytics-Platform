import os
from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

load_dotenv()

broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

app = Celery(
    'scraper',
    broker=broker_url,
    backend=result_backend,
    include=['tasks']
)

app.conf.update(
    result_expires=3600,
)

app.conf.beat_schedule = {
    'scrape-topcv-daily': {
        'task': 'tasks.scrape_topcv',
        'schedule': crontab(hour=0, minute=0), # Midnight every day
    },
}

if __name__ == '__main__':
    app.start()
