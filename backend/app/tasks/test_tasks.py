from __future__ import annotations

import asyncio
from typing import Optional
from backend.app.core.logging import logger
from backend.app.database.session import SessionLocal
from backend.app.services.evaluation_service import EvaluationService
from backend.app.tasks.celery_app import celery_app


async def execute_test_suite_job(
    test_suite_id: str,
    agent_id: str,
    prompt_version_id: Optional[str] = None,
) -> str:
    db = SessionLocal()
    try:
        run = await EvaluationService.execute_test_run(
            db=db,
            test_suite_id=test_suite_id,
            agent_id=agent_id,
            prompt_version_id=prompt_version_id,
        )
        return run.id
    except Exception as exc:
        logger.error(f"Background test job failed: {exc}", exc_info=True)
        raise
    finally:
        db.close()


@celery_app.task(name="tasks.run_test_suite")
def run_test_suite_celery(
    test_suite_id: str,
    agent_id: str,
    prompt_version_id: Optional[str] = None,
) -> str:
    """Celery worker task for executing a test run asynchronously."""
    return asyncio.run(
        execute_test_suite_job(
            test_suite_id=test_suite_id,
            agent_id=agent_id,
            prompt_version_id=prompt_version_id,
        )
    )

