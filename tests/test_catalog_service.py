from __future__ import annotations

import asyncio

import pytest

from anicompass.catalog import (
    CatalogAnime,
    CatalogAnimeId,
    CatalogError,
    CatalogErrorCode,
    CatalogFilters,
    CatalogProviderError,
    CatalogSearchResult,
    CatalogService,
    CatalogSource,
    RecommendationCandidate,
)


class RecordingProvider:
    source = CatalogSource.JIKAN

    def __init__(self) -> None:
        self.search_filters: CatalogFilters | None = None
        self.detail_id: CatalogAnimeId | None = None
        self.candidate: RecommendationCandidate | None = None
        self.anime = CatalogAnime(
            catalog_id=CatalogAnimeId(source=CatalogSource.JIKAN, provider_id="1"),
            title="Cowboy Bebop",
            year=1998,
        )

    async def search(self, filters: CatalogFilters) -> CatalogSearchResult:
        self.search_filters = filters
        return CatalogSearchResult(
            items=(self.anime,), source=self.source, query=filters.query
        )

    async def get_by_id(self, catalog_id: CatalogAnimeId) -> CatalogAnime:
        self.detail_id = catalog_id
        return self.anime

    async def resolve_candidate(
        self, candidate: RecommendationCandidate
    ) -> CatalogAnime | None:
        self.candidate = candidate
        return self.anime


class FailingProvider(RecordingProvider):
    async def search(self, filters: CatalogFilters) -> CatalogSearchResult:
        raise CatalogProviderError(
            CatalogError(
                code=CatalogErrorCode.RATE_LIMITED,
                message="Rate limited.",
                retry_after_seconds=5,
                provider_status_code=429,
            )
        )


def test_catalog_service_search_uses_default_provider_and_trims_query() -> None:
    provider = RecordingProvider()
    service = CatalogService({CatalogSource.JIKAN: provider})

    result = asyncio.run(service.search("  bebop  ", limit=3))

    assert provider.search_filters == CatalogFilters(query="bebop", limit=3)
    assert result.items[0].title == "Cowboy Bebop"
    assert result.query == "bebop"


def test_catalog_service_rejects_invalid_search_input() -> None:
    service = CatalogService({CatalogSource.JIKAN: RecordingProvider()})

    with pytest.raises(CatalogProviderError) as exc_info:
        asyncio.run(service.search("   "))

    assert exc_info.value.error.code is CatalogErrorCode.INVALID_REQUEST


def test_catalog_service_get_by_id_routes_by_catalog_source() -> None:
    provider = RecordingProvider()
    service = CatalogService({CatalogSource.JIKAN: provider})
    catalog_id = CatalogAnimeId(source=CatalogSource.JIKAN, provider_id="1")

    anime = asyncio.run(service.get_by_id(catalog_id))

    assert provider.detail_id == catalog_id
    assert anime.catalog_id == catalog_id


def test_catalog_service_resolve_candidate_routes_to_provider() -> None:
    provider = RecordingProvider()
    service = CatalogService({CatalogSource.JIKAN: provider})
    candidate = RecommendationCandidate(title="Cowboy Bebop", year=1998)

    anime = asyncio.run(service.resolve_candidate(candidate))

    assert provider.candidate == candidate
    assert anime is not None
    assert anime.title == "Cowboy Bebop"


def test_catalog_service_reports_missing_provider() -> None:
    service = CatalogService({CatalogSource.JIKAN: RecordingProvider()})

    with pytest.raises(CatalogProviderError) as exc_info:
        asyncio.run(service.search("bebop", source="unknown"))  # type: ignore[arg-type]

    assert exc_info.value.error.code is CatalogErrorCode.NOT_IMPLEMENTED


def test_catalog_service_preserves_provider_error_payload() -> None:
    service = CatalogService({CatalogSource.JIKAN: FailingProvider()})

    with pytest.raises(CatalogProviderError) as exc_info:
        asyncio.run(service.search("bebop"))

    assert exc_info.value.error.code is CatalogErrorCode.RATE_LIMITED
    assert exc_info.value.error.retry_after_seconds == 5
