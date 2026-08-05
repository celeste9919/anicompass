from __future__ import annotations

import os
import time
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QGuiApplication

from anicompass.catalog import (
    CatalogAnime,
    CatalogAnimeId,
    CatalogSearchResult,
    CatalogSource,
)
from anicompass.search import SearchBridge, SearchStatus, SearchViewModel

PROJECT_ROOT = Path(__file__).resolve().parents[1]
QML_PATH = PROJECT_ROOT / "src" / "anicompass" / "ui" / "Main.qml"


class MemoryCredentialBackend:
    def set_password(self, service_name: str, username: str, password: str) -> None:
        self.value = password

    def get_password(self, service_name: str, username: str) -> str | None:
        return None

    def delete_password(self, service_name: str, username: str) -> None:
        return None


class RecommendOrchestratorDouble:
    async def recommend(self, request, config):
        from anicompass.recommendation import RecommendationResult

        return RecommendationResult(items=())


class SearchServiceDouble:
    async def search(
        self,
        query: str,
        *,
        limit: int = 10,
        safe_for_all_audiences: bool = True,
    ) -> CatalogSearchResult:
        return CatalogSearchResult(
            items=(
                CatalogAnime(
                    catalog_id=CatalogAnimeId(
                        source=CatalogSource.JIKAN, provider_id="1"
                    ),
                    title="Cowboy Bebop",
                    year=1998,
                    genres=("Action", "Sci-Fi"),
                    attribution="Jikan / MyAnimeList",
                ),
            ),
            source=CatalogSource.JIKAN,
            query=query,
        )


def _app() -> QGuiApplication:
    app = QGuiApplication.instance()
    if app is None:
        QCoreApplication.setOrganizationName("AniCompassTests")
        QCoreApplication.setApplicationName("AniCompassSearchBridge")
        app = QGuiApplication([])
    return app


def _wait_for_bridge(
    bridge: SearchBridge, status: str, timeout_seconds: float = 2
) -> None:
    deadline = time.monotonic() + timeout_seconds
    app = _app()
    while time.monotonic() < deadline:
        app.processEvents()
        if bridge.property("status") == status:
            return
        time.sleep(0.01)
    raise AssertionError(f"Timed out waiting for search status {status!r}")


def test_search_bridge_emits_loading_then_success_items() -> None:
    bridge = SearchBridge(SearchViewModel(SearchServiceDouble()))

    bridge.search(" bebop ")

    assert bridge.property("status") == SearchStatus.LOADING.value
    assert bridge.property("isBusy") is True
    _wait_for_bridge(bridge, SearchStatus.SUCCESS.value)
    assert bridge.property("query") == "bebop"
    assert bridge.property("itemCount") == 1
    assert bridge.property("items")[0]["title"] == "Cowboy Bebop"
    assert bridge.property("hasSelection") is True
    assert bridge.property("selectedItem")["title"] == "Cowboy Bebop"
    bridge.close()


def test_search_bridge_selects_and_clears_item() -> None:
    bridge = SearchBridge(SearchViewModel(SearchServiceDouble()))

    bridge.search("bebop")
    _wait_for_bridge(bridge, SearchStatus.SUCCESS.value)
    bridge.clearSelection()
    assert bridge.property("hasSelection") is False
    bridge.selectItem("1")

    assert bridge.property("hasSelection") is True
    assert bridge.property("selectedItem")["providerId"] == "1"
    bridge.close()


def test_qml_shell_declares_search_bridge_controls() -> None:
    qml_text = QML_PATH.read_text(encoding="utf-8-sig")

    assert 'objectName: "searchInput"' in qml_text
    assert 'objectName: "searchButton"' in qml_text
    assert 'objectName: "searchStatusText"' in qml_text
    assert 'objectName: "searchResultsList"' in qml_text
    assert 'objectName: "searchDetailPanel"' in qml_text
    assert 'objectName: "addSelectedToListButton"' in qml_text
    assert "searchBridge.search" in qml_text
    assert "searchBridge.selectedItem" in qml_text
