"""Catalog provider contracts for AniCompass."""

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
from anicompass.catalog.provider import (
    CatalogProvider,
    JikanCatalogProvider,
    JikanRateLimiter,
)
from anicompass.catalog.service import CatalogService

__all__ = [
    "CatalogAnime",
    "CatalogAnimeId",
    "CatalogError",
    "CatalogErrorCode",
    "CatalogFilters",
    "CatalogProvider",
    "CatalogProviderError",
    "CatalogSearchResult",
    "CatalogService",
    "CatalogSource",
    "JikanCatalogProvider",
    "JikanRateLimiter",
    "RecommendationCandidate",
]
