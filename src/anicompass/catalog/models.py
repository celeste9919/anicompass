"""Provider-neutral catalog models."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class CatalogSource(StrEnum):
    """Supported external catalog sources."""

    JIKAN = "jikan"


class CatalogErrorCode(StrEnum):
    """Errors that catalog adapters must map into stable app states."""

    INVALID_REQUEST = "invalid_request"
    NOT_FOUND = "not_found"
    RATE_LIMITED = "rate_limited"
    TIMEOUT = "timeout"
    OFFLINE = "offline"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    PROVIDER_ERROR = "provider_error"
    NOT_IMPLEMENTED = "not_implemented"


class CatalogAnimeId(BaseModel):
    """Stable provider identity for an anime entry."""

    model_config = ConfigDict(frozen=True)

    source: CatalogSource
    provider_id: str = Field(min_length=1)


class CatalogFilters(BaseModel):
    """Provider-neutral search filters."""

    query: str = Field(min_length=1, max_length=120)
    safe_for_all_audiences: bool = True
    limit: int = Field(default=10, ge=1, le=25)


class RecommendationCandidate(BaseModel):
    """AI-produced candidate identity before catalog verification."""

    title: str = Field(min_length=1, max_length=160)
    year: int | None = Field(default=None, ge=1900, le=2100)
    original_title: str | None = Field(default=None, max_length=160)


class CatalogAnime(BaseModel):
    """Normalized anime metadata shown by the app."""

    catalog_id: CatalogAnimeId
    title: str = Field(min_length=1, max_length=200)
    original_title: str | None = Field(default=None, max_length=200)
    english_title: str | None = Field(default=None, max_length=200)
    synopsis: str | None = Field(default=None, max_length=4000)
    media_type: str | None = Field(default=None, max_length=60)
    episodes: int | None = Field(default=None, ge=0)
    year: int | None = Field(default=None, ge=1900, le=2100)
    season: str | None = Field(default=None, max_length=20)
    rating: str | None = Field(default=None, max_length=80)
    score: float | None = Field(default=None, ge=0, le=10)
    image_url: HttpUrl | None = None
    genres: tuple[str, ...] = ()
    studios: tuple[str, ...] = ()
    source_url: HttpUrl | None = None
    attribution: str = Field(default="Jikan / MyAnimeList", max_length=120)


class CatalogSearchResult(BaseModel):
    """Search response without provider-specific response shapes."""

    items: tuple[CatalogAnime, ...]
    source: CatalogSource
    query: str
    rate_limit_remaining: int | None = Field(default=None, ge=0)


class CatalogError(BaseModel):
    """Structured catalog error for UI and orchestration layers."""

    code: CatalogErrorCode
    message: str = Field(min_length=1, max_length=400)
    retry_after_seconds: int | None = Field(default=None, ge=0)
    provider_status_code: int | None = Field(default=None, ge=100, le=599)


class CatalogProviderError(Exception):
    """Exception wrapper carrying a stable catalog error payload."""

    def __init__(self, error: CatalogError) -> None:
        super().__init__(error.message)
        self.error = error
