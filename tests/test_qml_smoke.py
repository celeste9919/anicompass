from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_phase1_qml_file_exists() -> None:
    qml_path = PROJECT_ROOT / "src" / "anicompass" / "ui" / "Main.qml"
    qml_text = qml_path.read_text(encoding="utf-8-sig")

    assert qml_path.exists()
    assert "AniCompass" in qml_text
    assert "StackLayout" in qml_text
    assert "settingsService" in qml_text


def test_phase1_shell_contract_text_is_present() -> None:
    qml_text = (PROJECT_ROOT / "src" / "anicompass" / "ui" / "Main.qml").read_text(
        encoding="utf-8-sig"
    )

    for required_text in [
        "recommendTitle",
        "searchTitle",
        "listTitle",
        "historyTitle",
        "settingsTitle",
        "accentRed",
        "accentGreen",
        "accentBlue",
        "language",
    ]:
        assert required_text in qml_text


def test_phase1_main_entry_exists() -> None:
    main_path = PROJECT_ROOT / "src" / "anicompass" / "main.py"

    assert main_path.exists()
    assert "--smoke-test" in main_path.read_text(encoding="utf-8")
