"""Celery worker tasks.

Each task runs in a forked worker process, so the singleton
SessionStore / JobTracker created at module import bind their
Redis connection lazily on first use - per-process.

We use `asyncio.run` because `get_event_loop()` is deprecated
in Python 3.11 outside an already-running loop.
"""

from __future__ import annotations

import asyncio
import logging
import os

from celery_app import celery_app
from job_tracker import JobTracker
from session_store import SessionStore

logger = logging.getLogger(__name__)

job_tracker = JobTracker()
session_store = SessionStore()


@celery_app.task(bind=True, name="worker_tasks.process_cv_task")
def process_cv_task(self, file_path: str, filename: str, session_id: str, job_id: str):
    """Parse CV file via Phase 3+4, persist results.

    Status flow on the JobTracker:
        PROCESSING -> COMPLETED (with `result` payload)
        PROCESSING -> FAILED (with `error` message)
    """
    # Importing here keeps worker fork-time fast and avoids loading PhoBERT
    # in the FastAPI process that only enqueues jobs.
    import pipeline_bridge

    async def _run():
        await job_tracker.update_status(job_id, "PROCESSING")
        try:
            result = pipeline_bridge.run_phase34(file_path)
            result["session_id"] = session_id or ""
            result["task_type"] = "upload"
            result["response"] = (
                f"✅ Đã trích xuất xong CV ({result.get('num_experience', 0)} kinh nghiệm, "
                f"{result.get('num_skills', 0)} kỹ năng). Bạn muốn mình đánh giá ngay không?"
            )
            result["metadata"] = {
                "quality_score": result.get("quality_score", 0),
                "num_experience": result.get("num_experience", 0),
                "num_skills": result.get("num_skills", 0),
                "phase3_time_s": result.get("phase3_time_s", 0.0),
                "phase4_time_s": result.get("phase4_time_s", 0.0),
                "parse_time_s": result.get("parse_time_s", 0.0),
            }

            if session_id and result.get("resume_id"):
                await session_store.set_resume(
                    session_id,
                    result["resume_id"],
                    result["resume_dict"],
                    result["resume_name"],
                )

            await job_tracker.update_status(job_id, "COMPLETED", result=result)
        except Exception as e:
            logger.exception(f"process_cv_task failed for job {job_id}")
            await job_tracker.update_status(job_id, "FAILED", error=str(e))
        finally:
            # Best-effort temp file cleanup
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception:
                pass

    asyncio.run(_run())
