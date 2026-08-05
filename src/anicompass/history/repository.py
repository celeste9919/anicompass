"""SQLite repository for recommendation history."""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from types import TracebackType

from anicompass.history.models import RecommendationHistorySession

HISTORY_LIMIT = 10


class HistorySessionNotFoundError(Exception):
    """Raised when a history session id cannot be found."""


class SQLiteHistoryRepository:
    """Persist recent recommendation sessions in SQLite."""

    def __init__(self, database_path: Path | str = ":memory:") -> None:
        self._database_path = str(database_path)
        self._connection = sqlite3.connect(self._database_path)
        self._connection.row_factory = sqlite3.Row
        self.migrate()

    def __enter__(self) -> SQLiteHistoryRepository:
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
            self._connection.execute(
                """
                CREATE TABLE IF NOT EXISTS recommendation_history_sessions (
                    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    preferences TEXT NOT NULL,
                    language TEXT NOT NULL,
                    verified_count INTEGER NOT NULL,
                    unresolved_count INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    def save(
        self,
        session: RecommendationHistorySession,
    ) -> RecommendationHistorySession:
        with self._connection:
            cursor = self._connection.execute(
                """
                INSERT INTO recommendation_history_sessions (
                    preferences, language, verified_count, unresolved_count, created_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    session.preferences,
                    session.language,
                    session.verified_count,
                    session.unresolved_count,
                    session.created_at.isoformat(),
                ),
            )
            self._trim_old_sessions()
        return session.model_copy(update={"session_id": int(cursor.lastrowid)})

    def list_sessions(self) -> tuple[RecommendationHistorySession, ...]:
        rows = self._connection.execute(
            """
            SELECT * FROM recommendation_history_sessions
            ORDER BY created_at DESC, session_id DESC
            """
        ).fetchall()
        return tuple(self._from_row(row) for row in rows)

    def delete(self, session_id: int) -> None:
        with self._connection:
            cursor = self._connection.execute(
                "DELETE FROM recommendation_history_sessions WHERE session_id = ?",
                (session_id,),
            )
        if cursor.rowcount == 0:
            raise HistorySessionNotFoundError(str(session_id))

    def _trim_old_sessions(self) -> None:
        self._connection.execute(
            """
            DELETE FROM recommendation_history_sessions
            WHERE session_id NOT IN (
                SELECT session_id FROM recommendation_history_sessions
                ORDER BY created_at DESC, session_id DESC
                LIMIT ?
            )
            """,
            (HISTORY_LIMIT,),
        )

    def _from_row(self, row: sqlite3.Row) -> RecommendationHistorySession:
        return RecommendationHistorySession(
            session_id=int(row["session_id"]),
            preferences=row["preferences"],
            language=row["language"],
            verified_count=int(row["verified_count"]),
            unresolved_count=int(row["unresolved_count"]),
            created_at=datetime.fromisoformat(row["created_at"]).astimezone(UTC),
        )
