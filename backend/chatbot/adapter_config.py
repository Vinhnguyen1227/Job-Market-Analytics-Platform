"""Adapter / Ollama runtime configuration.

Locked decision: Ollama runs on the HOST (not in compose).
Containers reach it via host.docker.internal. Dev box without
trained adapters falls back to vanilla qwen2.5:1.5b.
"""

import os

MODEL_TOOL_CALL = os.environ.get("MODEL_TOOL_CALL", "qwen2.5:1.5b")
MODEL_HR_COACH = os.environ.get("MODEL_HR_COACH", "qwen2.5:1.5b")
MODEL_STRUCTURED_GEN = os.environ.get("MODEL_STRUCTURED_GEN", "qwen2.5:1.5b")
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://host.docker.internal:11434")

GEN_PARAMS = {
    "tool_call": {"temperature": 0.1, "top_p": 0.9, "num_predict": 256, "format": "json"},
    "hr_coach": {"temperature": 0.5, "top_p": 0.9, "num_predict": 1024},
    "structured_gen": {"temperature": 0.3, "top_p": 0.9, "num_predict": 2048},
}
