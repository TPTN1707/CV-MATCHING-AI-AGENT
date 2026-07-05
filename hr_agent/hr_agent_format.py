"""Defines the Pydantic models for the matching system response."""

from typing import List, Union

from pydantic import BaseModel, Field, field_validator, model_validator


class MatchResult(BaseModel):
    """Analysis result of the compatibility between a resume and a job posting."""

    job_id: str = Field(
        ...,
        description="Unique identifier of the job posting",
    )
    job_title: str = Field(
        ...,
        description="Job title",
    )
    job_url: str = Field(
        default="",
        description="Application URL",
    )
    match_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Compatibility score from 0 to 100",
    )
    strengths: List[str] = Field(
        default_factory=list,
        description="Candidate strengths that match the job requirements",
    )
    reasoning: str = Field(
        default="",
        description="Reason why the candidate is or is not a good match",
    )
    missing_skills: List[str] = Field(
        default_factory=list,
        description="Important skills the candidate is missing",
    )
    improvement_tips: str = Field(
        default="",
        description="Suggestions to improve the chances of getting hired (a single string)",
    )

    @model_validator(mode="before")
    @classmethod
    def normalize_field_names(cls, data):
        """
        The LLM may sometimes return field names that differ from the schema.
        Map common aliases to the correct field names.
        """
        if not isinstance(data, dict):
            return data

        # reasoning aliases
        if not data.get("reasoning"):
            for alias in ("reason", "explanation", "rationale", "match_reasoning", "fit_reason"):
                if alias in data and data[alias]:
                    data["reasoning"] = data[alias]
                    break

        # improvement_tips aliases
        if not data.get("improvement_tips"):
            for alias in ("tips", "improvement_tip", "advice", "suggestions", "recommendation"):
                if alias in data and data[alias]:
                    data["improvement_tips"] = data[alias]
                    break

        return data

    @field_validator("improvement_tips", mode="before")
    @classmethod
    def coerce_tips_to_str(cls, v):
        """If the LLM returns a list instead of a string, join it into a single string."""
        if isinstance(v, list):
            return "; ".join(str(item) for item in v)
        if v is None:
            return ""
        return v

    @field_validator("reasoning", mode="before")
    @classmethod
    def coerce_reasoning(cls, v):
        """Handle cases where the LLM returns a list or None."""
        if v is None:
            return ""
        if isinstance(v, list):
            return "; ".join(str(item) for item in v)
        return v


class MatchResponse(BaseModel):
    """Response containing the list of matching results."""

    matches: List[MatchResult] = Field(
        default_factory=list,
        description="List of analyzed job matching results",
    )