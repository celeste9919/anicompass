"""Local non-secret UI settings for AniCompass."""

from __future__ import annotations

import os
from pathlib import Path

from PySide6.QtCore import Property, QObject, QSettings, QStandardPaths, Signal, Slot


class SettingsService(QObject):
    """Persist UI preferences through a small local INI file.

    This service stores only non-sensitive preferences. API keys and provider
    credentials must stay in the future keyring-backed credential service.
    """

    languageChanged = Signal()
    currentPageChanged = Signal()
    accentChanged = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._settings_path = self._resolve_settings_path()
        self._settings = QSettings(str(self._settings_path), QSettings.Format.IniFormat)
        self._language = self._read_str("ui/language", "zh")
        self._current_page = max(0, min(4, self._read_int("ui/currentPage", 0)))
        self._accent_red = self._clamp_color(self._read_int("ui/accentRed", 72))
        self._accent_green = self._clamp_color(self._read_int("ui/accentGreen", 119))
        self._accent_blue = self._clamp_color(self._read_int("ui/accentBlue", 210))

    @Property(str, notify=languageChanged)
    def language(self) -> str:
        return self._language

    @Property(int, notify=currentPageChanged)
    def currentPage(self) -> int:
        return self._current_page

    @Property(int, notify=accentChanged)
    def accentRed(self) -> int:
        return self._accent_red

    @Property(int, notify=accentChanged)
    def accentGreen(self) -> int:
        return self._accent_green

    @Property(int, notify=accentChanged)
    def accentBlue(self) -> int:
        return self._accent_blue

    @Slot(str)
    def setLanguage(self, code: str) -> None:
        next_language = "en" if code == "en" else "zh"
        if self._language == next_language:
            return
        self._language = next_language
        self._ensure_settings_parent()
        self._settings.setValue("ui/language", self._language)
        self.languageChanged.emit()

    @Slot(int)
    def setCurrentPage(self, index: int) -> None:
        next_page = max(0, min(4, int(index)))
        if self._current_page == next_page:
            return
        self._current_page = next_page
        self._ensure_settings_parent()
        self._settings.setValue("ui/currentPage", self._current_page)
        self.currentPageChanged.emit()

    @Slot(float, float, float)
    def setAccentColor(self, red: float, green: float, blue: float) -> None:
        next_red = self._clamp_color(red)
        next_green = self._clamp_color(green)
        next_blue = self._clamp_color(blue)
        if (
            self._accent_red,
            self._accent_green,
            self._accent_blue,
        ) == (next_red, next_green, next_blue):
            return
        self._accent_red = next_red
        self._accent_green = next_green
        self._accent_blue = next_blue
        self._ensure_settings_parent()
        self._settings.setValue("ui/accentRed", self._accent_red)
        self._settings.setValue("ui/accentGreen", self._accent_green)
        self._settings.setValue("ui/accentBlue", self._accent_blue)
        self.accentChanged.emit()

    @Slot()
    def sync(self) -> None:
        self._ensure_settings_parent()
        self._settings.sync()

    @property
    def settings_path(self) -> Path:
        return self._settings_path

    def _read_str(self, key: str, default: str) -> str:
        value = self._settings.value(key, default)
        return value if isinstance(value, str) else default

    def _read_int(self, key: str, default: int) -> int:
        value = self._settings.value(key, default)
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def _clamp_color(self, value: float) -> int:
        return max(0, min(255, round(value)))

    def _ensure_settings_parent(self) -> None:
        try:
            self._settings_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            self._settings_path = Path.cwd() / "settings.ini"
            self._settings = QSettings(
                str(self._settings_path), QSettings.Format.IniFormat
            )

    def _resolve_settings_path(self) -> Path:
        override = os.environ.get("ANICOMPASS_CONFIG_DIR")
        if override:
            return Path(override) / "settings.ini"
        location = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.AppConfigLocation
        )
        config_dir = Path(location) if location else Path.cwd()
        return config_dir / "settings.ini"