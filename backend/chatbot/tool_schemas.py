"""
Tool Call Schemas — Pydantic models for Adapter A output validation.

Mirrors the training-time schemas from chatbot/phase 6-dataset-synthesis/
tool_call_schemas.py. Used to validate both Adapter A JSON output and
slash command arguments.
"""

from __future__ import annotations

from typing import List, Optional
import logging

from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


# ── Valid Enum Values ────────────────────────────────

# Common location aliases → canonical name
LOCATION_ALIASES = {
    "sg": "Hồ Chí Minh",
    "sài gòn": "Hồ Chí Minh",
    "saigon": "Hồ Chí Minh",
    "hcm": "Hồ Chí Minh",
    "hn": "Hà Nội",
    "ha noi": "Hà Nội",
    "đn": "Đà Nẵng",
    "da nang": "Đà Nẵng",
}


# ── Tool Parameter Schemas ───────────────────────────

class SearchJobsParams(BaseModel):
    """Parameters for search_jobs tool."""

    keyword: Optional[str] = None
    location: Optional[str] = None
    min_salary: Optional[int] = Field(None, ge=0, le=200)
    max_salary: Optional[int] = Field(None, ge=0, le=200)
    experience: Optional[str] = None
    work_type: Optional[str] = None

    @field_validator("location")
    @classmethod
    def validate_location(cls, v):
        if v is None:
            return v
        # Check aliases first
        alias = LOCATION_ALIASES.get(v.lower().strip())
        if alias:
            return alias
        from enum_cache import enum_cache
        cities = enum_cache.cities
        if not cities:
            return v
            
        if v not in cities:
            # Fuzzy match: check if input is substring of a valid city
            for city in cities:
                if v.lower() in city.lower():
                    return city
            logger.warning(f"Unknown location passed through: {v}")
        return v

    @field_validator("experience")
    @classmethod
    def validate_exp(cls, v):
        from enum_cache import enum_cache
        exp_buckets = enum_cache.exp_buckets
        if exp_buckets and v is not None and v not in exp_buckets:
            logger.warning(f"Unknown experience passed through: {v}")
        return v

    @field_validator("work_type")
    @classmethod
    def validate_work_type(cls, v):
        from enum_cache import enum_cache
        work_types = enum_cache.work_types
        if work_types and v is not None and v not in work_types:
            logger.warning(f"Unknown work type passed through: {v}")
        return v


class AssessResumeParams(BaseModel):
    """Parameters for assess_resume tool."""

    focus_areas: List[str] = Field(default_factory=list)


class MatchJobsParams(BaseModel):
    """Parameters for match_jobs tool."""

    target_role: Optional[str] = None
    cv_json: Optional[str] = None
    jd_text: Optional[str] = None


class InterviewPrepParams(BaseModel):
    """Parameters for interview_prep tool."""

    target_role: Optional[str] = None
    generate_roadmap: bool = False


class GeneralResponseParams(BaseModel):
    """Parameters for general_response tool (empty)."""

    pass


# ── Tool Call Envelope ───────────────────────────────

TOOL_PARAM_MAP = {
    "search_jobs": SearchJobsParams,
    "assess_resume": AssessResumeParams,
    "match_jobs": MatchJobsParams,
    "interview_prep": InterviewPrepParams,
    "general_response": GeneralResponseParams,
}


class ToolCallResult(BaseModel):
    """Validated tool call from Adapter A output.

    Attributes:
        tool: Tool name (one of the 5 defined tools).
        params: Validated parameters for the tool.
    """

    tool: str
    params: dict = Field(default_factory=dict)

    @field_validator("tool")
    @classmethod
    def validate_tool(cls, v):
        if v not in TOOL_PARAM_MAP:
            raise ValueError(
                f"Unknown tool: '{v}'. Valid tools: {list(TOOL_PARAM_MAP.keys())}"
            )
        return v

    def validated_params(self) -> BaseModel:
        """Parse and validate params against the tool's schema.

        Returns:
            Validated Pydantic model for this tool's params.
        """
        schema_cls = TOOL_PARAM_MAP[self.tool]
        return schema_cls(**self.params)
