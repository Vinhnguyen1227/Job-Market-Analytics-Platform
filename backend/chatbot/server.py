"""FastAPI server - chatbot orchestrator.

Endpoints (see slm_orchestrator_api_pipeline_guide.md):
    POST /api/chat               - sync chat turn
    POST /api/upload             - async CV upload bound to a session
    POST /api/kie                - async CV upload, anonymous (KIE page)
    GET  /api/job/{job_id}       - poll job status
    GET  /health                 - liveness + dependency probes
"""

from __future__ import annotations

import logging
import os
import tempfile
import uuid
from contextlib import asynccontextmanager
from typing import Any, Optional

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import slash_commands
from adapter_manager import adapter_mgr
from data_clients import es_client, qdrant_client
from intent_router import route as router_route
from job_tracker import JobTracker
from response_formatter import format_chat_response, format_error
from session_store import SessionStore
from tool_dispatcher import dispatch

logger = logging.getLogger("chatbot.server")
logging.basicConfig(level=logging.INFO)

session_store = SessionStore()
job_tracker = JobTracker()


# ── Lifespan ─────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    await session_store.connect()
    await job_tracker.connect()
    from mongo_client import mongo_client
    await mongo_client.connect()
    from enum_cache import enum_cache
    await enum_cache.get_valid_cities()
    await enum_cache.get_valid_exp_buckets()
    await enum_cache.get_valid_work_types()
    enum_cache.start_refresh_task()
    logger.info("Chatbot API ready")
    yield
    enum_cache.stop_refresh_task()
    await session_store.close()
    await job_tracker.close()
    await mongo_client.close()
    try:
        await es_client.close()
    except Exception:
        pass


app = FastAPI(title="CareerIntel Chatbot API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Trace ID middleware ─────────────────────────────────────────────

@app.middleware("http")
async def trace_id_middleware(request: Request, call_next):
    trace_id = request.headers.get("x-trace-id") or uuid.uuid4().hex[:12]
    request.state.trace_id = trace_id
    response = await call_next(request)
    response.headers["x-trace-id"] = trace_id
    return response


# ── Schemas ────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    history: list[dict[str, Any]] = []


# ── Helpers ─────────────────────────────────────────────────────────

_AFFIRMATIVE_WORDS = {
    "ok", "ok!", "okay", "yes", "y", "có", "co", "ừ", "uh", "ừm",
    "đồng ý", "dong y", "được", "duoc", "rồi", "roi", "đánh giá",
    "danh gia", "đi", "di", "sure", "yep", "yeah", "vâng", "vang",
    "dạ", "da", "oke", "okie",
}


def _is_affirmative_reply(message: str) -> bool:
    """True if the message is a short affirmative (≤4 words)."""
    words = message.lower().strip().rstrip("!.?").split()
    return len(words) <= 4 and any(w in _AFFIRMATIVE_WORDS for w in words)


def _last_assistant_is_cv_prompt(history: list[dict] | None) -> bool:
    """True if the last assistant message in history is the CV extraction prompt."""
    if not history:
        return False
    for msg in reversed(history):
        if msg.get("role") == "assistant":
            content = msg.get("content", "")
            return "trích xuất" in content.lower() and "đánh giá" in content.lower()
    return False


# ── Routes ─────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    redis_ok = True
    try:
        await session_store.connect()
        await session_store._redis.ping()  # type: ignore[attr-defined]
    except Exception as e:
        logger.warning(f"redis ping fail: {e}")
        redis_ok = False
        
    mongo_ok = True
    try:
        from mongo_client import mongo_client
        await mongo_client.connect()
        await mongo_client._db.command("ping")
    except Exception as e:
        logger.warning(f"mongo ping fail: {e}")
        mongo_ok = False
        
    return {
        "status": "ok",
        "ollama": "up" if await adapter_mgr.health() else "down",
        "redis": "up" if redis_ok else "down",
        "mongo": "up" if mongo_ok else "down",
        "qdrant": "up" if qdrant_client.health() else "down",
        "elasticsearch": "up" if await es_client.health() else "down",
    }


@app.post("/api/chat")
async def chat(req: ChatRequest, request: Request):
    trace_id = getattr(request.state, "trace_id", "")
    message = (req.message or "").strip()
    if not message:
        raise HTTPException(status_code=400, detail="empty_message")

    session_id = await session_store.create(req.session_id)
    session_data = await session_store.get(session_id) or {}
    
    # Supabase Fallback logic
    if req.user_id:
        from supabase_client import supabase_client
        resume_name, resume_json = supabase_client.get_user_resume(req.user_id)
        if resume_json and not session_data.get("resume_id"):
            # Overwrite session data with persistent data ONLY if no session resume exists
            session_data["resume_id"] = req.user_id  # Use user_id as resume_id for db-loaded resumes
            session_data["resume_dict"] = resume_json
            session_data["resume_name"] = resume_name

    # Fetch contextualized history BEFORE saving the current user message
    # to avoid duplicating the user message in the prompt
    history, summary = await session_store.get_contextualized_history(session_id)

    # Now persist the user message (non-fatal if fails)
    try:
        await session_store.append_history(session_id, "user", message)
    except Exception:
        logger.warning(f"Failed to persist user history for session {session_id}, continuing")

    # 1) slash command?
    tc = slash_commands.maybe_handle(message)
    # 2) Adapter A
    if tc is None:
        try:
            route_msg = message
            if message.lower().startswith("/search"):
                route_msg = message[7:].strip()

            tc = await router_route(route_msg)
            logger.info(f"Adapter A tool: {tc.tool}, params: {tc.params}")
            
            if message.lower().startswith("/search") and tc.tool != "search_jobs":
                logger.warning("Adapter A ignored forceful /search prompt, falling back to raw keyword")
                from tool_schemas import ToolCallResult as _TCR
                tc = _TCR(tool="search_jobs", params={"keyword": message[7:].strip()})
                
        except Exception as e:
            logger.exception("intent_router blew up")
            raise HTTPException(
                status_code=422,
                detail=format_error("Không phân loại được câu hỏi.", "router_failed", trace_id),
            ) from e

    # 2b) Context-aware override: short affirmative after CV upload → assess_resume
    #     Adapter A is single-turn and can't see history, so "ok"/"yes"/"có"
    #     after "Bạn muốn mình đánh giá ngay không?" gets misrouted to general_response.
    if (
        tc.tool == "general_response"
        and session_data.get("resume_id")
        and _is_affirmative_reply(message)
        and _last_assistant_is_cv_prompt(history)
    ):
        from tool_schemas import ToolCallResult as _TCR
        tc = _TCR(tool="assess_resume", params={"focus_areas": ["overall"]})
        logger.info(f"Override: general_response → assess_resume (affirmative after CV upload)")

    # 3) dispatch
    try:
        result = await dispatch(tc, session_id, session_data, message, history, summary)
    except Exception as e:
        logger.exception("tool_dispatcher blew up")
        raise HTTPException(
            status_code=500,
            detail=format_error("Lỗi khi chạy công cụ.", "dispatcher_failed", trace_id),
        ) from e

    # 4) persist history (non-fatal if Redis hiccups)
    try:
        await session_store.append_history(session_id, "assistant", result["response"])
    except Exception:
        logger.warning(f"Failed to persist assistant history for session {session_id}, continuing")

    md = result.get("metadata", {}) or {}
    md["trace_id"] = trace_id
    return format_chat_response(
        result["task_type"], result["response"], session_id, md,
    )

@app.get("/api/history/{session_id}")
async def get_chat_history(session_id: str):
    """Return full conversation history for frontend session restore."""
    from mongo_client import mongo_client
    history = await mongo_client.get_history(session_id)
    session = await session_store.get(session_id)
    return {
        "session_id": session_id,
        "history": history,
        "resume_id": session.get("resume_id") if session else None,
        "resume_name": session.get("resume_name") if session else None,
    }


@app.post("/api/upload")
async def upload(file: UploadFile = File(...), session_id: Optional[str] = Form(None), user_id: Optional[str] = Form(None)):
    # We need the worker to know the SAME job_id we return to the FE,
    # so we generate the id here once and pass it both to JobTracker
    # and to the Celery task.
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="missing_file")

    ext = os.path.splitext(file.filename)[1].lower() or ".bin"
    if ext not in {".pdf", ".docx", ".doc", ".png", ".jpg", ".jpeg"}:
        raise HTTPException(status_code=400, detail="unsupported_file_type")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="empty_file")
    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="file_too_large")

    fd, tmp_path = tempfile.mkstemp(suffix=ext)
    with os.fdopen(fd, "wb") as f:
        f.write(content)

    bound_session = await session_store.create(session_id)

    from mongo_client import mongo_client
    await mongo_client.upload_pdf(bound_session, file.filename, content)

    from worker_tasks import process_cv_task
    job_id = uuid.uuid4().hex[:12]
    task = process_cv_task.delay(tmp_path, file.filename, bound_session, job_id, user_id or "")
    # Register the job under the SAME job_id we just gave the worker.
    await _register_job(job_id, bound_session, "upload", task.id)

    return {"job_id": job_id, "status": "PENDING", "session_id": bound_session}


@app.post("/api/kie")
async def kie(file: UploadFile = File(...)):
    """Anonymous CV extraction for the standalone /kie page.

    Same async flow as /api/upload but the worker is told not to
    bind the resume to a session (session_id="").
    """
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="missing_file")

    ext = os.path.splitext(file.filename)[1].lower() or ".bin"
    if ext not in {".pdf", ".docx", ".doc", ".png", ".jpg", ".jpeg"}:
        raise HTTPException(status_code=400, detail="unsupported_file_type")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="empty_file")
    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="file_too_large")

    fd, tmp_path = tempfile.mkstemp(suffix=ext)
    with os.fdopen(fd, "wb") as f:
        f.write(content)

    throwaway_session = await session_store.create(None)

    from mongo_client import mongo_client
    await mongo_client.upload_pdf(throwaway_session, file.filename, content)

    from worker_tasks import process_cv_task
    job_id = uuid.uuid4().hex[:12]
    task = process_cv_task.delay(tmp_path, file.filename, "", job_id)
    await _register_job(job_id, throwaway_session, "kie", task.id)

    return {"job_id": job_id, "status": "PENDING"}


async def _register_job(job_id: str, session_id: str, job_type: str, celery_task_id: str):
    """Insert a job row using a caller-supplied job_id.

    JobTracker.create_job auto-generates the id; we bypass it so the
    FE polling id matches the id the Celery worker will write to.
    """
    await job_tracker.connect()
    import time as _t
    now = _t.time()
    data = {
        "job_id": job_id,
        "session_id": session_id,
        "job_type": job_type,
        "celery_task_id": celery_task_id,
        "status": "PENDING",
        "created_at": str(now),
        "result": "{}",
        "error": "",
    }
    await job_tracker._redis.hset(f"job:{job_id}", mapping=data)  # type: ignore[attr-defined]
    await job_tracker._redis.expire(f"job:{job_id}", 3600)        # type: ignore[attr-defined]
    await job_tracker._redis.zadd(f"session:{session_id}:jobs", {job_id: now})  # type: ignore[attr-defined]
    await job_tracker._redis.expire(f"session:{session_id}:jobs", 3600)         # type: ignore[attr-defined]


@app.get("/api/job/{job_id}")
async def get_job(job_id: str):
    data = await job_tracker.get_status(job_id)
    if data is None:
        raise HTTPException(status_code=404, detail="job_not_found")
    return data
