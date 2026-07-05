"""Định nghĩa các Pydantic model cho response của hệ thống matching."""

from typing import List, Union

from pydantic import BaseModel, Field, field_validator, model_validator


class MatchResult(BaseModel):
    """Kết quả phân tích mức độ phù hợp giữa resume và một job posting."""

    job_id: str = Field(
        ...,
        description="ID định danh của job posting",
    )
    job_title: str = Field(
        ...,
        description="Tên vị trí tuyển dụng",
    )
    job_url: str = Field(
        default="",
        description="URL để ứng tuyển",
    )
    match_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Điểm phù hợp từ 0-100",
    )
    strengths: List[str] = Field(
        default_factory=list,
        description="Các điểm mạnh của ứng viên khớp với yêu cầu",
    )
    reasoning: str = Field(
        default="",
        description="Lý do tại sao phù hợp hoặc không phù hợp",
    )
    missing_skills: List[str] = Field(
        default_factory=list,
        description="Các kỹ năng quan trọng ứng viên còn thiếu",
    )
    improvement_tips: str = Field(
        default="",
        description="Gợi ý cải thiện để tăng cơ hội trúng tuyển (một chuỗi duy nhất)",
    )

    @model_validator(mode="before")
    @classmethod
    def normalize_field_names(cls, data):
        """
        LLM đôi khi trả field name khác với schema.
        Map các alias phổ biến về đúng tên field.
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
        """Nếu LLM trả list thay vì string, nối lại thành chuỗi."""
        if isinstance(v, list):
            return "; ".join(str(item) for item in v)
        if v is None:
            return ""
        return v

    @field_validator("reasoning", mode="before")
    @classmethod
    def coerce_reasoning(cls, v):
        """Nếu LLM trả list hoặc None, xử lý cho đúng."""
        if v is None:
            return ""
        if isinstance(v, list):
            return "; ".join(str(item) for item in v)
        return v


class MatchResponse(BaseModel):
    """Response chứa danh sách kết quả matching."""

    matches: List[MatchResult] = Field(
        default_factory=list,
        description="Danh sách các job match đã được phân tích",
    )