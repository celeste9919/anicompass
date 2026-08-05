"""Versioned local backup models for AniCompass."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

BACKUP_FORMAT_VERSION = 1


class BackupWatchListItem(BaseModel):
    """Watch-list data that is safe to export."""

    model_config = ConfigDict(frozen=True)

    item_id: int | None = Field(default=None, ge=1)
    catalog_source: str = Field(min_length=1, max_length=40)
    provider_id: str = Field(min_length=1, max_length=80)
    title: str = Field(min_length=1, max_length=200)
    original_title: str | None = Field(default=None, max_length=200)
    image_url: str | None = Field(default=None, max_length=1000)
    source_url: str | None = Field(default=None, max_length=1000)
    status: str = Field(min_length=1, max_length=40)
    progress: int = Field(ge=0, le=9999)
    score: int | None = Field(default=None, ge=1, le=10)
    notes: str = Field(default="", max_length=2000)
    created_at: datetime
    updated_at: datetime

    @field_validator("created_at", "updated_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value


class BackupHistorySession(BaseModel):
    """Recommendation history data that is safe to export."""

    model_config = ConfigDict(frozen=True)

    session_id: int | None = Field(default=None, ge=1)
    preferences: str = Field(min_length=1, max_length=1000)
    language: Literal["zh", "en"] = "zh"
    verified_count: int = Field(ge=0, le=10)
    unresolved_count: int = Field(default=0, ge=0, le=10)
    created_at: datetime

    @field_validator("created_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value


class AniCompassBackup(BaseModel):
    """Versioned backup file payload."""

    model_config = ConfigDict(frozen=True)

    app: Literal["AniCompass"] = "AniCompass"
    format_version: Literal[BACKUP_FORMAT_VERSION] = BACKUP_FORMAT_VERSION
    exported_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    watch_list_items: tuple[BackupWatchListItem, ...] = ()
    recommendation_history: tuple[BackupHistorySession, ...] = ()

    @field_validator("exported_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value
