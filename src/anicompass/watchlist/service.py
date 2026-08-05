"""Business service for local watch-list actions."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Protocol

from anicompass.catalog.models import CatalogAnime
from anicompass.watchlist.models import WatchListFilter, WatchListItem, WatchListUpdate
from anicompass.watchlist.repository import SQLiteWatchListRepository


class WatchListRepository(Protocol):
    def add(self, item: WatchListItem) -> WatchListItem: ...
    def get(self, item_id: int) -> WatchListItem: ...
    def find_by_catalog_id(self, catalog_id) -> WatchListItem | None: ...
    def list_items(
        self,
        item_filter: WatchListFilter | None = None,
    ) -> tuple[WatchListItem, ...]: ...
    def update(self, item: WatchListItem) -> WatchListItem: ...
    def remove(self, item_id: int) -> None: ...


class WatchListService:
    """Validate user-owned watch-list flow and delegate persistence."""

    def __init__(self, repository: WatchListRepository) -> None:
        self._repository = repository

    @classmethod
    def from_sqlite(cls, database_path: str) -> WatchListService:
        return cls(SQLiteWatchListRepository(database_path))

    def add_anime(self, anime: CatalogAnime) -> WatchListItem:
        now = datetime.now(UTC)
        item = WatchListItem(
            catalog_id=anime.catalog_id,
            title=anime.title,
            original_title=anime.original_title,
            image_url=str(anime.image_url) if anime.image_url else None,
            source_url=str(anime.source_url) if anime.source_url else None,
            created_at=now,
            updated_at=now,
        )
        return self._repository.add(item)

    def update_item(self, item_id: int, patch: WatchListUpdate) -> WatchListItem:
        current = self._repository.get(item_id)
        update_values = patch.model_dump(exclude_unset=True)
        if not update_values:
            return current
        update_values["updated_at"] = datetime.now(UTC)
        return self._repository.update(current.model_copy(update=update_values))

    def list_items(
        self,
        item_filter: WatchListFilter | None = None,
    ) -> tuple[WatchListItem, ...]:
        return self._repository.list_items(item_filter)

    def remove_item(self, item_id: int) -> None:
        self._repository.remove(item_id)
