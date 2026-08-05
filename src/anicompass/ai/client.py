"""OpenAI-compatible chat-completions client."""

from __future__ import annotations

import httpx

from anicompass.ai.credentials import CredentialError, CredentialService
from anicompass.ai.models import (
    AIProviderCallError,
    AIProviderConfig,
    AIProviderError,
    AIProviderErrorCode,
    AIProviderResponse,
)


class OpenAICompatibleChatClient:
    """Call an OpenAI-compatible `/chat/completions` endpoint."""

    def __init__(
        self,
        credential_service: CredentialService,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._credential_service = credential_service
        self._http_client = http_client or httpx.AsyncClient()

    async def complete(
        self,
        config: AIProviderConfig,
        user_prompt: str,
        *,
        system_prompt: str = "You are AniCompass, an anime recommendation assistant.",
        max_tokens: int = 256,
    ) -> AIProviderResponse:
        api_key = self._read_api_key(config.provider_id)
        payload = {
            "model": config.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
            "max_tokens": max_tokens,
        }
        try:
            response = await self._http_client.post(
                self._endpoint(config),
                json=payload,
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=config.timeout_seconds,
            )
        except httpx.TimeoutException as exc:
            raise self._error(
                AIProviderErrorCode.TIMEOUT,
                "AI provider request timed out.",
            ) from exc
        except httpx.TransportError as exc:
            raise self._error(
                AIProviderErrorCode.OFFLINE,
                "AI provider is unreachable.",
            ) from exc

        if response.status_code >= 400:
            raise self._http_error(response)
        return self._parse_response(config, response)

    async def test_connection(self, config: AIProviderConfig) -> AIProviderResponse:
        return await self.complete(
            config,
            "Reply with the single word: ok",
            system_prompt="You are a connection test endpoint.",
            max_tokens=8,
        )

    def _read_api_key(self, provider_id: str) -> str:
        try:
            api_key = self._credential_service.get_api_key(provider_id)
        except CredentialError as exc:
            raise self._error(
                AIProviderErrorCode.MISSING_API_KEY,
                exc.public_message,
            ) from exc
        if not api_key:
            raise self._error(
                AIProviderErrorCode.MISSING_API_KEY,
                "API key is missing.",
            )
        return api_key

    def _endpoint(self, config: AIProviderConfig) -> str:
        base_url = str(config.base_url).rstrip("/")
        return f"{base_url}/chat/completions"

    def _parse_response(
        self,
        config: AIProviderConfig,
        response: httpx.Response,
    ) -> AIProviderResponse:
        try:
            body = response.json()
            content = body["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise self._error(
                AIProviderErrorCode.PROVIDER_ERROR,
                "AI provider returned an unexpected response.",
                response.status_code,
            ) from exc
        if not content:
            raise self._error(
                AIProviderErrorCode.PROVIDER_ERROR,
                "AI provider returned an empty response.",
                response.status_code,
            )
        return AIProviderResponse(
            provider_id=config.provider_id,
            model_name=config.model_name,
            content=content,
        )

    def _http_error(self, response: httpx.Response) -> AIProviderCallError:
        code = AIProviderErrorCode.PROVIDER_ERROR
        message = "AI provider request failed."
        if response.status_code == 400:
            code = AIProviderErrorCode.INVALID_REQUEST
            message = "AI provider rejected the request."
        elif response.status_code in {401, 403}:
            code = AIProviderErrorCode.AUTHENTICATION_FAILED
            message = "AI provider authentication failed."
        elif response.status_code == 429:
            code = AIProviderErrorCode.RATE_LIMITED
            message = "AI provider rate limit was reached."
        elif response.status_code >= 500:
            code = AIProviderErrorCode.PROVIDER_UNAVAILABLE
            message = "AI provider is temporarily unavailable."
        return self._error(code, message, response.status_code)

    def _error(
        self,
        code: AIProviderErrorCode,
        message: str,
        status_code: int | None = None,
    ) -> AIProviderCallError:
        return AIProviderCallError(
            AIProviderError(
                code=code,
                message=message,
                provider_status_code=status_code,
            )
        )
