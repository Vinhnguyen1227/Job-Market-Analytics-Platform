"""Intent router (Adapter A).

Calls the tool-call adapter via Ollama with `format=json`, validates
the result, and falls back to `general_response` if it can't be parsed.

History is intentionally NOT passed to Adapter A - the training set
used single-turn prompts (see slm_orchestrator_api_pipeline_guide.md
§13 Q3).
"""

from __future__ import annotations

import json
import logging

from pydantic import ValidationError

from adapter_manager import adapter_mgr
from adapter_prompts import TOOL_CALL_SYSTEM_PROMPT
from tool_schemas import ToolCallResult

logger = logging.getLogger(__name__)


def _safe_parse(raw: str) -> dict | None:
    if not raw:
        return None
    raw = raw.strip()
    # Sometimes the model wraps JSON in ```json ... ``` despite format=json.
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.lower().startswith("json"):
            raw = raw[4:].lstrip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


async def _try_once(user_msg: str, temperature: float | None = None) -> ToolCallResult | None:
    overrides = {"temperature": temperature} if temperature is not None else {}
    raw = await adapter_mgr.generate(
        "tool_call", system=TOOL_CALL_SYSTEM_PROMPT, user=user_msg, **overrides,
    )
    data = _safe_parse(raw)
    if data is None:
        return None
    try:
        tc = ToolCallResult(**data)
        # Soft-validate params for known tools; ignore failures so an
        # invalid location etc. still routes the user to a useful tool.
        try:
            tc.validated_params()
        except ValidationError as e:
            logger.info(f"params soft-validation failed: {e}")
        return tc
    except ValidationError as e:
        logger.warning(f"router envelope invalid: {e}")
        return None


async def route(user_msg: str, history: list[dict] | None = None) -> ToolCallResult:
    """Return a ToolCallResult, never raise.

    Strategy:
      1. Adapter A, default temperature -> validate.
      2. If invalid, retry once at temp=0.05 (almost greedy).
      3. Fallback to general_response so the user always gets a reply.
    """
    tc = await _try_once(user_msg)
    if tc is not None:
        return tc

    logger.warning("intent_router first pass invalid; retrying")
    tc = await _try_once(user_msg, temperature=0.05)
    if tc is not None:
        return tc

    logger.warning("intent_router gave up; falling back to general_response")
    return ToolCallResult(tool="general_response", params={})
