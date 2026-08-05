"""Catalog service layer for provider-neutral catalog operations."""

from __future__ import annotations

from collections.abc import Mapping

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
from anicompass.catalog.provider import CatalogProvider


class CatalogService:
    """Coordinate catalog providers without exposing provider details to UI."""

    def __init__(
        self,
        providers: Mapping[CatalogSource, CatalogProvider],
        *,
        default_source: CatalogSource = CatalogSource.JIKAN,
    ) -> None:
        self._providers = dict(providers)
        self._default_source = default_source
        if default_source not in self._providers:
            raise ValueError(f"Default catalog provider is missing: {default_source}")

    async def search(
        self,
        query: str,
        *,
        limit: int = 10,
        safe_for_all_audiences: bool = True,
        source: CatalogSource | None = None,
    ) -> CatalogSearchResult:
        filters = self._build_filters(
            query=query,
            limit=limit,
            safe_for_all_audiences=safe_for_all_audiences,
        )
        return await self._provider(source).search(filters)

    async def get_by_id(self, catalog_id: CatalogAnimeId) -> CatalogAnime:
        return await self._provider(catalog_id.source).get_by_id(catalog_id)

    async def resolve_candidate(
        self,
        candidate: RecommendationCandidate,
        *,
        source: CatalogSource | None = None,
    ) -> CatalogAnime | None:
        return await self._provider(source).resolve_candidate(candidate)

    def _provider(self, source: CatalogSource | None) -> CatalogProvider:
        selected_source = source or self._default_source
        provider = self._providers.get(selected_source)
        if provider is None:
            raise CatalogProviderError(
                CatalogError(
                    code=CatalogErrorCode.NOT_IMPLEMENTED,
                    message=f"Catalog provider is not configured: {selected_source}",
                )
            )
        return provider

    def _build_filters(
        self,
        *,
        query: str,
        limit: int,
        safe_for_all_audiences: bool,
    ) -> CatalogFilters:
        try:
            return CatalogFilters(
                query=query.strip(),
                limit=limit,
                safe_for_all_audiences=safe_for_all_audiences,
            )
        except ValidationError as exc:
            raise CatalogProviderError(
                CatalogError(
                    code=CatalogErrorCode.INVALID_REQUEST,
                    message="Catalog search input is invalid.",
                )
            ) from exc
