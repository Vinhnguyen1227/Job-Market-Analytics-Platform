"""
Intent Router — Classifies user messages into Phase 5 task types.

Uses keyword matching for Vietnamese patterns with LLM fallback.
Maps user intent to: assess, match, interview, upload, or general.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class IntentResult:
    """Result of intent classification.

    Attributes:
        intent: Detected intent type.
        confidence: Confidence score (0-1).
        task_params: Extra parameters extracted from the message.
    """
    intent: str = "general"
    confidence: float = 0.0
    task_params: dict = None

    def __post_init__(self):
        if self.task_params is None:
            self.task_params = {}


# ── Intent Patterns ──────────────────────────────────────

INTENT_PATTERNS: dict[str, list[re.Pattern]] = {
    "assess": [
        re.compile(r"đánh\s*giá\s*(cv|hồ\s*sơ|resume)", re.I),
        re.compile(r"nhận\s*xét\s*(cv|hồ\s*sơ|resume)", re.I),
        re.compile(r"feedback\s*(cv|hồ\s*sơ|resume)?", re.I),
        re.compile(r"chấm\s*điểm\s*(cv|hồ\s*sơ|resume)", re.I),
        re.compile(r"review\s*(cv|resume|my)", re.I),
        re.compile(r"(cv|hồ\s*sơ|resume)\s*(của\s*tôi|của\s*em|tôi)", re.I),
        re.compile(r"(cải\s*thiện|nâng\s*cấp)\s*(cv|hồ\s*sơ)", re.I),
        re.compile(r"(điểm\s*mạnh|điểm\s*yếu)\s*(cv|hồ\s*sơ)?", re.I),
        re.compile(r"viết\s*lại\s*(mục|phần|bullet)", re.I),
        re.compile(r"(sửa|fix)\s*(cv|hồ\s*sơ|resume)", re.I),
    ],
    "match": [
        re.compile(r"(tìm|gợi\s*ý)\s*(việc|job|công\s*việc)", re.I),
        re.compile(r"(việc|job|công\s*việc)\s*(phù\s*hợp|match)", re.I),
        re.compile(r"(matching|so\s*sánh)\s*(jd|job|cv)", re.I),
        re.compile(r"(ứng\s*tuyển|apply)\s*(vào|cho)", re.I),
        re.compile(r"(phù\s*hợp|fit)\s*(với|cho|vị\s*trí)", re.I),
        re.compile(r"jd\s*(nào|phù\s*hợp)", re.I),
        re.compile(r"(có\s*phù\s*hợp|tôi\s*có\s*nên)", re.I),
    ],
    "interview": [
        re.compile(r"(câu\s*hỏi|question)\s*(phỏng\s*vấn|interview)", re.I),
        re.compile(r"(phỏng\s*vấn|interview)\s*(cho|về|tại)", re.I),
        re.compile(r"(chuẩn\s*bị|prep)\s*(phỏng\s*vấn|interview)", re.I),
        re.compile(r"(lộ\s*trình|roadmap)\s*(học|study|nghề)", re.I),
        re.compile(r"(study|learning)\s*(plan|roadmap|path)", re.I),
        re.compile(r"(kỹ\s*năng|skill)\s*(cần\s*học|gap|thiếu)", re.I),
        re.compile(r"tạo\s*câu\s*hỏi", re.I),
        re.compile(r"(hỏi\s*gì|hỏi\s*những|interview\s*questions)", re.I),
    ],
}

# Keywords that hint the user wants to work with their resume
RESUME_CONTEXT_PATTERNS = [
    re.compile(r"(cv|hồ\s*sơ|resume)\s*(của\s*tôi|tôi|của\s*em)", re.I),
    re.compile(r"(tôi|em)\s*(vừa|đã|mới)\s*(upload|tải|gửi)", re.I),
]

# Target role extraction for interview/roadmap
TARGET_ROLE_PATTERN = re.compile(
    r"(?:cho|vị\s*trí|role|position|làm)\s+(.+?)(?:\s*\?|$)", re.I
)


class IntentRouter:
    """Classify user messages into Phase 5 task types.

    Uses a two-pass approach:
    1. Fast keyword matching against Vietnamese patterns
    2. Fallback to general if no match found

    For ambiguous messages, the router defaults to 'general'
    which uses direct LLM chat mode.
    """

    def classify(self, message: str, has_resume: bool = False) -> IntentResult:
        """Classify a user message into a task intent.

        Args:
            message: The user's text message.
            has_resume: Whether a resume has been uploaded in the session.

        Returns:
            IntentResult with detected intent and parameters.
        """
        message = message.strip()
        if not message:
            return IntentResult(intent="general", confidence=0.0)

        # Pass 1: Keyword pattern matching
        best_intent = None
        best_confidence = 0.0
        match_count = {}

        for intent, patterns in INTENT_PATTERNS.items():
            hits = sum(1 for p in patterns if p.search(message))
            if hits > 0:
                # Confidence scales with number of matching patterns
                confidence = min(0.5 + hits * 0.15, 0.95)
                match_count[intent] = hits
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_intent = intent

        # If a resume is uploaded and user asks about it with no clear intent,
        # default to assess
        if not best_intent and has_resume:
            for p in RESUME_CONTEXT_PATTERNS:
                if p.search(message):
                    best_intent = "assess"
                    best_confidence = 0.6
                    break

        if not best_intent:
            return IntentResult(intent="general", confidence=0.3)

        # Extract task-specific parameters
        params = {}

        # For interview: try to extract target role
        if best_intent == "interview":
            role_match = TARGET_ROLE_PATTERN.search(message)
            if role_match:
                params["target_role"] = role_match.group(1).strip()
            # Check if roadmap is requested
            if re.search(r"(lộ\s*trình|roadmap|study|plan|học)", message, re.I):
                params["generate_roadmap"] = True

        return IntentResult(
            intent=best_intent,
            confidence=best_confidence,
            task_params=params,
        )
