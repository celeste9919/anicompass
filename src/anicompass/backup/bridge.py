"""Qt-facing bridge for backup and restore actions."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Property, QObject, QUrl, Signal, Slot

from anicompass.backup.service import (
    BackupError,
    BackupService,
    BackupValidationError,
)


class BackupBridge(QObject):
    """Expose safe local backup operations to QML."""

    stateChanged = Signal()
    restoreCompleted = Signal()

    def __init__(
        self,
        service: BackupService,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._service = service
        self._status = "idle"
        self._error_code = ""
        self._error_message = ""
        self._last_path = ""
        self._last_watch_count = 0
        self._last_history_count = 0

    @Property(str, notify=stateChanged)
    def status(self) -> str:
        return self._status

    @Property(str, notify=stateChanged)
    def errorCode(self) -> str:
        return self._error_code

    @Property(str, notify=stateChanged)
    def errorMessage(self) -> str:
        return self._error_message

    @Property(str, notify=stateChanged)
    def lastPath(self) -> str:
        return self._last_path

    @Property(int, notify=stateChanged)
    def lastWatchCount(self) -> int:
        return self._last_watch_count

    @Property(int, notify=stateChanged)
    def lastHistoryCount(self) -> int:
        return self._last_history_count

    @Slot(str)
    def exportBackup(self, path_or_url: str) -> None:
        path = self._path_from_qml(path_or_url)
        if path is None:
            self._set_error("missing_path", "Choose a backup file path.")
            self.stateChanged.emit()
            return
        try:
            backup = self._service.export_backup(path)
        except BackupError as exc:
            self._set_error("export_failed", str(exc))
        else:
            self._set_success(
                "exported",
                path,
                len(backup.watch_list_items),
                len(backup.recommendation_history),
            )
        self.stateChanged.emit()

    @Slot(str)
    def importBackup(self, path_or_url: str) -> None:
        path = self._path_from_qml(path_or_url)
        if path is None:
            self._set_error("missing_path", "Choose a backup file path.")
            self.stateChanged.emit()
            return
        try:
            backup = self._service.import_backup(path)
        except BackupValidationError as exc:
            self._set_error("invalid_backup", str(exc))
        except BackupError as exc:
            self._set_error("import_failed", str(exc))
        else:
            self._set_success(
                "imported",
                path,
                len(backup.watch_list_items),
                len(backup.recommendation_history),
            )
            self.restoreCompleted.emit()
        self.stateChanged.emit()

    @Slot(str, result=str)
    def copyForStatus(self, language: str) -> str:
        if self._error_code:
            if language == "zh":
                if self._error_code == "missing_path":
                    return "请选择备份文件路径。"
                if self._error_code == "invalid_backup":
                    return "备份文件无效，现有数据已保留。"
                return "备份操作失败。"
            return self._error_message
        if self._status == "exported":
            if language == "zh":
                return (
                    f"已导出 {self._last_watch_count} 条片单和 "
                    f"{self._last_history_count} 条历史。"
                )
            return (
                f"Exported {self._last_watch_count} list items and "
                f"{self._last_history_count} history sessions."
            )
        if self._status == "imported":
            if language == "zh":
                return (
                    f"已恢复 {self._last_watch_count} 条片单和 "
                    f"{self._last_history_count} 条历史。"
                )
            return (
                f"Restored {self._last_watch_count} list items and "
                f"{self._last_history_count} history sessions."
            )
        return "可导出或恢复本地数据，API Key 不会进入备份。" if language == "zh" else (
            "Export or restore local data. API keys are never included."
        )

    def _path_from_qml(self, path_or_url: str) -> Path | None:
        value = path_or_url.strip()
        if not value:
            return None
        url = QUrl(value)
        if url.isValid() and url.isLocalFile():
            return Path(url.toLocalFile())
        return Path(value)

    def _set_success(
        self,
        status: str,
        path: Path,
        watch_count: int,
        history_count: int,
    ) -> None:
        self._status = status
        self._last_path = str(path)
        self._last_watch_count = watch_count
        self._last_history_count = history_count
        self._error_code = ""
        self._error_message = ""

    def _set_error(self, code: str, message: str) -> None:
        self._status = "error"
        self._error_code = code
        self._error_message = message
