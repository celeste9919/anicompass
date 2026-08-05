from __future__ import annotations

import asyncio

import httpx
import pytest

from anicompass.ai import (
    AIProviderErrorCode,
    CredentialService,
    OpenAICompatibleChatClient,
    default_provider_configs,
)


class MemoryCredentialBackend:
    def __init__(self, value: str | None = "sk-test") -> None:
        self.value = value

    def set_password(self, service_name: str, username: str, password: str) -> None:
        self.value = password

    def get_password(self, service_name: str, username: str) -> str | None:
        return self.value

    def delete_password(self, service_name: str, username: str) -> None:
        self.value = None


def _config():
    return default_provider_configs()[0]


def test_openai_compatible_client_posts_chat_completion_request() -> None:
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["auth"] = request.headers.get("authorization")
        captured["json"] = request.read().decode()
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": "ok"}}]},
        )

    client = OpenAICompatibleChatClient(
        CredentialService(backend=MemoryCredentialBackend()),
        httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )

    result = asyncio.run(client.test_connection(_config()))

    assert captured["url"] == "https://api.openai.com/v1/chat/completions"
    assert captured["auth"] == "Bearer sk-test"
    assert "sk-test" not in str(captured["json"])
    assert result.content == "ok"


def test_openai_compatible_client_requires_api_key() -> None:
    client = OpenAICompatibleChatClient(
        CredentialService(backend=MemoryCredentialBackend(value=None)),
        httpx.AsyncClient(
            transport=httpx.MockTransport(lambda request: httpx.Response(200)),
        ),
    )

    with pytest.raises(Exception) as exc_info:
        asyncio.run(client.test_connection(_config()))

    assert exc_info.value.error.code is AIProviderErrorCode.MISSING_API_KEY


def test_openai_compatible_client_maps_auth_and_rate_limit_errors() -> None:
    async def call(status_code: int):
        client = OpenAICompatibleChatClient(
            CredentialService(backend=MemoryCredentialBackend()),
            httpx.AsyncClient(
                transport=httpx.MockTransport(
                    lambda request: httpx.Response(status_code, json={})
                )
            ),
        )
        return await client.test_connection(_config())

    with pytest.raises(Exception) as auth_exc:
        asyncio.run(call(401))
    with pytest.raises(Exception) as rate_exc:
        asyncio.run(call(429))

    assert auth_exc.value.error.code is AIProviderErrorCode.AUTHENTICATION_FAILED
    assert rate_exc.value.error.code is AIProviderErrorCode.RATE_LIMITED


def test_openai_compatible_client_maps_unexpected_payload() -> None:
    client = OpenAICompatibleChatClient(
        CredentialService(backend=MemoryCredentialBackend()),
        httpx.AsyncClient(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(200, json={"choices": []})
            )
        ),
    )

    with pytest.raises(Exception) as exc_info:
        asyncio.run(client.test_connection(_config()))

    assert exc_info.value.error.code is AIProviderErrorCode.PROVIDER_ERROR
