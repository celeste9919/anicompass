"""SQLite repository for the local watch list."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from types import TracebackType

from anicompass.catalog.models import CatalogAnimeId
from anicompass.watchlist.models import WatchListFilter, WatchListItem, WatchStatus

SCHEMA_VERSION = 1


class DuplicateWatchListItemError(Exception):
    """Raised when the same provider item is added twice."""


class WatchListItemNotFoundError(Exception):
    """Raised when an item id cannot be found."""


class SQLiteWatchListRepository:
    """Persist watch-list records in a small local SQLite database."""

    def __init__(self, database_path: Path | str = ":memory:") -> None:
        self._database_path = str(database_path)
        self._connection = sqlite3.connect(self._database_path)
        self._connection.row_factory = sqlite3.Row
        self.migrate()

    def __enter__(self) -> SQLiteWatchListRepository:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    def close(self) -> None:
        self._connection.close()

    def migrate(self) -> None:
        with self._connection:
            self._connection.execute("PRAGMA foreign_keys = ON")
            self._connection.execute("PRAGMA user_version = 1")
            self._connection.execute(
                """
                CREATE TABLE IF NOT EXISTS watch_list_items (
                    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    catalog_source TEXT NOT NULL,
                    provider_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    original_title TEXT,
                    image_url TEXT,
                    source_url TEXT,
                    status TEXT NOT NULL,
                    progress INTEGER NOT NULL DEFAULT 0,
                    score INTEGER,
                    notes TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(catalog_source, provider_id)
                )
                """
            )

    def schema_version(self) -> int:
        row = self._connection.execute("PRAGMA user_version").fetchone()
        return int(row[0])

    def add(self, item: WatchListItem) -> WatchListItem:
        try:
            with self._connection:
                cursor = self._connection.execute(
                    """
                    INSERT INTO watch_list_items (
                        catalog_source, provider_id, title, original_title,
                        image_url, source_url, status, progress, score, notes,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    self._to_row_values(item),
                )
        except sqlite3.IntegrityError as exc:
            raise DuplicateWatchListItemError(item.catalog_id.provider_id) from exc
        return item.model_copy(update={"item_id": int(cursor.lastrowid)})

    def get(self, item_id: int) -> WatchListItem:
        row = self._connection.execute(
            "SELECT * FROM watch_list_items WHERE item_id = ?",
            (item_id,),
        ).fetchone()
        if row is None:
            raise WatchListItemNotFoundError(str(item_id))
        return self._from_row(row)

    def find_by_catalog_id(self, catalog_id: CatalogAnimeId) -> WatchListItem | None:
        row = self._connection.execute(
            """
            SELECT * FROM watch_list_items
            WHERE catalog_source = ? AND provider_id = ?
            """,
            (catalog_id.source.value, catalog_id.provider_id),
        ).fetchone()
        return self._from_row(row) if row else None

    def list_items(
        self,
        item_filter: WatchListFilter | None = None,
    ) -> tuple[WatchListItem, ...]:
        if item_filter and item_filter.status:
            rows: Iterable[sqlite3.Row] = self._connection.execute(
                """
                SELECT * FROM watch_list_items
                WHERE status = ?
                ORDER BY updated_at DESC, item_id DESC
                """,
                (item_filter.status.value,),
            ).fetchall()
        else:
            rows = self._connection.execute(
                """
                SELECT * FROM watch_list_items
                ORDER BY updated_at DESC, item_id DESC
                """
            ).fetchall()
        return tuple(self._from_row(row) for row in rows)

    def update(self, item: WatchListItem) -> WatchListItem:
        if item.item_id is None:
            raise WatchListItemNotFoundError("missing item_id")
        with self._connection:
            cursor = self._connection.execute(
                """
                UPDATE watch_list_items
                SET status = ?, progress = ?, score = ?, notes = ?, updated_at = ?
                WHERE item_id = ?
                """,
                (
                    item.status.value,
                    item.progress,
                    item.score,
                    item.notes,
                    item.updated_at.isoformat(),
                    item.item_id,
                ),
            )
        if cursor.rowcount == 0:
            raise WatchListItemNotFoundError(str(item.item_id))
        return self.get(item.item_id)

    def remove(self, item_id: int) -> None:
        with self._connection:
            cursor = self._connection.execute(
                "DELETE FROM watch_list_items WHERE item_id = ?",
                (item_id,),
            )
        if cursor.rowcount == 0:
            raise WatchListItemNotFoundError(str(item_id))

    def _to_row_values(self, item: WatchListItem) -> tuple[object, ...]:
        return (
            item.catalog_id.source.value,
            item.catalog_id.provider_id,
            item.title,
            item.original_title,
            item.image_url,
            item.source_url,
            item.status.value,
            item.progress,
            item.score,
            item.notes,
            item.created_at.isoformat(),
            item.updated_at.isoformat(),
        )

    def _from_row(self, row: sqlite3.Row) -> WatchListItem:
        return WatchListItem(
            item_id=int(row["item_id"]),
            catalog_id=CatalogAnimeId(
                source=row["catalog_source"],
                provider_id=row["provider_id"],
            ),
            title=row["title"],
            original_title=row["original_title"],
            image_url=row["image_url"],
            source_url=row["source_url"],
            status=WatchStatus(row["status"]),
            progress=int(row["progress"]),
            score=row["score"],
            notes=row["notes"],
            created_at=datetime.fromisoformat(row["created_at"]).astimezone(UTC),
            updated_at=datetime.fromisoformat(row["updated_at"]).astimezone(UTC),
        )
