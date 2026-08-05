"""Built-in non-secret AI provider presets."""

from __future__ import annotations

from anicompass.ai.models import AIProviderConfig, AIProviderType


def default_provider_configs() -> tuple[AIProviderConfig, ...]:
    """Return editable OpenAI-compatible provider presets without API keys."""

    return (
        AIProviderConfig(
            provider_type=AIProviderType.OPENAI,
            provider_id="openai",
            display_name="OpenAI",
            base_url="https://api.openai.com/v1",
            model_name="gpt-5-mini",
        ),
        AIProviderConfig(
            provider_type=AIProviderType.DEEPSEEK,
            provider_id="deepseek",
            display_name="DeepSeek",
            base_url="https://api.deepseek.com/v1",
            model_name="deepseek-chat",
        ),
        AIProviderConfig(
            provider_type=AIProviderType.QWEN,
            provider_id="qwen",
            display_name="Alibaba Cloud Model Studio / Qwen",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            model_name="qwen-plus",
        ),
        AIProviderConfig(
            provider_type=AIProviderType.CUSTOM,
            provider_id="custom",
            display_name="Custom Compatible Endpoint",
            base_url="https://example.com/v1",
            model_name="custom-model",
        ),
    )
