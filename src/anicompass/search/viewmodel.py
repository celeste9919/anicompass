"""Search screen state and controller boundary."""

from __future__ import annotations

from enum import StrEnum
from typing import Protocol

from pydantic import BaseModel

from anicompass.catalog.models import (
    CatalogAnime,
    CatalogError,
    CatalogErrorCode,
    CatalogProviderError,
    CatalogSearchResult,
)


class SearchStatus(StrEnum):
    """Stable states that the future QML search screen can render."""

    IDLE = "idle"
    LOADING = "loading"
    SUCCESS = "success"
    EMPTY = "empty"
    ERROR = "error"


class SearchViewState(BaseModel):
    """Immutable state snapshot for the Search screen."""

    status: SearchStatus = SearchStatus.IDLE
    query: str = ""
    items: tuple[CatalogAnime, ...] = ()
    selected_item: CatalogAnime | None = None
    error: CatalogError | None = None
    is_busy: bool = False


class CatalogSearchService(Protocol):
    """Small service surface consumed by SearchViewModel."""

    async def search(
        self,
        query: str,
        *,
        limit: int = 10,
        safe_for_all_audiences: bool = True,
    ) -> CatalogSearchResult:
        """Search catalog entries."""


class SearchViewModel:
    """Own Search screen state transitions without UI or provider details."""

    def __init__(self, catalog_service: CatalogSearchService) -> None:
        self._catalog_service = catalog_service
        self._state = SearchViewState()

    @property
    def state(self) -> SearchViewState:
        return self._state

    async def search(
        self,
        query: str,
        *,
        limit: int = 10,
        safe_for_all_audiences: bool = True,
    ) -> SearchViewState:
        trimmed_query = query.strip()
        if self._state.is_busy:
            return self._state
        self._state = SearchViewState(
            status=SearchStatus.LOADING,
            query=trimmed_query,
            is_busy=True,
        )
        try:
            result = await self._catalog_service.search(
                trimmed_query,
                limit=limit,
                safe_for_all_audiences=safe_for_all_audiences,
            )
        except CatalogProviderError as exc:
            self._state = SearchViewState(
                status=SearchStatus.ERROR,
                query=trimmed_query,
                error=exc.error,
            )
            return self._state
        except Exception as exc:
            self._state = SearchViewState(
                status=SearchStatus.ERROR,
                query=trimmed_query,
                error=CatalogError(
                    code=CatalogErrorCode.PROVIDER_ERROR,
                    message="Catalog search failed unexpectedly.",
                ),
            )
            raise RuntimeError("Unexpected catalog search failure.") from exc

        next_status = SearchStatus.SUCCESS if result.items else SearchStatus.EMPTY
        self._state = SearchViewState(
            status=next_status,
            query=result.query,
            items=result.items,
            selected_item=result.items[0] if result.items else None,
        )
        return self._state

    def select_result(self, provider_id: str) -> SearchViewState:
        """Select a result by provider id without leaking list indexes to QML."""

        selected_item = next(
            (
                item
                for item in self._state.items
                if item.catalog_id.provider_id == provider_id
            ),
            self._state.selected_item,
        )
        self._state = self._state.model_copy(update={"selected_item": selected_item})
        return self._state

    def clear_selection(self) -> SearchViewState:
        self._state = self._state.model_copy(update={"selected_item": None})
        return self._state

    def reset(self) -> SearchViewState:
        self._state = SearchViewState()
        return self._state
