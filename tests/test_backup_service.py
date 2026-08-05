from __future__ import annotations

import json

import pytest

from anicompass.backup import BackupService, BackupValidationError
from anicompass.catalog import CatalogAnime, CatalogAnimeId, CatalogSource
from anicompass.history import HistoryService, SQLiteHistoryRepository
from anicompass.recommendation.models import (
    RecommendationRequest,
    RecommendationResult,
    VerifiedRecommendation,
)
from anicompass.watchlist import SQLiteWatchListRepository, WatchListService


def _anime(provider_id: str = "1", title: str = "Cowboy Bebop") -> CatalogAnime:
    return CatalogAnime(
        catalog_id=CatalogAnimeId(source=CatalogSource.JIKAN, provider_id=provider_id),
        title=title,
        original_title=title,
        source_url="https://example.com/anime/1",
    )


def _recommendation_result() -> RecommendationResult:
    return RecommendationResult(
        items=(
            VerifiedRecommendation(
                anime=_anime(),
                reason="Fits the mood.",
            ),
        )
    )


def _seed_database(database_path) -> None:
    watch_repository = SQLiteWatchListRepository(database_path)
    history_repository = SQLiteHistoryRepository(database_path)
    try:
        WatchListService(watch_repository).add_anime(_anime())
        HistoryService(history_repository).save_result(
            RecommendationRequest(preferences="space jazz noir"),
            _recommendation_result(),
        )
    finally:
        watch_repository.close()
        history_repository.close()


def test_backup_service_exports_versioned_user_data_without_secrets(tmp_path) -> None:
    database_path = tmp_path / "anicompass.db"
    backup_path = tmp_path / "backup.json"
    _seed_database(database_path)

    backup = BackupService(database_path).export_backup(backup_path)
    payload = json.loads(backup_path.read_text(encoding="utf-8"))

    assert backup.format_version == 1
    assert payload["app"] == "AniCompass"
    assert payload["watch_list_items"][0]["title"] == "Cowboy Bebop"
    assert payload["recommendation_history"][0]["preferences"] == "space jazz noir"
    serialized = backup_path.read_text(encoding="utf-8").lower()
    assert "api_key" not in serialized
    assert "apikey" not in serialized
    assert "authorization" not in serialized
    assert "secret" not in serialized


def test_backup_service_restores_backup_into_new_database(tmp_path) -> None:
    source_database = tmp_path / "source.db"
    target_database = tmp_path / "target.db"
    backup_path = tmp_path / "backup.json"
    _seed_database(source_database)
    BackupService(source_database).export_backup(backup_path)

    BackupService(target_database).import_backup(backup_path)

    watch_repository = SQLiteWatchListRepository(target_database)
    history_repository = SQLiteHistoryRepository(target_database)
    try:
        watch_items = WatchListService(watch_repository).list_items()
        sessions = HistoryService(history_repository).list_sessions()
    finally:
        watch_repository.close()
        history_repository.close()

    assert len(watch_items) == 1
    assert watch_items[0].title == "Cowboy Bebop"
    assert len(sessions) == 1
    assert sessions[0].verified_count == 1


def test_backup_service_rejects_malformed_backup_without_changing_data(
    tmp_path,
) -> None:
    database_path = tmp_path / "anicompass.db"
    backup_path = tmp_path / "broken.json"
    _seed_database(database_path)
    backup_path.write_text(
        '{"app":"AniCompass","format_version":999}',
        encoding="utf-8",
    )

    with pytest.raises(BackupValidationError):
        BackupService(database_path).import_backup(backup_path)

    repository = SQLiteWatchListRepository(database_path)
    try:
        assert len(WatchListService(repository).list_items()) == 1
    finally:
        repository.close()


def test_backup_service_rolls_back_when_restore_violates_sqlite_constraints(
    tmp_path,
) -> None:
    database_path = tmp_path / "anicompass.db"
    valid_backup_path = tmp_path / "valid.json"
    broken_backup_path = tmp_path / "duplicate.json"
    _seed_database(database_path)
    service = BackupService(database_path)
    service.export_backup(valid_backup_path)
    payload = json.loads(valid_backup_path.read_text(encoding="utf-8"))
    payload["watch_list_items"].append(payload["watch_list_items"][0])
    broken_backup_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(BackupValidationError):
        service.import_backup(broken_backup_path)

    repository = SQLiteWatchListRepository(database_path)
    try:
        items = WatchListService(repository).list_items()
    finally:
        repository.close()
    assert len(items) == 1
    assert items[0].title == "Cowboy Bebop"

