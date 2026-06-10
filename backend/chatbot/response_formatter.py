"""Response formatters.

`format_chat_response` is the canonical FastAPI -> BFF envelope.
`format_job_cards` renders Elasticsearch `raw_data` hits (Vietnamese
scraper schema) into Markdown the frontend can show.
"""

from __future__ import annotations

from typing import Any


def format_chat_response(task_type: str, response_md: str, session_id: str, metadata: dict) -> dict:
    return {
        "response": response_md,
        "task_type": task_type,
        "session_id": session_id,
        "metadata": metadata or {},
    }


def _first(d: dict, *keys, default=""):
    for k in keys:
        v = d.get(k)
        if v not in (None, "", [], {}):
            return v
    return default


def format_job_cards(hits: list[dict[str, Any]]) -> str:
    if not hits:
        return "## Không tìm thấy công việc phù hợp\n\nBạn thử nới rộng từ khóa, địa điểm, hoặc mức lương xem nhé."

    lines: list[str] = [f"## Tìm thấy {len(hits)} công việc phù hợp\n"]
    for i, job in enumerate(hits, start=1):
        title = _first(job, "tieu_de", "title", default="(không rõ tiêu đề)")
        company = _first(job, "cong_ty", "company", default="(không rõ công ty)")
        # location can be `cities` (list) or `dia_diem` (string)
        cities = job.get("cities")
        if isinstance(cities, list) and cities:
            location = ", ".join(str(c) for c in cities)
        else:
            location = _first(job, "dia_diem", "location", default="Không rõ")
        salary_buckets = job.get("salaryBuckets")
        if isinstance(salary_buckets, list) and salary_buckets:
            salary = ", ".join(str(s) for s in salary_buckets)
        else:
            salary = _first(job, "luong", "salary", default="Thỏa thuận")
        link = _first(job, "link", "url", default="")

        head = f"### {i}. {title}"
        if link:
            head = f"### {i}. [{title}]({link})"
        lines.append(head)
        lines.append(f"- 🏢 **Công ty:** {company}")
        lines.append(f"- 📍 **Địa điểm:** {location}")
        lines.append(f"- 💰 **Lương:** {salary}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def format_error(msg: str, code: str = "error", trace_id: str = "") -> dict:
    return {
        "detail": code,
        "error_message": msg,
        "trace_id": trace_id,
    }
