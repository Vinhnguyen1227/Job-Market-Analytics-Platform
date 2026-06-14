"""Tool dispatcher.

Reads the validated `ToolCallResult` from intent_router / slash_commands
and runs the matching tool. Picks the right adapter (B or C) and the
right system prompt for each branch.
"""

from __future__ import annotations

import json
import logging
import time

from adapter_manager import adapter_mgr
from adapter_prompts import (
    HR_COACH_SYSTEM_PROMPT,
    STRUCTURED_GEN_INTERVIEW_PROMPT,
    STRUCTURED_GEN_ROADMAP_PROMPT,
)
from data_clients import es_client, qdrant_client
from response_formatter import format_job_cards

logger = logging.getLogger(__name__)


NEEDS_RESUME_MD = (
    "🧐 Mình cần xem CV của bạn trước khi đánh giá. "
    "Bấm 📎 ở khung chat để tải CV (PDF/DOCX) lên nhé."
)


def _resume_dict(session_data: dict | None) -> dict | None:
    if not session_data:
        return None
    rd = session_data.get("resume_dict")
    if not rd or rd == {}:
        return None
    return rd


async def dispatch(tc, session_id: str, session_data: dict | None, user_message: str, history: list[dict] | None = None, conversation_summary: str | None = None) -> dict:
    """Execute a tool call. Always returns the chat envelope dict
    `{response, task_type, metadata}` consumed by `format_chat_response`.
    """
    tool = tc.tool
    params = tc.params or {}
    started = time.time()

    if tool == "search_jobs":
        hits = await es_client.search_jobs(params)
        md = format_job_cards(hits)
        return {
            "response": md,
            "task_type": tool,
            "metadata": {
                "tool": tool,
                "params": params,
                "hits": len(hits),
                "latency_ms": int((time.time() - started) * 1000),
            },
        }

    resume_id = session_data.get("resume_id") if session_data else None
    resume_dict = _resume_dict(session_data)

    if tool in {"assess_resume", "match_jobs", "interview_prep"} and not resume_id:
        return {
            "response": NEEDS_RESUME_MD,
            "task_type": "needs_resume",
            "metadata": {"tool": tool, "reason": "no_resume_in_session"},
        }

    if tool == "assess_resume":
        cv_json_str = json.dumps(resume_dict or {}, ensure_ascii=False)
        user_prompt = f"CV (JSON):\n{cv_json_str}\n\nYêu cầu của ứng viên: {user_message}"
        md = await adapter_mgr.generate(
            "hr_coach", system=HR_COACH_SYSTEM_PROMPT, user=user_prompt, history=history, conversation_summary=conversation_summary
        )
        return {
            "response": md,
            "task_type": tool,
            "metadata": {"tool": tool, "resume_id": resume_id,
                         "latency_ms": int((time.time() - started) * 1000)},
        }

    if tool == "match_jobs":
        jd_text = params.get("jd_text") or ""
        if not jd_text:
            return {
                "response": "Bạn vui lòng dán mô tả công việc (JD) để mình so khớp với CV nhé.",
                "task_type": "error",
                "metadata": {"tool": tool, "reason": "missing_jd_text"},
            }
        gaps = qdrant_client.compare_skills(resume_id, jd_text)
        user_prompt = (
            f"Phân tích độ phù hợp giữa CV và JD sau.\n"
            f"Skill gap analysis (JSON): {json.dumps(gaps, ensure_ascii=False)}\n"
            f"Câu hỏi của ứng viên: {user_message}"
        )
        md = await adapter_mgr.generate(
            "hr_coach", system=HR_COACH_SYSTEM_PROMPT, user=user_prompt, history=history, conversation_summary=conversation_summary
        )
        return {
            "response": md,
            "task_type": tool,
            "metadata": {
                "tool": tool,
                "resume_id": resume_id,
                "missing_skills": gaps.get("missing", [])[:10],
                "latency_ms": int((time.time() - started) * 1000),
            },
        }

    if tool == "interview_prep":
        target = params.get("target_role") or ""
        is_roadmap = bool(params.get("generate_roadmap"))
        cv_json_str = json.dumps(resume_dict or {}, ensure_ascii=False)

        if is_roadmap:
            system_prompt = STRUCTURED_GEN_ROADMAP_PROMPT
            user_prompt = (
                f"Vị trí mục tiêu: {target or '(chưa rõ)'}\n"
                f"CV hiện tại (JSON): {cv_json_str}\n"
                "Hãy xuất lộ trình học dạng Markdown table có timeline, tài liệu, mức ưu tiên."
            )
        else:
            system_prompt = STRUCTURED_GEN_INTERVIEW_PROMPT
            user_prompt = (
                f"Vị trí ứng tuyển: {target or '(chưa rõ)'}\n"
                f"CV ứng viên (JSON): {cv_json_str}\n"
                "Hãy tạo 3 câu hỏi phỏng vấn kỹ thuật dựa trên dự án thực tế kèm rubric 5 sao."
            )

        md = await adapter_mgr.generate(
            "structured_gen", system=system_prompt, user=user_prompt, history=history, conversation_summary=conversation_summary
        )
        return {
            "response": md,
            "task_type": tool,
            "metadata": {
                "tool": tool,
                "target_role": target,
                "generate_roadmap": is_roadmap,
                "latency_ms": int((time.time() - started) * 1000),
            },
        }

    if tool == "general_response":
        md = await adapter_mgr.generate(
            "hr_coach", system=HR_COACH_SYSTEM_PROMPT, user=user_message, history=history, conversation_summary=conversation_summary
        )
        return {
            "response": md,
            "task_type": tool,
            "metadata": {"tool": tool,
                         "latency_ms": int((time.time() - started) * 1000)},
        }

    logger.warning(f"Unknown tool: {tool}")
    return {
        "response": "Xin lỗi, mình chưa hiểu yêu cầu này. Bạn nói rõ hơn giúp mình nhé.",
        "task_type": "error",
        "metadata": {"tool": tool, "reason": "unknown_tool"},
    }
