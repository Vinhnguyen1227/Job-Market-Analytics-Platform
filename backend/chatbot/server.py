"""
Chatbot Backend Server — FastAPI application.

Exposes HTTP endpoints for the Next.js frontend to interact with
the Phase 2→5 resume processing pipeline via conversational chat.

Endpoints:
    POST /api/chat       — Main conversational interface
    POST /api/upload     — Upload + process a resume (Phase 2→4)
    POST /api/task/{t}   — Direct task execution (Phase 5)
    GET  /api/health     — System health check
"""

from __future__ import annotations

import logging
import os
import uuid
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from intent_router import IntentRouter
from response_formatter import ResponseFormatter
from pipeline_bridge import (
    process_resume,
    execute_task,
    general_chat,
    check_health,
    DEFAULT_DB_PATH,
)

# ── Logging ──────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("chatbot-server")

# ── App Setup ────────────────────────────────────────────

app = FastAPI(
    title="CareerIntel Chatbot API",
    description="Backend server connecting the Phase 2→5 pipeline to the chatbot frontend.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Shared Instances ─────────────────────────────────────

router = IntentRouter()
formatter = ResponseFormatter()

# In-memory session store: session_id → {resume_id, resume_dict, resume_name}
# In production, use Redis or a database.
_sessions: dict[str, dict] = {}


# ── Request/Response Models ──────────────────────────────

class ChatRequest(BaseModel):
    """Chat message request."""
    message: str = Field(..., description="User's text message")
    session_id: Optional[str] = Field(None, description="Session ID for resume context")
    history: list[dict] = Field(default_factory=list, description="Chat history")


class ChatResponse(BaseModel):
    """Chat response envelope."""
    response: str = Field(..., description="AI response text (markdown)")
    task_type: str = Field("general", description="Detected intent type")
    session_id: str = Field(..., description="Session ID")
    metadata: dict = Field(default_factory=dict, description="Processing metadata")


class UploadResponse(BaseModel):
    """Resume upload response."""
    success: bool
    resume_id: Optional[str] = None
    resume_name: str = ""
    quality_score: float = 0.0
    is_valid: bool = False
    message: str = ""
    session_id: str = ""
    error: str = ""


class TaskRequest(BaseModel):
    """Direct task execution request."""
    resume_id: Optional[str] = None
    resume_json: Optional[dict] = None
    session_id: Optional[str] = None
    target_role: Optional[str] = None
    generate_roadmap: bool = False


class TaskResponse(BaseModel):
    """Task execution response."""
    success: bool
    task_type: str
    response: str = ""
    raw_result: dict = Field(default_factory=dict)
    error: str = ""
    metadata: dict = Field(default_factory=dict)


class HealthResponse(BaseModel):
    """System health response."""
    status: str
    llm_available: bool = False
    llm_url: str = ""
    llm_model: str = ""
    qdrant_available: bool = False
    qdrant_resume_count: int = 0
    error: str = ""


# ── Helper Functions ─────────────────────────────────────

def _get_or_create_session(session_id: Optional[str]) -> str:
    """Get an existing session or create a new one."""
    if session_id and session_id in _sessions:
        return session_id
    new_id = str(uuid.uuid4())[:8]
    _sessions[new_id] = {
        "resume_id": None,
        "resume_dict": None,
        "resume_name": None,
    }
    return new_id


def _get_session_resume(session_id: str) -> tuple[Optional[str], Optional[dict]]:
    """Get resume_id and resume_dict from session."""
    session = _sessions.get(session_id, {})
    return session.get("resume_id"), session.get("resume_dict")


# ── Endpoints ────────────────────────────────────────────

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """Main conversational chat endpoint.

    Classifies the user's intent, routes to the appropriate Phase 5
    task or general LLM chat, and returns a formatted response.
    """
    session_id = _get_or_create_session(req.session_id)
    resume_id, resume_dict = _get_session_resume(session_id)
    has_resume = resume_id is not None or resume_dict is not None

    # Classify intent
    intent = router.classify(req.message, has_resume=has_resume)
    logger.info(f"Intent: {intent.intent} (confidence={intent.confidence:.2f})")

    # Route to appropriate handler
    if intent.intent in ("assess", "match", "interview") and has_resume:
        # Execute Phase 5 task
        target_role = intent.task_params.get("target_role")
        generate_roadmap = intent.task_params.get("generate_roadmap", False)

        # Default target role for interview if none extracted
        if intent.intent == "interview" and not target_role:
            target_role = "Software Engineer"

        result = await execute_task(
            task_type=intent.intent,
            resume_id=resume_id,
            resume_dict=resume_dict,
            db_path=DEFAULT_DB_PATH,
            target_role=target_role,
            generate_roadmap=generate_roadmap,
        )

        if result.success:
            response_text = formatter.format(
                result.task_type, result.result, result.metadata
            )
        else:
            response_text = formatter.format_error(result.error)

        return ChatResponse(
            response=response_text,
            task_type=intent.intent,
            session_id=session_id,
            metadata=result.metadata,
        )

    elif intent.intent in ("assess", "match", "interview") and not has_resume:
        # User wants a task but hasn't uploaded a resume
        return ChatResponse(
            response=(
                "📎 **Bạn chưa tải lên CV!**\n\n"
                "Để tôi có thể đánh giá, vui lòng tải lên file CV (PDF hoặc DOCX) "
                "bằng cách nhấn nút **+** bên trái ô nhập tin nhắn.\n\n"
                "Sau khi tải lên, bạn có thể yêu cầu:\n"
                '- *"Đánh giá CV của tôi"*\n'
                '- *"Tạo câu hỏi phỏng vấn"*\n'
                '- *"Tìm việc phù hợp"*'
            ),
            task_type="no_resume",
            session_id=session_id,
        )

    else:
        # General LLM chat
        try:
            response_text = await general_chat(req.message, req.history)
        except Exception as e:
            logger.exception("General chat failed")
            response_text = formatter.format_error(str(e))

        return ChatResponse(
            response=response_text,
            task_type="general",
            session_id=session_id,
        )


@app.post("/api/upload", response_model=UploadResponse)
async def upload_endpoint(
    file: UploadFile = File(...),
    session_id: Optional[str] = Form(None),
):
    """Upload and process a resume through Phase 2→4.

    Accepts PDF or DOCX files, runs the full parsing → chunking →
    validation → storage pipeline, and returns the resume_id for
    subsequent Phase 5 task execution.
    """
    # Validate file type
    allowed_extensions = {".pdf", ".docx", ".doc", ".png", ".jpg", ".jpeg"}
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Allowed: {', '.join(allowed_extensions)}"
        )

    # Read file
    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty file")

    if len(file_bytes) > 20 * 1024 * 1024:  # 20MB limit
        raise HTTPException(status_code=400, detail="File too large (max 20MB)")

    sid = _get_or_create_session(session_id)
    logger.info(f"Upload: {file.filename} ({len(file_bytes)} bytes) session={sid}")

    # Process through pipeline
    result = await process_resume(file_bytes, file.filename, db_path=DEFAULT_DB_PATH)

    if result.success:
        # Store in session
        _sessions[sid]["resume_id"] = result.resume_id
        _sessions[sid]["resume_dict"] = result.resume_dict
        _sessions[sid]["resume_name"] = result.resume_name

        message = formatter.format_upload_success(
            result.resume_name, result.quality_score,
            result.is_valid, result.resume_id,
        )

        return UploadResponse(
            success=True,
            resume_id=result.resume_id,
            resume_name=result.resume_name,
            quality_score=result.quality_score,
            is_valid=result.is_valid,
            message=message,
            session_id=sid,
        )
    else:
        return UploadResponse(
            success=False,
            error=result.error,
            message=formatter.format_error(result.error),
            session_id=sid,
        )


@app.post("/api/task/{task_type}", response_model=TaskResponse)
async def task_endpoint(task_type: str, req: TaskRequest):
    """Execute a specific Phase 5 task directly.

    Useful for programmatic access or when the caller knows
    exactly which task to run.
    """
    valid_tasks = {"assess", "match", "interview"}
    if task_type not in valid_tasks:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid task_type: {task_type}. Valid: {valid_tasks}"
        )

    # Get resume from session if needed
    resume_id = req.resume_id
    resume_dict = req.resume_json
    if not resume_id and not resume_dict and req.session_id:
        rid, rdict = _get_session_resume(req.session_id)
        resume_id = resume_id or rid
        resume_dict = resume_dict or rdict

    if not resume_id and not resume_dict:
        raise HTTPException(
            status_code=400,
            detail="No resume provided. Upload a resume first or provide resume_id/resume_json."
        )

    result = await execute_task(
        task_type=task_type,
        resume_id=resume_id,
        resume_dict=resume_dict,
        db_path=DEFAULT_DB_PATH,
        target_role=req.target_role,
        generate_roadmap=req.generate_roadmap,
    )

    response_text = ""
    if result.success:
        response_text = formatter.format(result.task_type, result.result, result.metadata)
    else:
        response_text = formatter.format_error(result.error)

    return TaskResponse(
        success=result.success,
        task_type=task_type,
        response=response_text,
        raw_result=result.result,
        error=result.error,
        metadata=result.metadata,
    )


@app.get("/api/health", response_model=HealthResponse)
async def health_endpoint():
    """Check system health: LLM and Qdrant connectivity."""
    try:
        health = await check_health()
        return HealthResponse(
            status="ok" if health.get("llm_available") else "degraded",
            llm_available=health.get("llm_available", False),
            llm_url=health.get("llm_url", ""),
            llm_model=health.get("llm_model", ""),
            qdrant_available=health.get("qdrant_available", False),
            qdrant_resume_count=health.get("qdrant_resume_count", 0),
        )
    except Exception as e:
        return HealthResponse(
            status="error",
            error=str(e),
        )


@app.get("/")
async def root():
    """Root endpoint — API info."""
    return {
        "name": "CareerIntel Chatbot API",
        "version": "1.0.0",
        "endpoints": [
            "POST /api/chat",
            "POST /api/upload",
            "POST /api/task/{task_type}",
            "GET /api/health",
        ],
    }
