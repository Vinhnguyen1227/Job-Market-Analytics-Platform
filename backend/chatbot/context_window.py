"""Context Window Manager.
Manages token budget for SLM chatbot using extractive summarization.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

HISTORY_TOKEN_BUDGET = 2000
SUMMARY_TOKEN_BUDGET = 500

class ContextWindowManager:
    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Word-based token estimate (~1.3 tokens per word for VN)."""
        if not text:
            return 0
        return int(len(text.split()) * 1.3)

    @staticmethod
    def build_context(history: list[dict], budget: int = HISTORY_TOKEN_BUDGET) -> tuple[list[dict], str | None]:
        """Trim history to fit budget and extract summary of dropped messages.
        
        Returns:
            (trimmed_history, extractive_summary_or_none)
        """
        if not history:
            return [], None
            
        total_tokens = 0
        token_counts = []
        for msg in history:
            tokens = ContextWindowManager.estimate_tokens(msg.get("content", ""))
            token_counts.append(tokens)
            total_tokens += tokens
            
        if total_tokens <= budget:
            return history, None
            
        # Needs trimming. Keep recent messages until budget hit
        keep_idx = len(history) - 1
        current_budget = 0
        
        while keep_idx >= 0:
            if current_budget + token_counts[keep_idx] > budget:
                break
            current_budget += token_counts[keep_idx]
            keep_idx -= 1
            
        keep_idx += 1 # First message to keep
        
        # We always want at least 1 message if possible
        if keep_idx >= len(history):
            keep_idx = len(history) - 1
            
        dropped = history[:keep_idx]
        kept = history[keep_idx:]
        
        summary = ContextWindowManager.build_summary(dropped)
        return kept, summary
        
    @staticmethod
    def build_summary(dropped_messages: list[dict], budget: int = SUMMARY_TOKEN_BUDGET) -> str | None:
        """Extractive summary of dropped messages without LLM call."""
        if not dropped_messages:
            return None
            
        summary_lines = []
        
        # Keep first user intent if dropped
        first_user = next((m for m in dropped_messages if m["role"] == "user"), None)
        if first_user:
            # truncate long content
            content = first_user['content']
            if len(content) > 100: content = content[:100] + "..."
            summary_lines.append(f"- Yêu cầu ban đầu: {content}")
            
        # Keep last dropped message to maintain flow
        last_dropped = dropped_messages[-1]
        if last_dropped != first_user:
             role_name = "Người dùng" if last_dropped["role"] == "user" else "Hệ thống"
             content = last_dropped['content']
             if len(content) > 100: content = content[:100] + "..."
             summary_lines.append(f"- Trước đó ({role_name}): {content}")
             
        # Extract CV/Job mentions
        keywords = ["cv", "resume", "kinh nghiệm", "kỹ năng", "mức lương", "lương", "apply", "phỏng vấn", "job", "việc làm"]
        for msg in dropped_messages:
            if msg in (first_user, last_dropped):
                continue
            content = msg.get("content", "")
            lower_content = content.lower()
            if any(k in lower_content for k in keywords):
                role_name = "Người dùng" if msg["role"] == "user" else "Hệ thống"
                if len(content) > 100: content = content[:100] + "..."
                summary_lines.append(f"- Thông tin liên quan ({role_name}): {content}")
                
        if not summary_lines:
            return None
            
        summary = "\n".join(summary_lines)
        
        # Ensure it fits budget
        while ContextWindowManager.estimate_tokens(summary) > budget and len(summary_lines) > 2:
            summary_lines.pop(-2) # Remove middle lines first
            summary = "\n".join(summary_lines)
            
        return summary
