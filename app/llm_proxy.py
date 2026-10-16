"""Non-streaming server-side LLM adapter."""
from typing import Any

import httpx

from .config import Settings


class UpstreamInferenceError(Exception):
    """Raised when a configured upstream fails without exposing its details."""


def demo_response(prompt: str) -> str:
    """Return deterministic local behavior when no upstream endpoint is configured."""
    return (
        "Demo response (no upstream endpoint is configured):\n\n"
        f"Your prompt was received securely by the server: {prompt.strip()}\n\n"
        "Set LLM_ENDPOINT_URL and LLM_API_KEY in the server-side .env file to proxy "
        "non-streaming requests to a compatible upstream."
    )


def _extract_response(payload: Any) -> str:
    if isinstance(payload, dict):
        if isinstance(payload.get("response"), str):
            return payload["response"]
        if isinstance(payload.get("text"), str):
            return payload["text"]
        choices = payload.get("choices")
        if isinstance(choices, list) and choices:
            first = choices[0]
            if isinstance(first, dict):
                message = first.get("message")
                if isinstance(message, dict) and isinstance(message.get("content"), str):
                    return message["content"]
                if isinstance(first.get("text"), str):
                    return first["text"]
    raise UpstreamInferenceError("The upstream returned an unsupported response format.")


def _build_upstream_request(
    settings: Settings, prompt: str, history: list[dict[str, str]] | None = None
) -> tuple[dict[str, str], dict[str, Any]]:
    """Build a non-streaming request for the configured provider without leaking secrets."""
    payload: dict[str, Any] = {
        "messages": [*(history or []), {"role": "user", "content": prompt}],
        "stream": False,
    }
    if settings.uses_azure_openai:
        headers = {"Content-Type": "application/json", "api-key": settings.llm_api_key}
        # Deployment-specific Azure URLs select the model in their path. Azure OpenAI
        # v1 endpoints instead require a model/deployment identifier in the body.
        if settings.uses_azure_openai_v1:
            payload["model"] = settings.llm_model
    else:
        headers = {"Content-Type": "application/json"}
        if settings.llm_api_key:
            headers["Authorization"] = f"Bearer {settings.llm_api_key}"
        payload["model"] = settings.llm_model
    return headers, payload


def _upstream_url(settings: Settings) -> str:
    """Return the chat-completions URL for the selected upstream provider."""
    endpoint = settings.llm_endpoint_url.rstrip("/")
    if settings.uses_azure_openai_v1 and endpoint.endswith("/openai/v1"):
        return f"{endpoint}/chat/completions"
    return endpoint


async def infer(prompt: str, settings: Settings, history: list[dict[str, str]] | None = None) -> str:
    """Call a supported non-streaming endpoint, or provide safe demo output."""
    if not settings.upstream_configured:
        return demo_response(prompt)

    headers, payload = _build_upstream_request(settings, prompt, history)
    try:
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.post(_upstream_url(settings), headers=headers, json=payload)
            response.raise_for_status()
            return _extract_response(response.json())
    except (httpx.HTTPError, ValueError, UpstreamInferenceError) as error:
        raise UpstreamInferenceError("The configured inference service is unavailable.") from error
