"""
Response Formatter — Converts Phase 5 structured JSON into conversational Vietnamese.

Transforms FeedbackResult, MatchResult, and InterviewResult dataclass outputs
into human-readable markdown for display in the chatbot UI.
"""

from __future__ import annotations

import json
from typing import Optional


class ResponseFormatter:
    """Format Phase 5 task results as conversational Vietnamese markdown.

    Each task type has a dedicated formatter that produces rich,
    readable output while preserving the structured data as metadata.
    """

    def format(self, task_type: str, result: dict, metadata: dict = None) -> str:
        """Format a task result into conversational text.

        Args:
            task_type: One of 'assess', 'match', 'interview'.
            result: The task result dict (from TaskResponse.to_dict()['result']).
            metadata: Optional processing metadata.

        Returns:
            Formatted markdown string for chat display.
        """
        formatters = {
            "assess": self._format_assess,
            "match": self._format_match,
            "interview": self._format_interview,
        }

        formatter = formatters.get(task_type)
        if not formatter:
            return self._format_generic(result)

        try:
            return formatter(result, metadata or {})
        except Exception:
            return self._format_generic(result)

    def format_upload_success(self, resume_name: str, quality_score: float,
                               is_valid: bool, resume_id: str) -> str:
        """Format a successful resume upload response."""
        status = "✅ Hợp lệ" if is_valid else "⚠️ Có lỗi cần kiểm tra"
        score_emoji = "🌟" if quality_score >= 80 else "👍" if quality_score >= 60 else "📝"

        return (
            f"📄 **Đã xử lý thành công CV: {resume_name}**\n\n"
            f"- Trạng thái: {status}\n"
            f"- {score_emoji} Điểm chất lượng: **{quality_score}/100**\n"
            f"- ID: `{resume_id}`\n\n"
            f"Bạn có thể hỏi tôi:\n"
            f'- *"Đánh giá CV của tôi"* — Nhận xét chi tiết\n'
            f'- *"Tạo câu hỏi phỏng vấn"* — Chuẩn bị phỏng vấn\n'
            f'- *"Tìm việc phù hợp"* — So khớp JD\n'
        )

    def format_error(self, error: str) -> str:
        """Format an error response."""
        return (
            f"❌ **Xin lỗi, đã xảy ra lỗi:**\n\n"
            f"> {error}\n\n"
            f"Bạn có thể thử lại hoặc hỏi câu khác."
        )

    # ── Task-specific formatters ──────────────────────────

    def _format_assess(self, result: dict, metadata: dict) -> str:
        """Format FeedbackResult into conversational assessment."""
        grade = result.get("letter_grade", "?")
        overall = result.get("overall_assessment", "")
        strengths = result.get("strengths", [])
        weaknesses = result.get("weaknesses", [])
        section_feedback = result.get("section_feedback", [])
        rewrites = result.get("highlight_rewrites", [])

        grade_emoji = {
            "A": "🏆", "B": "👍", "C": "📝", "D": "⚠️", "F": "❌"
        }.get(grade, "📊")

        lines = [
            f"## {grade_emoji} Đánh giá CV — Hạng **{grade}**\n",
            f"{overall}\n",
        ]

        # Strengths
        if strengths:
            lines.append("### 💪 Điểm mạnh")
            for s in strengths:
                lines.append(f"- {s}")
            lines.append("")

        # Weaknesses
        if weaknesses:
            lines.append("### 📌 Cần cải thiện")
            for w in weaknesses:
                lines.append(f"- {w}")
            lines.append("")

        # Section scores
        if section_feedback:
            lines.append("### 📊 Điểm theo mục")
            for sf in section_feedback:
                score = sf.get("score", 0)
                bar = self._score_bar(score)
                lines.append(f"- **{sf.get('section', '?')}**: {bar} {score}/100")
                if sf.get("assessment"):
                    lines.append(f"  _{sf['assessment']}_")
                for sug in sf.get("suggestions", []):
                    lines.append(f"  - 💡 {sug}")
            lines.append("")

        # Highlight rewrites
        if rewrites:
            lines.append("### ✍️ Viết lại mô tả mơ hồ")
            for rw in rewrites:
                lines.append(f"**Gốc:** ~~{rw.get('original', '')}~~")
                lines.append(f"**Sửa:** ✅ {rw.get('rewritten', '')}")
                if rw.get("explanation"):
                    lines.append(f"_{rw['explanation']}_")
                lines.append("")

        # Processing info
        name = metadata.get("resume_name", "")
        latency = metadata.get("pipeline_time_s", "?")
        if name:
            lines.append(f"\n---\n_CV: {name} | Thời gian xử lý: {latency}s_")

        return "\n".join(lines)

    def _format_match(self, result: dict, metadata: dict) -> str:
        """Format MatchResult into job matching response."""
        summary = result.get("candidate_summary", "")
        skills = result.get("candidate_skills", [])
        jobs = result.get("jobs", [])

        lines = [
            "## 🎯 Kết quả so khớp việc làm\n",
            f"{summary}\n",
        ]

        if skills:
            lines.append(f"**Kỹ năng chính:** {', '.join(skills)}\n")

        if jobs:
            lines.append(f"### Tìm thấy {len(jobs)} vị trí phù hợp:\n")
            for i, job in enumerate(jobs, 1):
                fit = job.get("fit_score", 0)
                fit_emoji = "🟢" if fit >= 80 else "🟡" if fit >= 60 else "🔴"
                lines.append(
                    f"**{i}. {job.get('title', '?')}** — {job.get('company', '?')}"
                )
                lines.append(f"   {fit_emoji} Độ phù hợp: **{fit}%**")

                matching = job.get("matching_skills", [])
                missing = job.get("missing_skills", [])
                if matching:
                    lines.append(f"   ✅ Kỹ năng khớp: {', '.join(matching)}")
                if missing:
                    lines.append(f"   ❌ Thiếu: {', '.join(missing)}")
                if job.get("recommendation"):
                    lines.append(f"   💡 {job['recommendation']}")
                lines.append("")
        else:
            lines.append("_Chưa tìm thấy vị trí phù hợp trong cơ sở dữ liệu._\n")

        return "\n".join(lines)

    def _format_interview(self, result: dict, metadata: dict) -> str:
        """Format InterviewResult into interview prep response."""
        questions = result.get("questions", [])
        roadmap = result.get("roadmap")
        summary = result.get("candidate_summary", "")

        lines = [
            "## 🎤 Câu hỏi phỏng vấn\n",
        ]

        if summary:
            lines.append(f"_{summary}_\n")

        if questions:
            # Group by category
            technical = [q for q in questions if q.get("category") == "technical"]
            behavioral = [q for q in questions if q.get("category") == "behavioral"]

            if technical:
                lines.append("### 💻 Câu hỏi kỹ thuật")
                for i, q in enumerate(technical, 1):
                    diff_icon = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}.get(
                        q.get("difficulty", "medium"), "🟡"
                    )
                    lines.append(f"\n**{i}. {q.get('question', '')}** {diff_icon}")
                    if q.get("topic"):
                        lines.append(f"   _Chủ đề: {q['topic']}_")
                    hints = q.get("expected_hints", [])
                    if hints:
                        lines.append("   **Gợi ý trả lời:**")
                        for h in hints:
                            lines.append(f"   - {h}")
                lines.append("")

            if behavioral:
                lines.append("### 🤝 Câu hỏi hành vi")
                for i, q in enumerate(behavioral, 1):
                    lines.append(f"\n**{i}. {q.get('question', '')}**")
                    hints = q.get("expected_hints", [])
                    if hints:
                        lines.append("   **Gợi ý:**")
                        for h in hints:
                            lines.append(f"   - {h}")
                lines.append("")

        # Study roadmap
        if roadmap:
            lines.append(f"### 📚 Lộ trình học tập — {roadmap.get('target_role', '?')}")
            fit = roadmap.get("current_fit", 0)
            lines.append(f"\nĐộ phù hợp hiện tại: **{fit}%**")
            lines.append(f"Thời gian ước tính: **{roadmap.get('total_estimated_duration', '?')}**\n")

            for topic in roadmap.get("topics", []):
                priority_icon = {
                    "high": "🔴", "medium": "🟡", "low": "🟢"
                }.get(topic.get("priority", "medium"), "🟡")
                lines.append(
                    f"- {priority_icon} **{topic.get('topic', '?')}** "
                    f"({topic.get('current_level', '?')} → {topic.get('target_level', '?')})"
                )
                if topic.get("estimated_duration"):
                    lines.append(f"  ⏱ {topic['estimated_duration']}")
                for res in topic.get("resources", []):
                    lines.append(f"  📖 {res}")
            lines.append("")

        return "\n".join(lines)

    def _format_generic(self, result: dict) -> str:
        """Fallback formatter for unknown result types."""
        if isinstance(result, str):
            return result
        return f"```json\n{json.dumps(result, ensure_ascii=False, indent=2)}\n```"

    @staticmethod
    def _score_bar(score: float, width: int = 10) -> str:
        """Generate a visual score bar."""
        filled = round(score / 100 * width)
        return "█" * filled + "░" * (width - filled)
