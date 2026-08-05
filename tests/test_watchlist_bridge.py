from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QGuiApplication

from anicompass.watchlist import (
    SQLiteWatchListRepository,
    WatchListBridge,
    WatchListService,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
QML_PATH = PROJECT_ROOT / "src" / "anicompass" / "ui" / "Main.qml"


def _app() -> QGuiApplication:
    app = QGuiApplication.instance()
    if app is None:
        QCoreApplication.setOrganizationName("AniCompassTests")
        QCoreApplication.setApplicationName("AniCompassWatchListBridge")
        app = QGuiApplication([])
    return app


def _bridge() -> WatchListBridge:
    return WatchListBridge(WatchListService(SQLiteWatchListRepository()))


def _selected_payload(provider_id: str = "1") -> dict[str, object]:
    return {
        "catalogSource": "jikan",
        "providerId": provider_id,
        "title": "Cowboy Bebop",
        "originalTitle": "Cowboy Bebop",
        "imageUrl": "",
        "sourceUrl": "",
    }


def test_watchlist_bridge_adds_filters_and_removes_selected_catalog_item() -> None:
    bridge = _bridge()

    bridge.addFromCatalogItem(_selected_payload())

    assert bridge.property("itemCount") == 1
    assert bridge.property("items")[0]["title"] == "Cowboy Bebop"

    bridge.setStatusFilter("completed")
    assert bridge.property("statusFilter") == "completed"
    assert bridge.property("itemCount") == 0

    bridge.setStatusFilter("all")
    item_id = bridge.property("items")[0]["itemId"]
    bridge.removeItem(item_id)

    assert bridge.property("itemCount") == 0


def test_watchlist_bridge_updates_item_fields() -> None:
    bridge = _bridge()
    bridge.addFromCatalogItem(_selected_payload())
    item_id = bridge.property("items")[0]["itemId"]

    bridge.updateItem(item_id, "watching", 8, 10, "Comfort episode.")
    item = bridge.property("items")[0]

    assert item["status"] == "watching"
    assert item["progress"] == 8
    assert item["score"] == 10
    assert item["notes"] == "Comfort episode."


def test_watchlist_bridge_reports_duplicate_add() -> None:
    bridge = _bridge()

    bridge.addFromCatalogItem(_selected_payload())
    bridge.addFromCatalogItem(_selected_payload())

    assert bridge.property("errorCode") == "duplicate_item"
    assert bridge.copyForStatus("zh") == "这部动漫已经在你的片单里。"


def test_qml_declares_watchlist_controls() -> None:
    qml_text = QML_PATH.read_text(encoding="utf-8-sig")

    assert 'objectName: "watchListStatusText"' in qml_text
    assert 'objectName: "watchListResultsList"' in qml_text
    assert 'objectName: "watchFilter_all"' in qml_text
    assert "watchListBridge.items" in qml_text
    assert "watchListBridge.updateItem" in qml_text
    assert "watchListBridge.removeItem" in qml_text
