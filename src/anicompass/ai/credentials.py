"""Credential storage boundary backed by the operating-system keyring."""

from __future__ import annotations

from typing import Protocol

import keyring
from keyring.errors import KeyringError


class CredentialBackend(Protocol):
    def set_password(self, service_name: str, username: str, password: str) -> None: ...
    def get_password(self, service_name: str, username: str) -> str | None: ...
    def delete_password(self, service_name: str, username: str) -> None: ...


class CredentialError(Exception):
    """Base credential error with a stable public code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.public_message = message


class CredentialService:
    """Store provider API keys without exposing them to settings or logs."""

    def __init__(
        self,
        backend: CredentialBackend | None = None,
        service_name: str = "AniCompass",
    ) -> None:
        self._backend = backend or keyring
        self._service_name = service_name

    def set_api_key(self, provider_id: str, value: str) -> None:
        account = self._account(provider_id)
        secret = value.strip()
        if not secret:
            raise CredentialError("empty_secret", "API key cannot be empty.")
        try:
            self._backend.set_password(self._service_name, account, secret)
        except KeyringError as exc:
            raise CredentialError(
                "keyring_unavailable",
                "Operating-system credential storage is unavailable.",
            ) from exc

    def has_api_key(self, provider_id: str) -> bool:
        return self.get_api_key(provider_id) is not None

    def get_api_key(self, provider_id: str) -> str | None:
        try:
            value = self._backend.get_password(
                self._service_name,
                self._account(provider_id),
            )
        except KeyringError as exc:
            raise CredentialError(
                "keyring_unavailable",
                "Operating-system credential storage is unavailable.",
            ) from exc
        return value or None

    def delete_api_key(self, provider_id: str) -> None:
        try:
            self._backend.delete_password(
                self._service_name,
                self._account(provider_id),
            )
        except KeyringError as exc:
            raise CredentialError(
                "keyring_unavailable",
                "Operating-system credential storage is unavailable.",
            ) from exc

    def _account(self, provider_id: str) -> str:
        cleaned = provider_id.strip().lower()
        if not cleaned:
            raise CredentialError("invalid_provider", "Provider id is required.")
        return f"ai-provider:{cleaned}"
