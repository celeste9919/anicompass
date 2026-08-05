"""Local backup and restore service."""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from pydantic import ValidationError

from anicompass.backup.models import (
    AniCompassBackup,
    BackupHistorySession,
    BackupWatchListItem,
)
from anicompass.history.repository import SQLiteHistoryRepository
from anicompass.watchlist.repository import SQLiteWatchListRepository


class BackupError(Exception):
    """Base class for backup failures."""


class BackupValidationError(BackupError):
    """Raised when a backup file cannot be trusted for import."""


class BackupIOError(BackupError):
    """Raised when a backup file cannot be read or written."""


class BackupService:
    """Export and restore local user data without secrets."""

    def __init__(self, database_path: Path | str) -> None:
        self._database_path = str(database_path)
        self._ensure_schema()

    def export_backup(self, output_path: Path | str) -> AniCompassBackup:
        backup = self.build_backup()
        path = Path(output_path)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                backup.model_dump_json(indent=2),
                encoding="utf-8",
                newline="\n",
            )
        except OSError as exc:
            raise BackupIOError(str(exc)) from exc
        return backup

    def build_backup(self) -> AniCompassBackup:
        with self._connect() as connection:
            watch_items = tuple(
                self._watch_item_from_row(row)
                for row in connection.execute(
                    """
                    SELECT * FROM watch_list_items
                    ORDER BY updated_at DESC, item_id DESC
                    """
                ).fetchall()
            )
            history_sessions = tuple(
                self._history_session_from_row(row)
                for row in connection.execute(
                    """
                    SELECT * FROM recommendation_history_sessions
                    ORDER BY created_at DESC, session_id DESC
                    """
                ).fetchall()
            )
        return AniCompassBackup(
            watch_list_items=watch_items,
            recommendation_history=history_sessions,
        )

    def inspect_backup(self, backup_path: Path | str) -> AniCompassBackup:
        path = Path(backup_path)
        try:
            payload = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise BackupIOError(str(exc)) from exc
        try:
            return AniCompassBackup.model_validate_json(payload)
        except (ValidationError, ValueError, json.JSONDecodeError) as exc:
            raise BackupValidationError("Invalid AniCompass backup file.") from exc

    def import_backup(self, backup_path: Path | str) -> AniCompassBackup:
        backup = self.inspect_backup(backup_path)
        with self._connect() as connection:
            try:
                connection.execute("BEGIN")
                connection.execute("DELETE FROM watch_list_items")
                connection.execute("DELETE FROM recommendation_history_sessions")
                connection.executemany(
                    """
                    INSERT INTO watch_list_items (
                        item_id, catalog_source, provider_id, title, original_title,
                        image_url, source_url, status, progress, score, notes,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        self._watch_item_to_values(item)
                        for item in backup.watch_list_items
                    ],
                )
                connection.executemany(
                    """
                    INSERT INTO recommendation_history_sessions (
                        session_id, preferences, language, verified_count,
                        unresolved_count, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    [
                        self._history_session_to_values(session)
                        for session in backup.recommendation_history
                    ],
                )
            except sqlite3.Error as exc:
                connection.rollback()
                raise BackupValidationError(
                    "Backup import failed; existing data kept."
                ) from exc
            else:
                connection.commit()
        return backup

    def _ensure_schema(self) -> None:
        watch_repo = SQLiteWatchListRepository(self._database_path)
        watch_repo.close()
        history_repo = SQLiteHistoryRepository(self._database_path)
        history_repo.close()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _watch_item_from_row(self, row: sqlite3.Row) -> BackupWatchListItem:
        return BackupWatchListItem(
            item_id=int(row["item_id"]),
            catalog_source=row["catalog_source"],
            provider_id=row["provider_id"],
            title=row["title"],
            original_title=row["original_title"],
            image_url=row["image_url"],
            source_url=row["source_url"],
            status=row["status"],
            progress=int(row["progress"]),
            score=row["score"],
            notes=row["notes"],
            created_at=datetime.fromisoformat(row["created_at"]).astimezone(UTC),
            updated_at=datetime.fromisoformat(row["updated_at"]).astimezone(UTC),
        )

    def _history_session_from_row(self, row: sqlite3.Row) -> BackupHistorySession:
        return BackupHistorySession(
            session_id=int(row["session_id"]),
            preferences=row["preferences"],
            language=row["language"],
            verified_count=int(row["verified_count"]),
            unresolved_count=int(row["unresolved_count"]),
            created_at=datetime.fromisoformat(row["created_at"]).astimezone(UTC),
        )

    def _watch_item_to_values(self, item: BackupWatchListItem) -> tuple[object, ...]:
        return (
            item.item_id,
            item.catalog_source,
            item.provider_id,
            item.title,
            item.original_title,
            item.image_url,
            item.source_url,
            item.status,
            item.progress,
            item.score,
            item.notes,
            item.created_at.isoformat(),
            item.updated_at.isoformat(),
        )

    def _history_session_to_values(
        self,
        session: BackupHistorySession,
    ) -> tuple[object, ...]:
        return (
            session.session_id,
            session.preferences,
            session.language,
            session.verified_count,
            session.unresolved_count,
            session.created_at.isoformat(),
        )

