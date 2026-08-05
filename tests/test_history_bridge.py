from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QGuiApplication

from anicompass.history import HistoryBridge, HistoryService, SQLiteHistoryRepository
from anicompass.history.models import RecommendationHistorySession

PROJECT_ROOT = Path(__file__).resolve().parents[1]
QML_PATH = PROJECT_ROOT / "src" / "anicompass" / "ui" / "Main.qml"


def _app() -> QGuiApplication:
    app = QGuiApplication.instance()
    if app is None:
        QCoreApplication.setOrganizationName("AniCompassTests")
        QCoreApplication.setApplicationName("AniCompassHistoryBridge")
        app = QGuiApplication([])
    return app


def _bridge() -> HistoryBridge:
    repository = SQLiteHistoryRepository()
    service = HistoryService(repository)
    service._repository.save(
        RecommendationHistorySession(
            preferences="space jazz noir",
            language="en",
            verified_count=1,
            unresolved_count=0,
        )
    )
    return HistoryBridge(service)


def test_history_bridge_lists_and_deletes_sessions() -> None:
    bridge = _bridge()

    assert bridge.property("sessionCount") == 1
    assert bridge.property("sessions")[0]["preferences"] == "space jazz noir"

    bridge.deleteSession(bridge.property("sessions")[0]["sessionId"])

    assert bridge.property("sessionCount") == 0


def test_qml_declares_history_controls() -> None:
    qml_text = QML_PATH.read_text(encoding="utf-8-sig")

    assert 'objectName: "historyStatusText"' in qml_text
    assert 'objectName: "historyResultsList"' in qml_text
    assert "historyBridge.sessions" in qml_text
    assert "historyBridge.deleteSession" in qml_text
