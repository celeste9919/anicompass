"""Catalog provider interfaces and Jikan adapter."""

from __future__ import annotations

import asyncio
from typing import Any, Protocol

import httpx
from pydantic import ValidationError

from anicompass.catalog.models import (
    CatalogAnime,
    CatalogAnimeId,
    CatalogError,
    CatalogErrorCode,
    CatalogFilters,
    CatalogProviderError,
    CatalogSearchResult,
    CatalogSource,
    RecommendationCandidate,
)

JsonObject = dict[str, Any]


class CatalogProvider(Protocol):
    """Provider-neutral catalog contract."""

    source: CatalogSource

    async def search(self, filters: CatalogFilters) -> CatalogSearchResult:
        """Search anime by provider-neutral filters."""

    async def get_by_id(self, catalog_id: CatalogAnimeId) -> CatalogAnime:
        """Fetch one anime by provider identity."""

    async def resolve_candidate(
        self, candidate: RecommendationCandidate
    ) -> CatalogAnime | None:
        """Resolve an AI candidate to verified catalog metadata."""


class JikanRateLimiter:
    """Small in-process limiter matching Jikan's documented public limits."""

    def __init__(self, requests_per_second: int = 3) -> None:
        self._min_interval = 1 / requests_per_second
        self._last_request = 0.0
        self._lock = asyncio.Lock()

    async def wait(self) -> None:
        loop = asyncio.get_running_loop()
        async with self._lock:
            now = loop.time()
            delay = self._min_interval - (now - self._last_request)
            if delay > 0:
                await asyncio.sleep(delay)
            self._last_request = loop.time()


class JikanCatalogProvider:
    """Jikan v4 catalog adapter."""

    source = CatalogSource.JIKAN
    base_url = "https://api.jikan.moe/v4"
    requests_per_second = 3
    requests_per_minute = 60

    def __init__(
        self,
        client: httpx.AsyncClient | None = None,
        *,
        base_url: str | None = None,
        timeout_seconds: float = 10.0,
        rate_limiter: JikanRateLimiter | None = None,
    ) -> None:
        self._owns_client = client is None
        self._client = client or httpx.AsyncClient(timeout=timeout_seconds)
        self._base_url = (base_url or self.base_url).rstrip("/")
        self._rate_limiter = rate_limiter or JikanRateLimiter(
            self.requests_per_second
        )

    async def search(self, filters: CatalogFilters) -> CatalogSearchResult:
        payload = await self._get_json(
            "/anime",
            params={
                "q": filters.query,
                "limit": filters.limit,
                "sfw": "true" if filters.safe_for_all_audiences else "false",
            },
        )
        data = payload.get("data")
        if not isinstance(data, list):
            raise self._provider_error("Jikan search response did not include data.")
        return CatalogSearchResult(
            items=tuple(self._normalize_anime(item) for item in data),
            source=self.source,
            query=filters.query,
            rate_limit_remaining=self._read_rate_limit_remaining(payload),
        )

    async def get_by_id(self, catalog_id: CatalogAnimeId) -> CatalogAnime:
        if catalog_id.source is not self.source:
            raise ValueError(f"Unsupported catalog source: {catalog_id.source}")
        payload = await self._get_json(f"/anime/{catalog_id.provider_id}")
        data = payload.get("data")
        if not isinstance(data, dict):
            raise self._provider_error("Jikan detail response did not include data.")
        return self._normalize_anime(data)

    async def resolve_candidate(
        self, candidate: RecommendationCandidate
    ) -> CatalogAnime | None:
        filters = CatalogFilters(query=candidate.title, limit=5)
        result = await self.search(filters)
        if candidate.year is None:
            return result.items[0] if result.items else None
        for item in result.items:
            if item.year == candidate.year:
                return item
        return result.items[0] if result.items else None

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def _get_json(
        self, path: str, params: dict[str, str | int] | None = None
    ) -> JsonObject:
        await self._rate_limiter.wait()
        try:
            response = await self._client.get(
                f"{self._base_url}{path}", params=params
            )
        except httpx.TimeoutException as exc:
            raise self._catalog_error(
                CatalogErrorCode.TIMEOUT, "Jikan timed out."
            ) from exc
        except httpx.RequestError as exc:
            raise self._catalog_error(
                CatalogErrorCode.OFFLINE, "Jikan is unreachable."
            ) from exc

        if response.status_code >= 400 or response.status_code == 304:
            raise self._error_from_response(response)

        try:
            payload = response.json()
        except ValueError as exc:
            raise self._provider_error("Jikan returned invalid JSON.") from exc
        if not isinstance(payload, dict):
            raise self._provider_error("Jikan returned an unexpected JSON payload.")
        return payload

    def _normalize_anime(self, raw: JsonObject) -> CatalogAnime:
        try:
            return CatalogAnime(
                catalog_id=CatalogAnimeId(
                    source=self.source, provider_id=str(raw.get("mal_id"))
                ),
                title=self._first_text(raw, "title", "title_english", "title_japanese"),
                original_title=self._optional_text(raw.get("title_japanese")),
                english_title=self._optional_text(raw.get("title_english")),
                synopsis=self._optional_text(raw.get("synopsis")),
                media_type=self._optional_text(raw.get("type")),
                episodes=raw.get("episodes"),
                year=raw.get("year"),
                season=self._optional_text(raw.get("season")),
                rating=self._optional_text(raw.get("rating")),
                score=raw.get("score"),
                image_url=self._image_url(raw),
                genres=self._names(raw.get("genres")),
                studios=self._names(raw.get("studios")),
                source_url=self._optional_text(raw.get("url")),
            )
        except (TypeError, ValidationError, ValueError) as exc:
            raise self._provider_error(
                "Jikan anime item could not be normalized."
            ) from exc

    def _error_from_response(self, response: httpx.Response) -> CatalogProviderError:
        status_map = {
            400: CatalogErrorCode.INVALID_REQUEST,
            404: CatalogErrorCode.NOT_FOUND,
            405: CatalogErrorCode.INVALID_REQUEST,
            429: CatalogErrorCode.RATE_LIMITED,
            500: CatalogErrorCode.PROVIDER_UNAVAILABLE,
            503: CatalogErrorCode.PROVIDER_UNAVAILABLE,
        }
        code = status_map.get(response.status_code)
        if code is None and response.status_code >= 500:
            code = CatalogErrorCode.PROVIDER_UNAVAILABLE
        if code is None:
            code = CatalogErrorCode.PROVIDER_ERROR
        return self._catalog_error(
            code,
            f"Jikan returned HTTP {response.status_code}.",
            retry_after_seconds=self._retry_after(response),
            provider_status_code=response.status_code,
        )

    def _catalog_error(
        self,
        code: CatalogErrorCode,
        message: str,
        *,
        retry_after_seconds: int | None = None,
        provider_status_code: int | None = None,
    ) -> CatalogProviderError:
        return CatalogProviderError(
            CatalogError(
                code=code,
                message=message,
                retry_after_seconds=retry_after_seconds,
                provider_status_code=provider_status_code,
            )
        )

    def _provider_error(self, message: str) -> CatalogProviderError:
        return self._catalog_error(CatalogErrorCode.PROVIDER_ERROR, message)

    def _retry_after(self, response: httpx.Response) -> int | None:
        value = response.headers.get("Retry-After")
        if value is None:
            return None
        try:
            return max(0, int(value))
        except ValueError:
            return None

    def _read_rate_limit_remaining(self, payload: JsonObject) -> int | None:
        value = payload.get("rate_limit_remaining")
        try:
            return int(value) if value is not None else None
        except (TypeError, ValueError):
            return None

    def _first_text(self, raw: JsonObject, *keys: str) -> str:
        for key in keys:
            value = self._optional_text(raw.get(key))
            if value:
                return value
        raise ValueError("missing title")

    def _optional_text(self, value: object) -> str | None:
        if isinstance(value, str):
            stripped = value.strip()
            return stripped or None
        return None

    def _names(self, value: object) -> tuple[str, ...]:
        if not isinstance(value, list):
            return ()
        names: list[str] = []
        for item in value:
            if isinstance(item, dict):
                name = self._optional_text(item.get("name"))
                if name:
                    names.append(name)
        return tuple(names)

    def _image_url(self, raw: JsonObject) -> str | None:
        images = raw.get("images")
        if not isinstance(images, dict):
            return None
        for group_name in ("jpg", "webp"):
            group = images.get(group_name)
            if isinstance(group, dict):
                url = self._optional_text(group.get("image_url"))
                if url:
                    return url
        return None
