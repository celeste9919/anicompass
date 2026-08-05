"""Local watch-list domain models."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from anicompass.catalog.models import CatalogAnimeId, CatalogSource


class WatchStatus(StrEnum):
    """User-owned watch-list states."""

    PLAN_TO_WATCH = "plan_to_watch"
    WATCHING = "watching"
    COMPLETED = "completed"


class WatchListItem(BaseModel):
    """A locally persisted anime entry owned by the user."""

    model_config = ConfigDict(frozen=True)

    item_id: int | None = None
    catalog_id: CatalogAnimeId
    title: str = Field(min_length=1, max_length=200)
    original_title: str | None = Field(default=None, max_length=200)
    image_url: str | None = Field(default=None, max_length=1000)
    source_url: str | None = Field(default=None, max_length=1000)
    status: WatchStatus = WatchStatus.PLAN_TO_WATCH
    progress: int = Field(default=0, ge=0, le=9999)
    score: int | None = Field(default=None, ge=1, le=10)
    notes: str = Field(default="", max_length=2000)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("created_at", "updated_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value


class WatchListUpdate(BaseModel):
    """Validated patch values for a watch-list item."""

    status: WatchStatus | None = None
    progress: int | None = Field(default=None, ge=0, le=9999)
    score: int | None = Field(default=None, ge=1, le=10)
    notes: str | None = Field(default=None, max_length=2000)


class WatchListFilter(BaseModel):
    """Optional list filter."""

    status: WatchStatus | None = None


def parse_catalog_source(value: str) -> CatalogSource:
    return CatalogSource(value)
