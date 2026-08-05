from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from anicompass.backup import BackupBridge, BackupService
from anicompass.catalog import CatalogAnime, CatalogAnimeId, CatalogSource
from anicompass.watchlist import SQLiteWatchListRepository, WatchListService

PROJECT_ROOT = Path(__file__).resolve().parents[1]
QML_PATH = PROJECT_ROOT / "src" / "anicompass" / "ui" / "Main.qml"


def _anime() -> CatalogAnime:
    return CatalogAnime(
        catalog_id=CatalogAnimeId(source=CatalogSource.JIKAN, provider_id="1"),
        title="Cowboy Bebop",
    )


def _seed_watch_item(database_path: Path) -> None:
    repository = SQLiteWatchListRepository(database_path)
    try:
        WatchListService(repository).add_anime(_anime())
    finally:
        repository.close()


def test_backup_bridge_exports_and_imports_local_file_url(tmp_path) -> None:
    source_database = tmp_path / "source.db"
    target_database = tmp_path / "target.db"
    backup_path = tmp_path / "backup.json"
    _seed_watch_item(source_database)

    source_bridge = BackupBridge(BackupService(source_database))
    source_bridge.exportBackup(backup_path.as_uri())

    assert source_bridge.property("status") == "exported"
    assert source_bridge.property("lastWatchCount") == 1

    target_bridge = BackupBridge(BackupService(target_database))
    restored = []
    target_bridge.restoreCompleted.connect(lambda: restored.append(True))
    target_bridge.importBackup(backup_path.as_uri())

    assert target_bridge.property("status") == "imported"
    assert target_bridge.property("lastWatchCount") == 1
    assert restored == [True]


def test_backup_bridge_reports_invalid_backup(tmp_path) -> None:
    database_path = tmp_path / "anicompass.db"
    backup_path = tmp_path / "broken.json"
    backup_path.write_text(
        '{"app":"AniCompass","format_version":999}',
        encoding="utf-8",
    )

    bridge = BackupBridge(BackupService(database_path))
    bridge.importBackup(str(backup_path))

    assert bridge.property("status") == "error"
    assert bridge.property("errorCode") == "invalid_backup"
    assert "保留" in bridge.copyForStatus("zh")


def test_qml_declares_backup_controls() -> None:
    qml_text = QML_PATH.read_text(encoding="utf-8-sig")

    assert 'import QtQuick.Dialogs' in qml_text
    assert 'objectName: "exportBackupButton"' in qml_text
    assert 'objectName: "importBackupButton"' in qml_text
    assert 'objectName: "backupStatusText"' in qml_text
    assert 'objectName: "exportBackupDialog"' in qml_text
    assert 'objectName: "importBackupDialog"' in qml_text
    assert 'backupBridge.exportBackup' in qml_text
    assert 'backupBridge.importBackup' in qml_text
