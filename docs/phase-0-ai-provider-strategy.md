# Phase 0 AI Provider Strategy

Date: 2026-08-04  
Decision: Use OpenAI-compatible chat completion style as the first shared adapter path.

## Goal

AniCompass users configure their own AI provider, endpoint, model, and API key.
The app must not hard-code secrets or pretend to have AI results when a provider
is missing or failing.

## Initial Presets

The first settings UI should offer these provider presets:

1. OpenAI
2. DeepSeek
3. Alibaba Cloud Model Studio / Qwen
4. Custom OpenAI-compatible endpoint

The preset only fills provider type and suggested endpoint pattern. The user can
manually edit endpoint and model name because provider model catalogs change.

## Why This Is Enough For V1

- It satisfies the confirmed requirement for international, domestic, and custom
  providers.
- It keeps one shared request/response path for most providers.
- It avoids adding several provider SDKs in v1.
- It keeps PromptBuilder and ResultParser independent of provider details.

## Provider Notes

### OpenAI

Use the official OpenAI API path as one preset. Do not claim a fixed latest
model in code. Let the user enter or update the model name.

Official reference:

- `https://platform.openai.com/docs/api-reference/chat`

### DeepSeek

DeepSeek documents OpenAI-compatible access. It can use the shared compatible
adapter with a DeepSeek endpoint and user API key.

Official reference:

- `https://api-docs.deepseek.com/`

### Alibaba Cloud Model Studio / Qwen

Alibaba Cloud Model Studio documents OpenAI-compatible chat completion APIs for
Qwen and other hosted models. Endpoints can vary by region and workspace, so the
settings UI must let users edit the endpoint.

Official references:

- `https://www.alibabacloud.com/help/en/model-studio/qwen-api-via-openai-chat-completions`
- `https://www.alibabacloud.com/help/en/model-studio/models`

### Custom Compatible Endpoint

The custom option requires:

- HTTPS endpoint by default
- API key stored in keyring
- user-entered model name
- configurable timeout
- clear provider error mapping

## V1 Adapter Interface

Use one provider-neutral interface:

1. `validate_config(config)`
2. `complete(config, prompt_payload)`

The adapter must return raw provider text plus safe metadata. It must not parse
AniCompass recommendation objects directly.

## Validation Rules

- Reject empty API keys.
- Reject empty model names.
- Reject non-HTTPS endpoints unless a future local-development exception is
  explicitly approved.
- Never log full requests, raw credentials, or authorization headers.
- On missing credentials, show configuration guidance instead of fake results.

## Later Provider Extensions

Dedicated provider adapters may be added only when the provider is not reliably
covered by the compatible adapter or offers a feature AniCompass explicitly
needs.
