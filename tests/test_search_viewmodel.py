from __future__ import annotations

import asyncio

import pytest

from anicompass.catalog import (
    CatalogAnime,
    CatalogAnimeId,
    CatalogError,
    CatalogErrorCode,
    CatalogProviderError,
    CatalogSearchResult,
    CatalogSource,
)
from anicompass.search import SearchStatus, SearchViewModel


class SearchServiceDouble:
    def __init__(self, result: CatalogSearchResult | None = None) -> None:
        self.result = result or CatalogSearchResult(
            items=(), source=CatalogSource.JIKAN, query=""
        )
        self.calls: list[tuple[str, int, bool]] = []

    async def search(
        self,
        query: str,
        *,
        limit: int = 10,
        safe_for_all_audiences: bool = True,
    ) -> CatalogSearchResult:
        self.calls.append((query, limit, safe_for_all_audiences))
        return self.result.model_copy(update={"query": query})


class FailingSearchService(SearchServiceDouble):
    async def search(
        self,
        query: str,
        *,
        limit: int = 10,
        safe_for_all_audiences: bool = True,
    ) -> CatalogSearchResult:
        self.calls.append((query, limit, safe_for_all_audiences))
        raise CatalogProviderError(
            CatalogError(code=CatalogErrorCode.RATE_LIMITED, message="Rate limited.")
        )


class UnexpectedFailingSearchService(SearchServiceDouble):
    async def search(
        self,
        query: str,
        *,
        limit: int = 10,
        safe_for_all_audiences: bool = True,
    ) -> CatalogSearchResult:
        self.calls.append((query, limit, safe_for_all_audiences))
        raise ValueError("boom")


def _anime() -> CatalogAnime:
    return CatalogAnime(
        catalog_id=CatalogAnimeId(source=CatalogSource.JIKAN, provider_id="1"),
        title="Cowboy Bebop",
    )


def test_search_view_model_initial_state_and_reset() -> None:
    view_model = SearchViewModel(SearchServiceDouble())

    assert view_model.state.status is SearchStatus.IDLE
    assert view_model.state.items == ()

    asyncio.run(view_model.search("bebop"))
    state = view_model.reset()

    assert state.status is SearchStatus.IDLE
    assert state.query == ""
    assert state.items == ()


def test_search_view_model_success_state_trims_query_and_passes_options() -> None:
    service = SearchServiceDouble(
        CatalogSearchResult(items=(_anime(),), source=CatalogSource.JIKAN, query="")
    )
    view_model = SearchViewModel(service)

    state = asyncio.run(
        view_model.search("  bebop  ", limit=3, safe_for_all_audiences=False)
    )

    assert service.calls == [("bebop", 3, False)]
    assert state.status is SearchStatus.SUCCESS
    assert state.query == "bebop"
    assert state.items[0].title == "Cowboy Bebop"
    assert state.selected_item is not None
    assert state.selected_item.title == "Cowboy Bebop"
    assert state.is_busy is False


def test_search_view_model_empty_state() -> None:
    view_model = SearchViewModel(SearchServiceDouble())

    state = asyncio.run(view_model.search("unknown"))

    assert state.status is SearchStatus.EMPTY
    assert state.items == ()
    assert state.error is None


def test_search_view_model_error_state_preserves_catalog_error() -> None:
    view_model = SearchViewModel(FailingSearchService())

    state = asyncio.run(view_model.search("bebop"))

    assert state.status is SearchStatus.ERROR
    assert state.error is not None
    assert state.error.code is CatalogErrorCode.RATE_LIMITED
    assert state.items == ()


def test_search_view_model_rejects_duplicate_submission_while_busy() -> None:
    service = SearchServiceDouble()
    view_model = SearchViewModel(service)
    view_model._state = view_model.state.model_copy(update={"is_busy": True})

    state = asyncio.run(view_model.search("bebop"))

    assert state.is_busy is True
    assert service.calls == []


def test_search_view_model_wraps_unexpected_errors() -> None:
    view_model = SearchViewModel(UnexpectedFailingSearchService())

    with pytest.raises(RuntimeError):
        asyncio.run(view_model.search("bebop"))

    assert view_model.state.status is SearchStatus.ERROR
    assert view_model.state.error is not None
    assert view_model.state.error.code is CatalogErrorCode.PROVIDER_ERROR


def test_search_view_model_selects_and_clears_result_by_provider_id() -> None:
    first = _anime()
    second = CatalogAnime(
        catalog_id=CatalogAnimeId(source=CatalogSource.JIKAN, provider_id="2"),
        title="Samurai Champloo",
    )
    service = SearchServiceDouble(
        CatalogSearchResult(items=(first, second), source=CatalogSource.JIKAN, query="")
    )
    view_model = SearchViewModel(service)

    asyncio.run(view_model.search("shinichiro watanabe"))
    selected = view_model.select_result("2")

    assert selected.selected_item is not None
    assert selected.selected_item.title == "Samurai Champloo"

    cleared = view_model.clear_selection()

    assert cleared.selected_item is None
