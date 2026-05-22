"""
Pipeline Bridge — Adapter between FastAPI server and the chatbot pipeline phases.

Handles the sys.path switching, module imports, and provides clean async-safe
wrappers around Phase 2→5 pipeline runners. Runs pipeline work in a thread pool
to avoid blocking the FastAPI event loop.
"""

from __future__ import annotations

import asyncio
import io
import json
import logging
import os
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field, asdict
from typing import Optional

logger = logging.getLogger(__name__)

# ── Path Setup ───────────────────────────────────────────
# Resolve paths relative to this file → backend/chatbot/
# The chatbot phases live at: <project_root>/chatbot/phase X-*/
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_THIS_DIR, "..", ".."))
_CHATBOT_ROOT = os.path.join(_PROJECT_ROOT, "chatbot")

PHASE2_DIR = os.path.join(_CHATBOT_ROOT, "phase 2-parsing and layout")
PHASE3_DIR = os.path.join(_CHATBOT_ROOT, "phase 3-semantic chunking")
PHASE4_DIR = os.path.join(_CHATBOT_ROOT, "phase 4-validation and storage")
PHASE5_DIR = os.path.join(_CHATBOT_ROOT, "phase 5-rag and tasks")

ALL_PHASE_DIRS = [PHASE2_DIR, PHASE3_DIR, PHASE4_DIR, PHASE5_DIR]

# Default paths
DEFAULT_DB_PATH = os.path.join(_CHATBOT_ROOT, "data", "qdrant_db")
DEFAULT_LLM_URL = "http://localhost:11434/v1"
DEFAULT_MODEL = "qwen2.5:7b"

# Thread pool for blocking pipeline work
_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="pipeline")

# Force UTF-8 stdout on Windows
if sys.platform == "win32":
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "buffer"):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


# ── Result Types ─────────────────────────────────────────

@dataclass
class ResumeProcessResult:
    """Result of processing a resume through Phase 2→4."""
    success: bool = False
    resume_id: Optional[str] = None
    resume_name: str = ""
    quality_score: float = 0.0
    is_valid: bool = False
    error: str = ""
    resume_dict: dict = field(default_factory=dict)
    processing_time_s: float = 0.0


@dataclass
class TaskResult:
    """Result of executing a Phase 5 task."""
    success: bool = False
    task_type: str = ""
    result: dict = field(default_factory=dict)
    error: str = ""
    metadata: dict = field(default_factory=dict)


@dataclass
class ChatResult:
    """Result of a full chat interaction."""
    success: bool = False
    response: str = ""
    task_type: str = "general"
    raw_result: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)


# ── Phase Switching (borrowed from run_pipeline.py) ──────

def _switch_phase(phase_dir: str):
    """Set sys.path so only the given phase dir is active (remove others)."""
    for d in ALL_PHASE_DIRS:
        if d in sys.path:
            sys.path.remove(d)
    sys.path.insert(0, phase_dir)
    # Phase 5 needs Phase 4 for vector_store and embedder
    if phase_dir == PHASE5_DIR:
        if PHASE4_DIR not in sys.path:
            sys.path.append(PHASE4_DIR)
    # Invalidate cached modules from other phases
    for mod_name in list(sys.modules.keys()):
        mod = sys.modules[mod_name]
        if hasattr(mod, "__file__") and mod.__file__:
            for d in ALL_PHASE_DIRS:
                if d == PHASE4_DIR and phase_dir == PHASE5_DIR:
                    if "vector_store" in mod_name or "embedder" in mod_name:
                        continue
                if d != phase_dir and mod.__file__.startswith(d):
                    del sys.modules[mod_name]
                    break


# ── Synchronous Pipeline Runners ─────────────────────────

def _run_phase2(file_path: str) -> dict:
    """Phase 2: Parse document + layout analysis."""
    _switch_phase(PHASE2_DIR)
    from docrag.pipeline import DocumentIngestionPipeline

    pipeline = DocumentIngestionPipeline(
        use_gpu=False,
        layout_method="rule_based",
    )
    result = pipeline.process(file_path, analyze_layout=True)
    return {"parsed": result["parsed"], "layout": result["layout"]}


def _run_phase3_from_pdf(parsed_doc, layout_analysis) -> dict:
    """Phase 3: Semantic chunking from Phase 2 output."""
    _switch_phase(PHASE3_DIR)
    from pipeline import SemanticExtractionPipeline

    pipeline = SemanticExtractionPipeline(
        use_ner=False,
        use_llm=False,
    )
    resume = pipeline.process(parsed_doc, layout_analysis)
    return {"resume": resume}


def _run_phase4(canonical_resume, db_path: str) -> dict:
    """Phase 4: Validate + Embed + Store in Qdrant."""
    _switch_phase(PHASE4_DIR)
    from pipeline import ValidationStoragePipeline

    pipeline = ValidationStoragePipeline(
        use_embeddings=True,
        use_storage=True,
        embedding_device="cpu",
        db_path=db_path,
    )
    validated = pipeline.validate_and_store(canonical_resume)
    point_id = validated.embedding_ids[0] if validated.embedding_ids else None
    return {
        "validated": validated,
        "point_id": point_id,
    }


def _run_phase5_task(
    task_type: str,
    resume_id: Optional[str],
    resume_dict: Optional[dict],
    db_path: str,
    target_role: Optional[str] = None,
    generate_roadmap: bool = False,
) -> dict:
    """Phase 5: Execute a single RAG task."""
    _switch_phase(PHASE5_DIR)
    from pipeline import RAGTaskPipeline
    from schema import TaskRequest

    pipeline = RAGTaskPipeline(
        db_path=db_path,
        llm_base_url=DEFAULT_LLM_URL,
        model_name=DEFAULT_MODEL,
        embedding_device="cpu",
    )

    # Build request
    req_kwargs = {"task_type": task_type}
    if resume_id:
        req_kwargs["resume_id"] = resume_id
    elif resume_dict:
        req_kwargs["resume_json"] = resume_dict

    if target_role:
        req_kwargs["target_role"] = target_role
    if generate_roadmap:
        req_kwargs["generate_roadmap"] = True

    request = TaskRequest(**req_kwargs)
    response = pipeline.execute(request)

    return {
        "task_type": response.task_type,
        "success": response.success,
        "result": response.result.to_dict() if hasattr(response.result, "to_dict") else (response.result or {}),
        "error": response.error,
        "metadata": response.metadata,
    }


def _run_full_pipeline(file_path: str, db_path: str) -> ResumeProcessResult:
    """Run Phase 2 → 3 → 4 on a single file."""
    t0 = time.time()
    try:
        # Phase 2
        p2 = _run_phase2(file_path)

        # Phase 3
        p3 = _run_phase3_from_pdf(p2["parsed"], p2["layout"])
        resume = p3["resume"]

        # Phase 4
        p4 = _run_phase4(resume, db_path)
        validated = p4["validated"]

        name = resume.personal_info.name or os.path.basename(file_path)
        return ResumeProcessResult(
            success=True,
            resume_id=p4["point_id"],
            resume_name=name,
            quality_score=validated.quality_score.overall,
            is_valid=validated.validation_report.is_valid,
            resume_dict=resume.to_dict(),
            processing_time_s=round(time.time() - t0, 2),
        )
    except Exception as e:
        logger.exception("Pipeline failed")
        return ResumeProcessResult(
            success=False,
            error=str(e),
            processing_time_s=round(time.time() - t0, 2),
        )


def _check_llm_health() -> dict:
    """Check LLM and Qdrant availability."""
    _switch_phase(PHASE5_DIR)
    from pipeline import RAGTaskPipeline

    pipeline = RAGTaskPipeline(
        db_path=DEFAULT_DB_PATH,
        llm_base_url=DEFAULT_LLM_URL,
        model_name=DEFAULT_MODEL,
        embedding_device="cpu",
    )
    return pipeline.check_health()


def _general_chat(message: str, history: list[dict] = None) -> str:
    """Direct LLM chat for general questions (no RAG)."""
    _switch_phase(PHASE5_DIR)
    from llm_client import LLMClient

    client = LLMClient(
        base_url=DEFAULT_LLM_URL,
        model=DEFAULT_MODEL,
        temperature=0.7,
        max_tokens=2048,
    )

    system = (
        "Bạn là CareerIntel AI — trợ lý thông minh về thị trường việc làm Việt Nam. "
        "Bạn giúp tư vấn nghề nghiệp, phân tích xu hướng tuyển dụng, và hỗ trợ tìm việc. "
        "Trả lời bằng tiếng Việt, thân thiện và chuyên nghiệp. "
        "Sử dụng markdown để định dạng câu trả lời."
    )

    response = client.generate(
        system_prompt=system,
        user_prompt=message,
        json_mode=False,
    )
    return response.get("raw", response.get("content", "Xin lỗi, tôi không thể trả lời lúc này."))


# ── Async Wrappers (for FastAPI) ─────────────────────────

async def process_resume(file_bytes: bytes, filename: str,
                         db_path: str = DEFAULT_DB_PATH) -> ResumeProcessResult:
    """Process an uploaded resume through Phase 2→4.

    Saves file to a temp location, runs the pipeline in a thread pool,
    then cleans up.

    Args:
        file_bytes: Raw file content.
        filename: Original filename (used for format detection).
        db_path: Qdrant database path.

    Returns:
        ResumeProcessResult with resume_id and quality metrics.
    """
    # Save to temp file (pipeline needs a file path)
    suffix = os.path.splitext(filename)[1]
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix, prefix="chatbot_")
    try:
        tmp.write(file_bytes)
        tmp.flush()
        tmp.close()

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            _executor, _run_full_pipeline, tmp.name, db_path
        )
        return result
    finally:
        try:
            os.unlink(tmp.name)
        except OSError:
            pass


async def execute_task(
    task_type: str,
    resume_id: Optional[str] = None,
    resume_dict: Optional[dict] = None,
    db_path: str = DEFAULT_DB_PATH,
    target_role: Optional[str] = None,
    generate_roadmap: bool = False,
) -> TaskResult:
    """Execute a Phase 5 task asynchronously.

    Args:
        task_type: One of 'assess', 'match', 'interview'.
        resume_id: Qdrant point ID.
        resume_dict: Inline resume dict (alternative).
        db_path: Qdrant database path.
        target_role: Target role for interview/roadmap.
        generate_roadmap: Whether to include study roadmap.

    Returns:
        TaskResult with formatted output.
    """
    loop = asyncio.get_event_loop()
    try:
        raw = await loop.run_in_executor(
            _executor,
            _run_phase5_task,
            task_type, resume_id, resume_dict, db_path,
            target_role, generate_roadmap,
        )
        return TaskResult(
            success=raw["success"],
            task_type=raw["task_type"],
            result=raw["result"],
            error=raw.get("error", ""),
            metadata=raw.get("metadata", {}),
        )
    except Exception as e:
        logger.exception("Task execution failed")
        return TaskResult(
            success=False,
            task_type=task_type,
            error=str(e),
        )


async def general_chat(message: str, history: list[dict] = None) -> str:
    """Run a general LLM chat asynchronously."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, _general_chat, message, history)


async def check_health() -> dict:
    """Check system health asynchronously."""
    loop = asyncio.get_event_loop()
    try:
        return await loop.run_in_executor(_executor, _check_llm_health)
    except Exception as e:
        return {"llm_available": False, "error": str(e)}
