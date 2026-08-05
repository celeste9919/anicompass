from __future__ import annotations

import pytest
from keyring.errors import KeyringError
from pydantic import ValidationError

from anicompass.ai import (
    AIProviderConfig,
    AIProviderType,
    CredentialError,
    CredentialService,
    default_provider_configs,
)


class MemoryCredentialBackend:
    def __init__(self) -> None:
        self.values: dict[tuple[str, str], str] = {}

    def set_password(self, service_name: str, username: str, password: str) -> None:
        self.values[(service_name, username)] = password

    def get_password(self, service_name: str, username: str) -> str | None:
        return self.values.get((service_name, username))

    def delete_password(self, service_name: str, username: str) -> None:
        self.values.pop((service_name, username), None)


class FailingCredentialBackend(MemoryCredentialBackend):
    def set_password(self, service_name: str, username: str, password: str) -> None:
        raise KeyringError("backend unavailable")

    def get_password(self, service_name: str, username: str) -> str | None:
        raise KeyringError("backend unavailable")

    def delete_password(self, service_name: str, username: str) -> None:
        raise KeyringError("backend unavailable")


def test_default_provider_configs_are_non_secret_openai_compatible_presets() -> None:
    configs = default_provider_configs()

    assert {config.provider_id for config in configs} == {
        "openai",
        "deepseek",
        "qwen",
        "custom",
    }
    assert all("key" not in config.model_dump() for config in configs)
    assert all(str(config.base_url).endswith("/v1") for config in configs)


def test_ai_provider_config_normalizes_and_validates_provider_id() -> None:
    config = AIProviderConfig(
        provider_type=AIProviderType.CUSTOM,
        provider_id=" My_Custom-Provider ",
        display_name="Custom",
        base_url="https://example.com/v1",
        model_name="anime-model",
    )

    assert config.provider_id == "my_custom-provider"

    with pytest.raises(ValidationError):
        AIProviderConfig(
            provider_type=AIProviderType.CUSTOM,
            provider_id="bad/provider",
            display_name="Custom",
            base_url="https://example.com/v1",
            model_name="anime-model",
        )


def test_credential_service_sets_reads_checks_and_deletes_api_key() -> None:
    backend = MemoryCredentialBackend()
    service = CredentialService(backend=backend)

    service.set_api_key("OpenAI", " sk-test ")

    assert service.has_api_key("openai") is True
    assert service.get_api_key("openai") == "sk-test"

    service.delete_api_key("openai")

    assert service.has_api_key("openai") is False


def test_credential_service_rejects_empty_secret_without_backend_write() -> None:
    backend = MemoryCredentialBackend()
    service = CredentialService(backend=backend)

    with pytest.raises(CredentialError) as exc_info:
        service.set_api_key("openai", "  ")

    assert exc_info.value.code == "empty_secret"
    assert backend.values == {}


def test_credential_service_maps_keyring_backend_failures() -> None:
    service = CredentialService(backend=FailingCredentialBackend())

    with pytest.raises(CredentialError) as exc_info:
        service.set_api_key("openai", "sk-test")

    assert exc_info.value.code == "keyring_unavailable"
