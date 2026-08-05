"""Parse AI recommendation JSON into typed candidates."""

from __future__ import annotations

import json

from pydantic import BaseModel, Field, ValidationError

from anicompass.catalog.models import RecommendationCandidate
from anicompass.recommendation.models import ParsedRecommendation


class RecommendationParseError(Exception):
    """Raised when AI output cannot be parsed into candidate recommendations."""


class _AIRecommendationItem(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    year: int | None = Field(default=None, ge=1900, le=2100)
    original_title: str | None = Field(default=None, max_length=160)
    reason: str = Field(min_length=1, max_length=1000)


class _AIRecommendationPayload(BaseModel):
    recommendations: tuple[_AIRecommendationItem, ...] = Field(min_length=1)


class RecommendationParser:
    """Strict parser for the JSON-only response requested by the prompt."""

    def parse(self, content: str) -> tuple[ParsedRecommendation, ...]:
        try:
            raw = json.loads(content)
            payload = _AIRecommendationPayload.model_validate(raw)
        except (json.JSONDecodeError, ValidationError) as exc:
            raise RecommendationParseError(
                "AI recommendation output is invalid."
            ) from exc
        return tuple(
            ParsedRecommendation(
                candidate=RecommendationCandidate(
                    title=item.title,
                    year=item.year,
                    original_title=item.original_title,
                ),
                reason=item.reason,
            )
            for item in payload.recommendations
        )
