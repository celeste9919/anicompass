from __future__ import annotations

import os
import time
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QGuiApplication

from anicompass.ai import AIConfigBridge, AIProviderResponse, CredentialService

PROJECT_ROOT = Path(__file__).resolve().parents[1]
QML_PATH = PROJECT_ROOT / "src" / "anicompass" / "ui" / "Main.qml"


class MemoryCredentialBackend:
    def __init__(self) -> None:
        self.values: dict[tuple[str, str], str] = {}

    def set_password(self, service_name: str, username: str, password: str) -> None:
        self.values[(service_name, username)] = password

    def get_password(self, service_name: str, username: str) -> str | None:
        return self.values.get((service_name, username))

    def delete_password(self, service_name: str, username: str) -> None:
        self.values.pop((service_name, username), None)


class PassingConnectionClient:
    async def test_connection(self, config):
        return AIProviderResponse(
            provider_id=config.provider_id,
            model_name=config.model_name,
            content="ok",
        )


def _app() -> QGuiApplication:
    app = QGuiApplication.instance()
    if app is None:
        QCoreApplication.setOrganizationName("AniCompassTests")
        QCoreApplication.setApplicationName("AniCompassAIConfigBridge")
        app = QGuiApplication([])
    return app


def _bridge() -> AIConfigBridge:
    return AIConfigBridge(
        CredentialService(backend=MemoryCredentialBackend()),
        connection_client=PassingConnectionClient(),
    )


def test_ai_config_bridge_lists_providers_and_saves_without_exposing_key() -> None:
    bridge = _bridge()

    assert bridge.property("providers")[0]["providerId"] == "openai"
    bridge.saveApiKey("sk-test")

    assert bridge.property("hasApiKey") is True
    assert "sk-test" not in str(bridge.property("providers"))

    bridge.deleteApiKey()

    assert bridge.property("hasApiKey") is False


def test_ai_config_bridge_selects_provider_and_reports_empty_key() -> None:
    bridge = _bridge()

    bridge.selectProvider("deepseek")
    bridge.saveApiKey(" ")

    assert bridge.property("selectedProviderId") == "deepseek"
    assert bridge.property("errorCode") == "empty_secret"
    assert bridge.copyForStatus("zh") == "API Key \u4e0d\u80fd\u4e3a\u7a7a\u3002"


def test_ai_config_bridge_runs_connection_test() -> None:
    app = _app()
    bridge = _bridge()

    bridge.testConnection()
    assert bridge.property("connectionStatus") == "testing"

    for _ in range(100):
        app.processEvents()
        time.sleep(0.01)
        if bridge.property("connectionStatus") == "connected":
            break

    assert bridge.property("connectionStatus") == "connected"
    assert bridge.copyForStatus("en") == "AI connection test passed."
    bridge.close()


def test_qml_declares_ai_config_controls() -> None:
    qml_text = QML_PATH.read_text(encoding="utf-8-sig")

    assert 'objectName: "aiProviderCombo"' in qml_text
    assert 'objectName: "aiApiKeyInput"' in qml_text
    assert 'objectName: "saveApiKeyButton"' in qml_text
    assert 'objectName: "deleteApiKeyButton"' in qml_text
    assert 'objectName: "testAiConnectionButton"' in qml_text
    assert 'objectName: "aiConfigStatusText"' in qml_text
    assert "aiConfigBridge.saveApiKey" in qml_text
    assert "aiConfigBridge.testConnection" in qml_text
