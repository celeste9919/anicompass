"""Recommendation history models."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RecommendationHistorySession(BaseModel):
    """A completed recommendation session saved locally."""

    model_config = ConfigDict(frozen=True)

    session_id: int | None = None
    preferences: str = Field(min_length=1, max_length=1000)
    language: str = Field(default="zh", pattern="^(zh|en)$")
    verified_count: int = Field(ge=0, le=10)
    unresolved_count: int = Field(default=0, ge=0, le=10)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("created_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value
