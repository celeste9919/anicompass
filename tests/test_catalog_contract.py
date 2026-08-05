from __future__ import annotations

import asyncio

import httpx
import pytest
from pydantic import ValidationError

from anicompass.catalog import (
    CatalogAnime,
    CatalogAnimeId,
    CatalogErrorCode,
    CatalogFilters,
    CatalogProviderError,
    CatalogSource,
    JikanCatalogProvider,
    RecommendationCandidate,
)


class NoWaitLimiter:
    async def wait(self) -> None:
        return None


def _sample_anime(provider_id: int = 1) -> dict:
    return {
        "mal_id": provider_id,
        "url": f"https://myanimelist.net/anime/{provider_id}/Cowboy_Bebop",
        "images": {"jpg": {"image_url": "https://cdn.example.test/bebop.jpg"}},
        "title": "Cowboy Bebop",
        "title_english": "Cowboy Bebop",
        "title_japanese": "\u30ab\u30a6\u30dc\u30fc\u30a4\u30d3\u30d0\u30c3\u30d7",
        "type": "TV",
        "episodes": 26,
        "rating": "R - 17+",
        "score": 8.75,
        "synopsis": "Bounty hunters in space.",
        "year": 1998,
        "season": "spring",
        "genres": [{"name": "Action"}, {"name": "Sci-Fi"}],
        "studios": [{"name": "Sunrise"}],
    }


def _client(handler) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


def test_catalog_models_validate_provider_neutral_anime() -> None:
    anime = CatalogAnime(
        catalog_id=CatalogAnimeId(source=CatalogSource.JIKAN, provider_id="1"),
        title="Cowboy Bebop",
        original_title="Cowboy Bebop",
        episodes=26,
        year=1998,
        score=8.75,
        genres=("Action", "Sci-Fi"),
        source_url="https://myanimelist.net/anime/1/Cowboy_Bebop",
    )

    assert anime.catalog_id.provider_id == "1"
    assert anime.attribution == "Jikan / MyAnimeList"
    assert anime.genres == ("Action", "Sci-Fi")


def test_catalog_filters_reject_empty_query_and_large_limit() -> None:
    with pytest.raises(ValidationError):
        CatalogFilters(query="")

    with pytest.raises(ValidationError):
        CatalogFilters(query="anime", limit=100)


def test_jikan_search_normalizes_results_and_query_params() -> None:
    captured: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["path"] = request.url.path
        captured["query"] = request.url.query.decode()
        return httpx.Response(200, json={"data": [_sample_anime()]})

    provider = JikanCatalogProvider(
        client=_client(handler), rate_limiter=NoWaitLimiter()
    )
    result = asyncio.run(provider.search(CatalogFilters(query="bebop", limit=3)))

    assert captured["path"] == "/v4/anime"
    assert "q=bebop" in captured["query"]
    assert "limit=3" in captured["query"]
    assert "sfw=true" in captured["query"]
    assert result.source is CatalogSource.JIKAN
    assert result.query == "bebop"
    assert result.items[0].catalog_id.provider_id == "1"
    assert result.items[0].title == "Cowboy Bebop"
    assert result.items[0].genres == ("Action", "Sci-Fi")
    assert str(result.items[0].image_url) == "https://cdn.example.test/bebop.jpg"


def test_jikan_get_by_id_normalizes_detail_result() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v4/anime/1"
        return httpx.Response(200, json={"data": _sample_anime()})

    provider = JikanCatalogProvider(
        client=_client(handler), rate_limiter=NoWaitLimiter()
    )
    anime = asyncio.run(
        provider.get_by_id(CatalogAnimeId(source=CatalogSource.JIKAN, provider_id="1"))
    )

    assert anime.media_type == "TV"
    assert anime.studios == ("Sunrise",)


def test_jikan_rate_limit_response_maps_retry_after() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, headers={"Retry-After": "8"}, json={})

    provider = JikanCatalogProvider(
        client=_client(handler), rate_limiter=NoWaitLimiter()
    )

    with pytest.raises(CatalogProviderError) as exc_info:
        asyncio.run(provider.search(CatalogFilters(query="bebop")))

    assert exc_info.value.error.code is CatalogErrorCode.RATE_LIMITED
    assert exc_info.value.error.retry_after_seconds == 8
    assert exc_info.value.error.provider_status_code == 429


def test_jikan_gateway_timeout_maps_to_provider_unavailable() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(504, json={})

    provider = JikanCatalogProvider(
        client=_client(handler), rate_limiter=NoWaitLimiter()
    )

    with pytest.raises(CatalogProviderError) as exc_info:
        asyncio.run(provider.search(CatalogFilters(query="bebop")))

    assert exc_info.value.error.code is CatalogErrorCode.PROVIDER_UNAVAILABLE
    assert exc_info.value.error.provider_status_code == 504

def test_jikan_timeout_maps_to_catalog_timeout() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("slow")

    provider = JikanCatalogProvider(
        client=_client(handler), rate_limiter=NoWaitLimiter()
    )

    with pytest.raises(CatalogProviderError) as exc_info:
        asyncio.run(provider.search(CatalogFilters(query="bebop")))

    assert exc_info.value.error.code is CatalogErrorCode.TIMEOUT


def test_jikan_resolve_candidate_prefers_matching_year() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        first = _sample_anime(provider_id=1)
        first["year"] = 1998
        second = _sample_anime(provider_id=2)
        second["year"] = 2020
        return httpx.Response(200, json={"data": [first, second]})

    provider = JikanCatalogProvider(
        client=_client(handler), rate_limiter=NoWaitLimiter()
    )
    result = asyncio.run(
        provider.resolve_candidate(
            RecommendationCandidate(title="Cowboy Bebop", year=2020)
        )
    )

    assert result is not None
    assert result.catalog_id.provider_id == "2"
