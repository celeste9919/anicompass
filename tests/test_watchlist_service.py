from __future__ import annotations

import pytest
from pydantic import ValidationError

from anicompass.catalog import CatalogAnime, CatalogAnimeId, CatalogSource
from anicompass.watchlist import (
    DuplicateWatchListItemError,
    SQLiteWatchListRepository,
    WatchListFilter,
    WatchListItemNotFoundError,
    WatchListService,
    WatchListUpdate,
    WatchStatus,
)


def _anime(provider_id: str = "1", title: str = "Cowboy Bebop") -> CatalogAnime:
    return CatalogAnime(
        catalog_id=CatalogAnimeId(source=CatalogSource.JIKAN, provider_id=provider_id),
        title=title,
        original_title="Cowboy Bebop",
    )


def test_watchlist_repository_migrates_schema() -> None:
    repository = SQLiteWatchListRepository()

    assert repository.schema_version() == 1
    repository.close()


def test_watchlist_service_adds_and_reloads_item_from_sqlite(tmp_path) -> None:
    database_path = tmp_path / "anicompass.db"
    repository = SQLiteWatchListRepository(database_path)
    service = WatchListService(repository)

    created = service.add_anime(_anime())
    repository.close()

    reloaded_repository = SQLiteWatchListRepository(database_path)
    try:
        items = WatchListService(reloaded_repository).list_items()

        assert created.item_id is not None
        assert len(items) == 1
        assert items[0].title == "Cowboy Bebop"
        assert items[0].status is WatchStatus.PLAN_TO_WATCH
    finally:
        reloaded_repository.close()


def test_watchlist_repository_prevents_duplicate_catalog_items() -> None:
    repository = SQLiteWatchListRepository()
    service = WatchListService(repository)

    service.add_anime(_anime())

    with pytest.raises(DuplicateWatchListItemError):
        service.add_anime(_anime())

    repository.close()


def test_watchlist_service_updates_status_progress_score_and_notes() -> None:
    repository = SQLiteWatchListRepository()
    service = WatchListService(repository)
    created = service.add_anime(_anime())

    updated = service.update_item(
        created.item_id or 0,
        WatchListUpdate(
            status=WatchStatus.WATCHING,
            progress=12,
            score=9,
            notes="Great soundtrack.",
        ),
    )

    assert updated.status is WatchStatus.WATCHING
    assert updated.progress == 12
    assert updated.score == 9
    assert updated.notes == "Great soundtrack."
    assert updated.updated_at >= created.updated_at
    repository.close()


def test_watchlist_service_filters_by_status() -> None:
    repository = SQLiteWatchListRepository()
    service = WatchListService(repository)
    first = service.add_anime(_anime("1", "Cowboy Bebop"))
    service.add_anime(_anime("2", "Samurai Champloo"))
    service.update_item(
        first.item_id or 0,
        WatchListUpdate(status=WatchStatus.COMPLETED),
    )

    completed = service.list_items(WatchListFilter(status=WatchStatus.COMPLETED))

    assert [item.title for item in completed] == ["Cowboy Bebop"]
    repository.close()


def test_watchlist_update_rejects_invalid_progress_and_score() -> None:
    with pytest.raises(ValidationError):
        WatchListUpdate(progress=-1)

    with pytest.raises(ValidationError):
        WatchListUpdate(score=11)


def test_watchlist_service_removes_items() -> None:
    repository = SQLiteWatchListRepository()
    service = WatchListService(repository)
    created = service.add_anime(_anime())

    service.remove_item(created.item_id or 0)

    with pytest.raises(WatchListItemNotFoundError):
        repository.get(created.item_id or 0)
    repository.close()
