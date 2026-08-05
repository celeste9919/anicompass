"""Qt-facing bridge for AI provider configuration."""

from __future__ import annotations

import asyncio
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Protocol

from PySide6.QtCore import Property, QObject, Signal, Slot

from anicompass.ai.client import OpenAICompatibleChatClient
from anicompass.ai.credentials import CredentialError, CredentialService
from anicompass.ai.models import (
    AIProviderCallError,
    AIProviderConfig,
    AIProviderResponse,
)
from anicompass.ai.providers import default_provider_configs


class AIConnectionClient(Protocol):
    async def test_connection(
        self,
        config: AIProviderConfig,
    ) -> AIProviderResponse: ...


class AIConfigBridge(QObject):
    """Expose non-secret AI provider choices and keyring actions to QML."""

    stateChanged = Signal()
    _connectionFinished = Signal(object, object)

    def __init__(
        self,
        credential_service: CredentialService,
        providers: tuple[AIProviderConfig, ...] | None = None,
        parent: QObject | None = None,
        connection_client: AIConnectionClient | None = None,
        executor: ThreadPoolExecutor | None = None,
    ) -> None:
        super().__init__(parent)
        self._credential_service = credential_service
        self._providers = providers or default_provider_configs()
        self._selected_provider_id = self._providers[0].provider_id
        self._error_code = ""
        self._error_message = ""
        self._is_testing = False
        self._connection_status = "idle"
        self._connection_client = connection_client or OpenAICompatibleChatClient(
            credential_service
        )
        self._executor = executor or ThreadPoolExecutor(max_workers=1)
        self._owns_executor = executor is None
        self._connectionFinished.connect(self._handle_connection_finished)

    @Property(list, notify=stateChanged)
    def providers(self) -> list[dict[str, object]]:
        return [self._provider_to_qml(provider) for provider in self._providers]

    @Property(str, notify=stateChanged)
    def selectedProviderId(self) -> str:
        return self._selected_provider_id

    @Property(bool, notify=stateChanged)
    def hasApiKey(self) -> bool:
        try:
            return self._credential_service.has_api_key(self._selected_provider_id)
        except CredentialError as exc:
            self._set_error(exc.code, exc.public_message)
            return False

    @Property(bool, notify=stateChanged)
    def isTestingConnection(self) -> bool:
        return self._is_testing

    @Property(str, notify=stateChanged)
    def connectionStatus(self) -> str:
        return self._connection_status

    @Property(str, notify=stateChanged)
    def errorCode(self) -> str:
        return self._error_code

    @Property(str, notify=stateChanged)
    def errorMessage(self) -> str:
        return self._error_message

    @Slot(str)
    def selectProvider(self, provider_id: str) -> None:
        if provider_id not in {provider.provider_id for provider in self._providers}:
            self._set_error("unknown_provider", "Unknown AI provider.")
        else:
            self._selected_provider_id = provider_id
            self._clear_error()
        self.stateChanged.emit()

    @Slot(str)
    def saveApiKey(self, api_key: str) -> None:
        try:
            self._credential_service.set_api_key(self._selected_provider_id, api_key)
            self._clear_error()
        except CredentialError as exc:
            self._set_error(exc.code, exc.public_message)
        self.stateChanged.emit()

    @Slot()
    def testConnection(self) -> None:
        if self._is_testing:
            return
        self._clear_error()
        self._is_testing = True
        self._connection_status = "testing"
        self.stateChanged.emit()
        future = self._executor.submit(self._run_connection_test)
        future.add_done_callback(self._emit_connection_finished)

    @Slot()
    def deleteApiKey(self) -> None:
        try:
            self._credential_service.delete_api_key(self._selected_provider_id)
            self._clear_error()
        except CredentialError as exc:
            self._set_error(exc.code, exc.public_message)
        self.stateChanged.emit()

    @Slot(str, result=str)
    def copyForStatus(self, language: str) -> str:
        if self._connection_status == "testing":
            return (
                "\u6b63\u5728\u6d4b\u8bd5 AI \u8fde\u63a5..."
                if language == "zh"
                else "Testing AI connection..."
            )
        if self._connection_status == "connected" and not self._error_code:
            return (
                "AI \u8fde\u63a5\u6d4b\u8bd5\u901a\u8fc7\u3002"
                if language == "zh"
                else "AI connection test passed."
            )
        if self._error_code:
            if language == "zh" and self._error_code == "empty_secret":
                return "API Key \u4e0d\u80fd\u4e3a\u7a7a\u3002"
            if language == "zh" and self._error_code == "keyring_unavailable":
                return (
                    "\u7cfb\u7edf\u5bc6\u94a5\u5b58\u50a8"
                    "\u6682\u4e0d\u53ef\u7528\u3002"
                )
            if language == "zh":
                return "AI \u914d\u7f6e\u64cd\u4f5c\u5931\u8d25\u3002"
            return self._error_message
        if self.hasApiKey:
            return (
                "API Key \u5df2\u5b89\u5168\u4fdd\u5b58\u3002"
                if language == "zh"
                else "API key is saved."
            )
        return (
            "\u5c1a\u672a\u4fdd\u5b58 API Key\u3002"
            if language == "zh"
            else "No API key saved."
        )

    @Slot(object, object)
    def _handle_connection_finished(
        self,
        response: AIProviderResponse | None,
        error: BaseException | None,
    ) -> None:
        self._is_testing = False
        if response is not None:
            self._connection_status = "connected"
            self._clear_error()
        elif isinstance(error, AIProviderCallError):
            self._connection_status = "error"
            self._set_error(error.error.code.value, error.error.message)
        elif error is not None:
            self._connection_status = "error"
            self._set_error("provider_error", "AI connection test failed.")
        self.stateChanged.emit()

    def close(self) -> None:
        if self._owns_executor:
            self._executor.shutdown(wait=False, cancel_futures=True)

    def _run_connection_test(self) -> AIProviderResponse:
        return asyncio.run(
            self._connection_client.test_connection(self._selected_provider())
        )

    def _emit_connection_finished(
        self,
        future: Future[AIProviderResponse],
    ) -> None:
        try:
            self._connectionFinished.emit(future.result(), None)
        except BaseException as exc:
            self._connectionFinished.emit(None, exc)

    def _selected_provider(self) -> AIProviderConfig:
        return next(
            provider
            for provider in self._providers
            if provider.provider_id == self._selected_provider_id
        )

    def _provider_to_qml(self, provider: AIProviderConfig) -> dict[str, object]:
        return {
            "providerId": provider.provider_id,
            "displayName": provider.display_name,
            "providerType": provider.provider_type.value,
            "baseUrl": str(provider.base_url),
            "modelName": provider.model_name,
            "timeoutSeconds": provider.timeout_seconds,
        }

    def _clear_error(self) -> None:
        self._error_code = ""
        self._error_message = ""

    def _set_error(self, code: str, message: str) -> None:
        self._error_code = code
        self._error_message = message
