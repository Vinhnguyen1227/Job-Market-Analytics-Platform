from tool_schemas import ToolCallResult

SLASH = {
    "/search": lambda rest: ToolCallResult(tool="search_jobs", params={"keyword": rest}),
    "/coach": lambda rest: ToolCallResult(tool="assess_resume", params={"focus_areas": []}),
    "/review": lambda rest: ToolCallResult(tool="assess_resume", params={"focus_areas": []}),
    "/match": lambda rest: ToolCallResult(tool="match_jobs", params={"jd_text": rest}),
    "/interview": lambda rest: ToolCallResult(tool="interview_prep", params={"target_role": rest, "generate_roadmap": False}),
    "/roadmap": lambda rest: ToolCallResult(tool="interview_prep", params={"target_role": rest, "generate_roadmap": True}),
}

def maybe_handle(msg: str) -> ToolCallResult | None:
    msg = msg.strip()
    if not msg.startswith("/"):
        return None
    parts = msg.split(maxsplit=1)
    cmd = parts[0].lower()
    rest = parts[1] if len(parts) > 1 else ""
    
    if cmd in SLASH:
        return SLASH[cmd](rest)
    return None
