import os

from celery import Celery

CELERY_BROKER_URL = (
    f"amqp://{os.getenv('RABBITMQ_USER')}:{os.getenv('RABBITMQ_PASSWORD')}"
    f"@{os.getenv('RABBITMQ_HOST')}:{os.getenv('RABBITMQ_PORT')}//"
)

CELERY_BACKEND_URL = (
    f"redis://:{os.getenv('REDIS_PASSWORD')}"
    f"@{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}/{os.getenv('REDIS_DB')}"
)


app = Celery(
    "runner",
    broker=CELERY_BROKER_URL,
    backend=CELERY_BACKEND_URL,
    include=["worker.main"],
)


app.conf.update(task_track_started=True, acks_late=True)
