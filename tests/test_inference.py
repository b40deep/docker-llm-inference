import asyncio

from app.config import Settings
from app.llm_proxy import _build_upstream_request, _upstream_url, infer


def test_inference_uses_safe_demo_without_endpoint():
    response = asyncio.run(infer("Explain a proxy.", Settings(app_password="test", llm_endpoint_url="")))
    assert "Demo response" in response
    assert "Explain a proxy." in response


def test_azure_openai_request_uses_api_key_and_deployment_url_payload():
    settings = Settings(
        app_password="test",
        llm_provider="azure_openai",
        llm_endpoint_url=(
            "https://example.openai.azure.com/openai/deployments/chat/chat/completions?api-version=2024-10-21"
        ),
        llm_api_key="secret",
    )

    headers, payload = _build_upstream_request(settings, "Hello")

    assert headers == {"Content-Type": "application/json", "api-key": "secret"}
    assert payload == {"messages": [{"role": "user", "content": "Hello"}], "stream": False}


def test_azure_openai_v1_base_url_targets_chat_completions():
    settings = Settings(
        app_password="test",
        llm_provider="azure_openai_v1",
        llm_endpoint_url="https://example.services.ai.azure.com/openai/v1",
    )

    assert _upstream_url(settings) == "https://example.services.ai.azure.com/openai/v1/chat/completions"


def test_azure_openai_v1_request_includes_model():
    settings = Settings(
        app_password="test",
        llm_provider="azure_openai_v1",
        llm_endpoint_url="https://example.services.ai.azure.com/openai/v1",
        llm_api_key="secret",
        llm_model="gpt-6-astra",
    )

    headers, payload = _build_upstream_request(settings, "Hello")

    assert headers == {"Content-Type": "application/json", "api-key": "secret"}
    assert payload == {
        "model": "gpt-6-astra",
        "messages": [{"role": "user", "content": "Hello"}],
        "stream": False,
    }


def test_request_includes_prior_search_context_before_current_prompt():
    settings = Settings(app_password="test", llm_model="model")
    history = [
        {"role": "user", "content": "Earlier search"},
        {"role": "assistant", "content": "Earlier response"},
    ]

    _, payload = _build_upstream_request(settings, "Current search", history)

    assert payload["messages"] == [
        *history,
        {"role": "user", "content": "Current search"},
    ]
