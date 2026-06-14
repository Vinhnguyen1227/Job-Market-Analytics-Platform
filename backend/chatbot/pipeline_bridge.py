"""Phase 3 + Phase 4 bridge for the Celery worker.

Goal: take a raw CV file (PDF/DOCX/image), end with a stored
canonical resume in Qdrant + a quality score.

Phase 2 (layout analysis) does NOT exist in this repo. We bypass
`SemanticExtractionPipeline.process()` (which demands Phase 2
outputs) and call its building blocks directly via the
`chunk_from_raw_sections` shortcut on `SemanticChunker`.

We use heuristic section splitting from raw text to feed the
chunker the {section_label -> raw_text} dict it expects.
"""

from __future__ import annotations

import importlib.util
import logging
import os
import pathlib
import re
import sys
import time
from typing import Any

logger = logging.getLogger(__name__)

# ── Module loading from folders with spaces ───────────────────────────

_THIS = os.path.abspath(__file__)
_CHATBOT_BACKEND = os.path.dirname(_THIS)
_REPO_ROOT = os.path.dirname(os.path.dirname(_CHATBOT_BACKEND))

# In Docker the chatbot phases are copied to /chatbot (see Dockerfile);
# in dev they live at <repo>/chatbot.
_CHATBOT_ROOT_CANDIDATES = [
    os.environ.get("CHATBOT_PHASES_DIR"),
    "/chatbot",
    os.path.join(_REPO_ROOT, "chatbot"),
]
CHATBOT_ROOT = next(p for p in _CHATBOT_ROOT_CANDIDATES if p and os.path.isdir(p))

P3_DIR = os.path.join(CHATBOT_ROOT, "phase 3-semantic chunking")
P4_DIR = os.path.join(CHATBOT_ROOT, "phase 4-validation and storage")

# Phase 3/4 use bare `from schema import ...` style. Add their dirs to sys.path.
for d in (P3_DIR, P4_DIR):
    if d not in sys.path:
        sys.path.insert(0, d)


def _load(modname: str, path: str):
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[modname] = mod
    spec.loader.exec_module(mod)
    return mod


P3 = _load("phase3_pipeline", os.path.join(P3_DIR, "pipeline.py"))
P4 = _load("phase4_pipeline", os.path.join(P4_DIR, "pipeline.py"))


# ── Singletons (heavy: PhoBERT NER, BGE-M3 embedder) ──────────────────

_pipeline3 = None
_pipeline4 = None
_warmed_up = False


def _get_pipelines():
    """Lazy-init the heavy Phase 3 + 4 pipelines once per worker process."""
    global _pipeline3, _pipeline4
    if _pipeline3 is None:
        # Skip LLM normalization (heavy 7B call) - quality_score still
        # works without it. NER stays on for Vietnamese entity extraction.
        _pipeline3 = P3.SemanticExtractionPipeline(
            use_ner=os.environ.get("CHATBOT_USE_NER", "0") == "1",
            use_llm=os.environ.get("CHATBOT_USE_LLM", "0") == "1",
            ner_device=os.environ.get("CHATBOT_NER_DEVICE", "cpu"),
        )
    if _pipeline4 is None:
        _pipeline4 = P4.ValidationStoragePipeline(
            use_embeddings=True,
            use_storage=True,
            embedding_device=os.environ.get("CHATBOT_EMBED_DEVICE", "cpu"),
            db_path=os.environ.get("QDRANT_PATH", "data/qdrant_db"),
        )
    return _pipeline3, _pipeline4


def warmup():
    """Pre-load models and run dummy inference to trigger JIT compilation.

    Call this from the Celery worker_init signal so the first real
    PDF upload doesn't pay the ~50s cold-start penalty.
    """
    global _warmed_up
    if _warmed_up:
        return

    t0 = time.time()
    logger.info("pipeline_bridge: warming up PhoBERT NER + BGE-M3 models...")

    pipeline3, pipeline4 = _get_pipelines()

    # Warm NER model with a short dummy text
    if pipeline3.use_ner and pipeline3.ner_extractor:
        try:
            pipeline3.ner_extractor.extract_from_text("Nguyễn Văn A làm việc tại FPT Software")
            logger.info("  NER model warmed up")
        except Exception as e:
            logger.warning(f"  NER warmup failed (non-fatal): {e}")

    # Warm embedding model with a short dummy text
    if pipeline4.use_embeddings and pipeline4.embedder:
        try:
            pipeline4.embedder.embed_query("warmup")
            logger.info("  Embedding model warmed up")
        except Exception as e:
            logger.warning(f"  Embedding warmup failed (non-fatal): {e}")

    _warmed_up = True
    logger.info(f"pipeline_bridge: warmup done ({time.time() - t0:.1f}s)")



# ── File parsing ──────────────────────────────────────────────────────

def parse_file(file_path: str) -> str:
    ext = file_path.lower().rsplit(".", 1)[-1]
    if ext == "pdf":
        import fitz
        doc = fitz.open(file_path)
        text = "\n".join(page.get_text() for page in doc)
        if text.strip():
            return text
        # Empty -> OCR fallback
    if ext in {"docx", "doc"}:
        import docx
        doc = docx.Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)

    import pytesseract
    from PIL import Image
    if ext == "pdf":
        # OCR each page rendered as image
        import fitz
        doc = fitz.open(file_path)
        out = []
        for page in doc:
            pix = page.get_pixmap(dpi=200)
            from io import BytesIO
            img = Image.open(BytesIO(pix.tobytes("png")))
            out.append(pytesseract.image_to_string(img, lang="vie+eng"))
        return "\n".join(out)
    return pytesseract.image_to_string(Image.open(file_path), lang="vie+eng")


# ── Section heuristics (replace Phase 2 layout analysis) ───────────────

_SECTION_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("personal_info", re.compile(r"^\s*(thông tin (cá nhân|liên hệ)|personal info|contact)\s*$", re.I)),
    ("objective", re.compile(r"^\s*(mục tiêu|tóm tắt|career objective|summary|profile)\s*$", re.I)),
    ("experience", re.compile(r"^\s*(kinh nghiệm( làm việc)?|work experience|experience|employment history)\s*$", re.I)),
    ("education", re.compile(r"^\s*(học vấn|trình độ học vấn|education|academic background)\s*$", re.I)),
    ("projects", re.compile(r"^\s*(dự án|projects?|portfolio)\s*$", re.I)),
    ("skills", re.compile(r"^\s*(kỹ năng( chuyên môn)?|skills?|technical skills?)\s*$", re.I)),
    ("certifications", re.compile(r"^\s*(chứng chỉ|certifications?)\s*$", re.I)),
    ("courses", re.compile(r"^\s*(khoá học|khóa học|courses?|training)\s*$", re.I)),
    ("awards", re.compile(r"^\s*(giải thưởng|thành tích|awards?|achievements?)\s*$", re.I)),
    ("languages", re.compile(r"^\s*(ngoại ngữ|languages?)\s*$", re.I)),
    ("hobbies", re.compile(r"^\s*(sở thích|hobbies|interests?)\s*$", re.I)),
]


def _split_into_sections(text: str) -> dict[str, str]:
    """Split raw CV text into {section_label: raw_text}.

    Lines that match a section heading start a new bucket; everything
    before the first heading goes into `personal_info`.
    """
    sections: dict[str, list[str]] = {"personal_info": []}
    current = "personal_info"

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip().rstrip(":").strip()
        matched_label: str | None = None
        for label, pat in _SECTION_PATTERNS:
            if pat.match(stripped):
                matched_label = label
                break

        if matched_label:
            current = matched_label
            sections.setdefault(current, [])
            # Don't keep the heading line itself.
            continue

        sections.setdefault(current, []).append(line)

    return {label: "\n".join(lines).strip() for label, lines in sections.items() if any(l.strip() for l in lines)}


# ── Main entry ────────────────────────────────────────────────────────

def run_phase34(file_path: str) -> dict[str, Any]:
    """Parse -> chunk -> extract -> validate -> embed -> store.

    Returns the dict the chat envelope `result` field expects (see
    slm_orchestrator_api_pipeline_guide.md §3.5).
    """
    t_parse = time.time()
    text = parse_file(file_path)
    sections = _split_into_sections(text)
    if not sections:
        raise ValueError("Không trích xuất được nội dung từ file CV.")

    pipeline3, pipeline4 = _get_pipelines()

    # ── Phase 3: chunk + regex + NER + assemble ──
    t3 = time.time()
    chunks = pipeline3.chunker.chunk_from_raw_sections(sections)

    regex_entities = pipeline3.regex_extractor.extract_from_chunks(chunks)
    ner_entities: dict = {}
    if pipeline3.use_ner and pipeline3.ner_extractor:
        try:
            ner_entities = pipeline3.ner_extractor.extract_from_chunks(chunks)
        except Exception as e:
            logger.warning(f"NER skipped: {e}")

    all_entities = []
    for chunk in chunks:
        merged = pipeline3._merge_entities(
            regex_entities.get(chunk.chunk_id, []),
            ner_entities.get(chunk.chunk_id, []),
        )
        chunk.entities = merged
        all_entities.extend(merged)

    canonical = pipeline3._assemble_from_chunks(chunks, None)
    canonical.raw_entities = all_entities
    canonical.chunks = chunks
    canonical.metadata.update({
        "source": "chatbot_bridge",
        "source_path": file_path,
        "source_format": pathlib.Path(file_path).suffix.lstrip(".").lower(),
        "num_chunks": len(chunks),
        "num_entities": len(all_entities),
    })
    phase3_time_s = round(time.time() - t3, 2)

    # ── Phase 4: validate + embed + store ──
    t4 = time.time()
    validated = pipeline4.validate_and_store(canonical)
    phase4_time_s = round(time.time() - t4, 2)

    point_id = ""
    if validated.embedding_ids:
        point_id = str(validated.embedding_ids[0])
    elif validated.metadata.get("point_id"):
        point_id = str(validated.metadata["point_id"])

    quality_overall = 0
    try:
        quality_overall = int(getattr(validated.quality_score, "overall", 0))
    except Exception:
        quality_overall = 0

    return {
        "resume_id": point_id,
        "resume_dict": canonical.to_dict() if hasattr(canonical, "to_dict") else canonical.model_dump(),
        "resume_name": pathlib.Path(file_path).name,
        "quality_score": quality_overall,
        "num_experience": len(getattr(canonical, "experience", []) or []),
        "num_skills": len(getattr(canonical, "skills", []) or []),
        "phase3_time_s": phase3_time_s,
        "phase4_time_s": phase4_time_s,
        "parse_time_s": round(t3 - t_parse, 2),
    }
