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

from celery import signals
from celery_app import celery_app
from job_tracker import JobTracker
from session_store import SessionStore

logger = logging.getLogger(__name__)

job_tracker = JobTracker()
session_store = SessionStore()


@signals.worker_process_init.connect
def _on_worker_init(**kwargs):
    """Pre-warm PhoBERT NER + BGE-M3 at worker startup.

    Runs before any task is consumed so the first PDF upload
    doesn't pay the ~50s model-loading penalty.
    """
    import pipeline_bridge
    logger.info("worker_init: pre-warming pipeline models...")
    pipeline_bridge.warmup()
    logger.info("worker_init: models ready")


@celery_app.task(bind=True, name="worker_tasks.process_cv_task")
def process_cv_task(self, file_path: str, filename: str, session_id: str, job_id: str, user_id: str = ""):
    """Parse CV file via Phase 3+4, persist results.

    Status flow on the JobTracker:
        PROCESSING -> COMPLETED (with `result` payload)
        PROCESSING -> FAILED (with `error` message)
    """
    # Importing here keeps worker fork-time fast and avoids loading PhoBERT
    # in the FastAPI process that only enqueues jobs.
    import pipeline_bridge
    from supabase_client import supabase_client

    async def _run():
        await job_tracker.update_status(job_id, "PROCESSING")
        try:
            result = pipeline_bridge.run_phase34(file_path)
            
            # Strip debug data before storing
            resume_dict = result.get("resume_dict", {})
            for key in ["raw_entities", "chunks", "metadata"]:
                if key in resume_dict:
                    del resume_dict[key]
            result["resume_dict"] = resume_dict
            
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
                
            if user_id:
                supabase_client.upsert_user_resume(
                    user_id=user_id,
                    resume_dict=result["resume_dict"],
                    resume_name=result.get("resume_name", filename),
                    quality_score=result.get("quality_score", 0),
                    num_experience=result.get("num_experience", 0),
                    num_skills=result.get("num_skills", 0)
                )

            await job_tracker.update_status(job_id, "COMPLETED", result=result)
            
            if session_id:
                await session_store.append_history(
                    session_id, "assistant", result["response"]
                )
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
            
            # Prevent "Event loop is closed" on subsequent tasks by 
            # closing connections bound to this task's event loop.
            try:
                await session_store.close()
                await job_tracker.close()
                from mongo_client import mongo_client
                await mongo_client.close()
            except Exception as e:
                logger.error(f"Error closing connections: {e}")

    asyncio.run(_run())
