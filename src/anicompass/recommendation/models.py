"""Recommendation pipeline models."""

from __future__ import annotations

from pydantic import BaseModel, Field

from anicompass.catalog.models import CatalogAnime, RecommendationCandidate


class RecommendationRequest(BaseModel):
    """User preference input for AI recommendations."""

    preferences: str = Field(min_length=3, max_length=1000)
    count: int = Field(default=5, ge=1, le=10)
    language: str = Field(default="zh", pattern="^(zh|en)$")
    safe_for_all_audiences: bool = True


class ParsedRecommendation(BaseModel):
    """Candidate and AI explanation before catalog verification."""

    candidate: RecommendationCandidate
    reason: str = Field(min_length=1, max_length=1000)


class VerifiedRecommendation(BaseModel):
    """Catalog-verified recommendation shown to users."""

    anime: CatalogAnime
    reason: str = Field(min_length=1, max_length=1000)


class RecommendationResult(BaseModel):
    """Recommendation pipeline output with explicit unresolved candidates."""

    items: tuple[VerifiedRecommendation, ...]
    unresolved: tuple[ParsedRecommendation, ...] = ()
