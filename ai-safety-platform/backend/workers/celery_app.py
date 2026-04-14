from __future__ import annotations

from celery import Celery

from backend.config.settings import settings


celery_app = Celery(
    "ai_safety_platform",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

