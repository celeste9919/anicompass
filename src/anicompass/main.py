"""AniCompass PySide6/QML application entry point."""

from __future__ import annotations

import argparse
import os
import sqlite3
import sys
import tempfile
from pathlib import Path

from PySide6.QtCore import QCoreApplication, QObject, QStandardPaths, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from anicompass.ai import (
    AIConfigBridge,
    CredentialService,
    OpenAICompatibleChatClient,
    default_provider_configs,
)
from anicompass.backup import BackupBridge, BackupService
from anicompass.catalog import CatalogService, CatalogSource, JikanCatalogProvider
from anicompass.history import HistoryBridge, HistoryService, SQLiteHistoryRepository
from anicompass.recommendation import RecommendationOrchestrator
from anicompass.recommendation.bridge import RecommendBridge
from anicompass.search.bridge import SearchBridge
from anicompass.search.viewmodel import SearchViewModel
from anicompass.settings import SettingsService
from anicompass.watchlist import (
    SQLiteWatchListRepository,
    WatchListBridge,
    WatchListService,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def bundled_path(relative_path: str) -> Path:
    """Return a path that works both from source and from a PyInstaller bundle."""
    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root:
        return Path(bundle_root) / relative_path
    return PROJECT_ROOT / relative_path


MAIN_QML = bundled_path("src/anicompass/ui/Main.qml")


def configure_application_metadata() -> None:
    QCoreApplication.setOrganizationName("AniCompass")
    QCoreApplication.setApplicationName("AniCompass")
    QCoreApplication.setApplicationVersion("0.0.1")


def resolve_config_dir() -> Path:
    override = os.environ.get("ANICOMPASS_CONFIG_DIR")
    if override:
        return Path(override)
    location = QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.AppConfigLocation
    )
    return Path(location) if location else Path.cwd()


def create_catalog_service() -> CatalogService:
    provider = JikanCatalogProvider()
    return CatalogService({CatalogSource.JIKAN: provider})


def create_recommend_bridge(parent: QObject | None = None) -> RecommendBridge:
    credential_service = CredentialService()
    orchestrator = RecommendationOrchestrator(
        OpenAICompatibleChatClient(credential_service),
        create_catalog_service(),
    )
    return RecommendBridge(
        orchestrator,
        default_provider_configs()[0],
        parent=parent,
        history_service=create_history_service(),
    )


def create_search_bridge(parent: QObject | None = None) -> SearchBridge:
    service = create_catalog_service()
    return SearchBridge(SearchViewModel(service), parent=parent)


def create_sqlite_path(filename: str = "anicompass.db") -> Path:
    config_dir = resolve_config_dir()
    try:
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / filename
    except OSError:
        fallback_dir = Path(tempfile.gettempdir()) / "AniCompass"
        fallback_dir.mkdir(parents=True, exist_ok=True)
        return fallback_dir / filename


def create_history_service() -> HistoryService:
    try:
        repository = SQLiteHistoryRepository(create_sqlite_path())
    except sqlite3.Error:
        fallback_dir = Path(tempfile.gettempdir()) / "AniCompass"
        fallback_dir.mkdir(parents=True, exist_ok=True)
        repository = SQLiteHistoryRepository(fallback_dir / "anicompass.db")
    return HistoryService(repository)


def create_backup_bridge(parent: QObject | None = None) -> BackupBridge:
    return BackupBridge(BackupService(create_sqlite_path()), parent=parent)


def create_history_bridge(parent: QObject | None = None) -> HistoryBridge:
    return HistoryBridge(create_history_service(), parent=parent)


def create_ai_config_bridge(parent: QObject | None = None) -> AIConfigBridge:
    return AIConfigBridge(CredentialService(), parent=parent)


def create_watchlist_bridge(parent: QObject | None = None) -> WatchListBridge:
    try:
        repository = SQLiteWatchListRepository(create_sqlite_path())
    except sqlite3.Error:
        fallback_dir = Path(tempfile.gettempdir()) / "AniCompass"
        fallback_dir.mkdir(parents=True, exist_ok=True)
        repository = SQLiteWatchListRepository(fallback_dir / "anicompass.db")
    return WatchListBridge(WatchListService(repository), parent=parent)


def create_engine(
    qml_path: Path = MAIN_QML,
    *,
    search_bridge: SearchBridge | None = None,
    watchlist_bridge: WatchListBridge | None = None,
    ai_config_bridge: AIConfigBridge | None = None,
    recommend_bridge: RecommendBridge | None = None,
    history_bridge: HistoryBridge | None = None,
    backup_bridge: BackupBridge | None = None,
) -> QQmlApplicationEngine:
    """Load the root QML file and fail loudly if it cannot be created."""
    engine = QQmlApplicationEngine()
    settings_service = SettingsService(parent=engine)
    bridge = search_bridge or create_search_bridge(parent=engine)
    list_bridge = watchlist_bridge or create_watchlist_bridge(parent=engine)
    ai_bridge = ai_config_bridge or create_ai_config_bridge(parent=engine)
    rec_bridge = recommend_bridge or create_recommend_bridge(parent=engine)
    hist_bridge = history_bridge or create_history_bridge(parent=engine)
    backup = backup_bridge or create_backup_bridge(parent=engine)
    backup.restoreCompleted.connect(list_bridge.stateChanged.emit)
    backup.restoreCompleted.connect(hist_bridge.notifyChanged)
    engine.rootContext().setContextProperty("settingsService", settings_service)
    engine.rootContext().setContextProperty("searchBridge", bridge)
    engine.rootContext().setContextProperty("watchListBridge", list_bridge)
    engine.rootContext().setContextProperty("aiConfigBridge", ai_bridge)
    engine.rootContext().setContextProperty("recommendBridge", rec_bridge)
    engine.rootContext().setContextProperty("historyBridge", hist_bridge)
    engine.rootContext().setContextProperty("backupBridge", backup)
    engine.load(QUrl.fromLocalFile(str(qml_path)))
    if not engine.rootObjects():
        raise RuntimeError(f"QML root failed to load: {qml_path}")
    return engine


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Launch AniCompass.")
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="Load QML and exit without entering the GUI event loop.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    configure_application_metadata()
    app = QGuiApplication(sys.argv[:1])

    # Smoke tests verify the QML shell loads before business features are added.
    create_engine()

    if args.smoke_test:
        return 0
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
