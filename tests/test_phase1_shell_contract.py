from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from anicompass.main import create_engine

PROJECT_ROOT = Path(__file__).resolve().parents[1]
QML_PATH = PROJECT_ROOT / "src" / "anicompass" / "ui" / "Main.qml"


def _app() -> QGuiApplication:
    app = QGuiApplication.instance()
    if app is None:
        QCoreApplication.setOrganizationName("AniCompassTests")
        QCoreApplication.setApplicationName("AniCompassShellContract")
        app = QGuiApplication([])
    return app


def _load_root() -> tuple[QQmlApplicationEngine, object]:
    app = _app()
    engine = create_engine(QML_PATH)
    app.processEvents()
    roots = engine.rootObjects()
    assert roots, "QML root failed to load"
    return engine, roots[0]


def test_phase1_navigation_language_and_theme_contracts(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("ANICOMPASS_CONFIG_DIR", str(tmp_path))
    _engine, root = _load_root()

    root.selectPage(4)
    root.setLanguage("en")
    root.setAccentColor(-20, 128.6, 300)
    root.syncSettings()
    _app().processEvents()

    assert root.property("currentPage") == 4
    assert root.property("language") == "en"
    assert root.property("accentRed") == 0
    assert root.property("accentGreen") == 129
    assert root.property("accentBlue") == 255
    assert root.copyFor("settingsTitle") == "Preferences"

    root.selectPage(99)
    assert root.property("currentPage") == 4

    root.setLanguage("unknown")
    assert root.property("language") == "zh"
    assert root.copyFor("settingsTitle") == "\u504f\u597d\u8bbe\u7f6e"
    root.deleteLater()
    _app().processEvents()
    del root
    del _engine


def test_phase1_shell_settings_persist_between_qml_engine_instances(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setenv("ANICOMPASS_CONFIG_DIR", str(tmp_path))
    first_engine, first_root = _load_root()
    first_root.selectPage(2)
    first_root.setLanguage("en")
    first_root.setAccentColor(12, 34, 56)
    first_root.syncSettings()
    _app().processEvents()
    first_root.deleteLater()
    del first_root
    del first_engine

    second_engine, second_root = _load_root()
    _app().processEvents()

    assert second_root.property("currentPage") == 2
    assert second_root.property("language") == "en"
    assert second_root.property("accentRed") == 12
    assert second_root.property("accentGreen") == 34
    assert second_root.property("accentBlue") == 56
    assert (tmp_path / "settings.ini").exists()
    second_root.deleteLater()
    del second_root
    del second_engine