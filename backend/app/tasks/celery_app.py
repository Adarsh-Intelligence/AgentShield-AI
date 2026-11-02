from __future__ import annotations

import os
from celery import Celery
from backend.app.config import settings

celery_app = Celery(
    "agentshield",
    broker=settings.broker_url,
    backend=settings.result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 minutes max per test run
    worker_prefetch_multiplier=1,
)

celery_app.autodiscover_tasks(["backend.app.tasks"])

