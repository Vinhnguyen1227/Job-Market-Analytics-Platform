"""Ollama adapter manager.

Wraps the async Ollama client and routes generation calls to the
correct Ollama model for each LoRA adapter (tool_call, hr_coach,
structured_gen). `format="json"` is a top-level chat arg, not an
option, so we extract it from GEN_PARAMS before sending.
"""

from __future__ import annotations

import ollama

from adapter_config import (
    GEN_PARAMS,
    MODEL_HR_COACH,
    MODEL_STRUCTURED_GEN,
    MODEL_TOOL_CALL,
    OLLAMA_HOST,
)
from adapter_prompts import CONVERSATION_SUMMARY_TEMPLATE


class AdapterManager:
    def __init__(self):
        self.client = ollama.AsyncClient(host=OLLAMA_HOST)

    async def generate(
        self,
        adapter: str,
        system: str,
        user: str,
        history: list[dict] | None = None,
        conversation_summary: str | None = None,
        **overrides,
    ) -> str:
        model_map = {
            "tool_call": MODEL_TOOL_CALL,
            "hr_coach": MODEL_HR_COACH,
            "structured_gen": MODEL_STRUCTURED_GEN,
        }
        model = model_map[adapter]
        params = {**GEN_PARAMS[adapter], **overrides}
        fmt = params.pop("format", None)
        
        messages = [{"role": "system", "content": system}]
        if conversation_summary:
            messages.append({"role": "system", "content": CONVERSATION_SUMMARY_TEMPLATE.format(summary=conversation_summary)})
            
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user})
        
        kwargs = {"model": model, "messages": messages, "options": params}
        if fmt:
            kwargs["format"] = fmt
        out = await self.client.chat(**kwargs)
        return out["message"]["content"]

    async def health(self) -> bool:
        try:
            await self.client.list()
            return True
        except Exception:
            return False


adapter_mgr = AdapterManager()
