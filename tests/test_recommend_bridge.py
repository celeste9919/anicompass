from __future__ import annotations

import asyncio
import os
import time
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QGuiApplication

from anicompass.ai import AIProviderConfig, AIProviderType
from anicompass.catalog import CatalogAnime, CatalogAnimeId, CatalogSource
from anicompass.history import HistoryService, SQLiteHistoryRepository
from anicompass.recommendation import RecommendationResult
from anicompass.recommendation.bridge import RecommendBridge
from anicompass.recommendation.models import VerifiedRecommendation

PROJECT_ROOT = Path(__file__).resolve().parents[1]
QML_PATH = PROJECT_ROOT / "src" / "anicompass" / "ui" / "Main.qml"


class OrchestratorDouble:
    async def recommend(self, request, config):
        return RecommendationResult(
            items=(
                VerifiedRecommendation(
                    anime=CatalogAnime(
                        catalog_id=CatalogAnimeId(
                            source=CatalogSource.JIKAN,
                            provider_id="1",
                        ),
                        title="Cowboy Bebop",
                        year=1998,
                        score=8.7,
                    ),
                    reason="Fits the space jazz mood.",
                ),
            )
        )


class SlowOrchestratorDouble(OrchestratorDouble):
    async def recommend(self, request, config):
        await asyncio.sleep(0.01)
        return await super().recommend(request, config)


def _app() -> QGuiApplication:
    app = QGuiApplication.instance()
    if app is None:
        QCoreApplication.setOrganizationName("AniCompassTests")
        QCoreApplication.setApplicationName("AniCompassRecommendBridge")
        app = QGuiApplication([])
    return app


def _config() -> AIProviderConfig:
    return AIProviderConfig(
        provider_type=AIProviderType.CUSTOM,
        provider_id="custom",
        display_name="Custom",
        base_url="https://example.com/v1",
        model_name="anime-model",
    )


def test_recommend_bridge_runs_recommendation_to_success() -> None:
    app = _app()
    bridge = RecommendBridge(SlowOrchestratorDouble(), _config())

    bridge.recommend("space jazz noir", 3, "en")
    assert bridge.property("status") == "loading"

    for _ in range(100):
        app.processEvents()
        time.sleep(0.01)
        if bridge.property("status") == "success":
            break

    assert bridge.property("status") == "success"
    assert bridge.property("items")[0]["title"] == "Cowboy Bebop"
    assert bridge.copyForStatus("en") == "1 verified recommendations."
    bridge.close()


def test_recommend_bridge_saves_successful_session_to_history() -> None:
    repository = SQLiteHistoryRepository()
    history = HistoryService(repository)
    app = _app()
    bridge = RecommendBridge(
        SlowOrchestratorDouble(),
        _config(),
        history_service=history,
    )

    bridge.recommend("space jazz noir", 3, "en")
    for _ in range(100):
        app.processEvents()
        time.sleep(0.01)
        if bridge.property("status") == "success":
            break

    sessions = history.list_sessions()

    assert len(sessions) == 1
    assert sessions[0].preferences == "space jazz noir"
    assert sessions[0].verified_count == 1
    bridge.close()
    repository.close()


def test_recommend_bridge_rejects_short_preferences() -> None:
    bridge = RecommendBridge(OrchestratorDouble(), _config())

    bridge.recommend("x", 3, "en")

    assert bridge.property("status") == "error"
    assert bridge.property("errorCode") == "invalid_request"
    bridge.close()


def test_qml_declares_recommend_controls() -> None:
    qml_text = QML_PATH.read_text(encoding="utf-8-sig")

    assert 'objectName: "recommendPreferenceInput"' in qml_text
    assert 'objectName: "recommendCountInput"' in qml_text
    assert 'objectName: "recommendButton"' in qml_text
    assert 'objectName: "recommendStatusText"' in qml_text
    assert 'objectName: "recommendResultsList"' in qml_text
    assert "recommendBridge.recommend" in qml_text
    assert "recommendBridge.items" in qml_text
