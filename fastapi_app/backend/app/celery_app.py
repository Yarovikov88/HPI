from celery import Celery
import os

# Создаем экземпляр Celery
celery_app = Celery(
    "hpi_tasks",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    include=["app.services.ai"]
)

# Конфигурация
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 минут
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    # Конфигурация для celerybeat-schedule
    beat_schedule_filename=os.path.join("/app/celery", "celerybeat-schedule"),
    beat_schedule_sync_every=1,
)

# Автоматическое обнаружение задач
celery_app.autodiscover_tasks() 