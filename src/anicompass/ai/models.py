"""AI provider configuration models."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, HttpUrl, field_validator


class AIProviderType(StrEnum):
    """OpenAI-compatible provider presets supported by configuration."""

    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    QWEN = "qwen"
    CUSTOM = "custom"


class AIProviderConfig(BaseModel):
    """Non-secret provider settings stored outside credential storage."""

    provider_type: AIProviderType
    provider_id: str = Field(min_length=1, max_length=80)
    display_name: str = Field(min_length=1, max_length=120)
    base_url: HttpUrl
    model_name: str = Field(min_length=1, max_length=120)
    timeout_seconds: float = Field(default=30, ge=1, le=120)

    @field_validator("provider_id")
    @classmethod
    def provider_id_is_storage_safe(cls, value: str) -> str:
        cleaned = value.strip().lower()
        if not cleaned.replace("-", "").replace("_", "").isalnum():
            raise ValueError("provider_id must be alphanumeric with - or _ only")
        return cleaned


class AIProviderErrorCode(StrEnum):
    """Stable AI provider error states for UI and orchestration."""

    MISSING_API_KEY = "missing_api_key"
    INVALID_REQUEST = "invalid_request"
    AUTHENTICATION_FAILED = "authentication_failed"
    RATE_LIMITED = "rate_limited"
    TIMEOUT = "timeout"
    OFFLINE = "offline"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    PROVIDER_ERROR = "provider_error"


class AIProviderError(BaseModel):
    """Structured AI provider error safe for UI display."""

    code: AIProviderErrorCode
    message: str = Field(min_length=1, max_length=400)
    provider_status_code: int | None = Field(default=None, ge=100, le=599)


class AIProviderResponse(BaseModel):
    """Provider-neutral text response returned from chat completions."""

    provider_id: str
    model_name: str
    content: str = Field(min_length=1, max_length=20000)


class AIProviderCallError(Exception):
    """Exception carrying a stable AI provider error payload."""

    def __init__(self, error: AIProviderError) -> None:
        super().__init__(error.message)
        self.error = error
