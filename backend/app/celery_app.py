from celery import Celery
from .config import get_settings

settings = get_settings()

celery_app = Celery(
    "my_tools",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    worker_prefetch_multiplier=1,
)


@celery_app.task(bind=True, name="default_task")
def default_task(self):
    return {"status": "ok"}
