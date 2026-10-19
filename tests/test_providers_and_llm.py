from types import SimpleNamespace

import openai
import pytest

from vrybot.llm import AllProvidersFailed, LLMClient
from vrybot.providers import Provider, load_providers


def _clear_env(monkeypatch):
    for var in ["PROVIDERS", "GROQ_API_KEY", "GEMINI_API_KEY", "OPENROUTER_API_KEY",
                "CUSTOM_BASE_URL", "CUSTOM_API_KEY", "CUSTOM_MODEL", "GROQ_MODEL"]:
        monkeypatch.delenv(var, raising=False)


def test_providers_without_key_are_skipped(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    assert [p.name for p in load_providers()] == ["gemini"]


def test_order_and_reasoning_flag(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("PROVIDERS", "gemini,groq")
    monkeypatch.setenv("GROQ_API_KEY", "a")
    monkeypatch.setenv("GEMINI_API_KEY", "b")
    gemini_, groq_ = sorted(load_providers(), key=lambda p: p.name)
    assert [p.name for p in load_providers()] == ["gemini", "groq"]
    assert "reasoning_effort" in groq_.extra_body and gemini_.extra_body == {}


def test_custom_local_server_needs_no_key(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("PROVIDERS", "custom")
    monkeypatch.setenv("CUSTOM_BASE_URL", "http://localhost:11434/v1")
    monkeypatch.setenv("CUSTOM_MODEL", "llama3.2")
    [p] = load_providers()
    assert p.base_url.startswith("http://localhost") and p.api_key


def test_unknown_provider_raises(monkeypatch):
    _clear_env(monkeypatch)
    monkeypatch.setenv("PROVIDERS", "nope")
    with pytest.raises(ValueError):
        load_providers()


def _client(*names):
    providers = [Provider(n, "https://example.invalid/v1", "k", "m") for n in names]
    return LLMClient(providers, temperature=0.5, max_tokens=50)


def _reply(text):
    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=text))])


class _FakeRateLimit(openai.RateLimitError):
    def __init__(self):  # skip the real constructor, which needs an HTTP response
        Exception.__init__(self, "rate limited")


async def test_falls_back_when_first_provider_is_rate_limited():
    llm = _client("a", "b")

    async def limited(**_):
        raise _FakeRateLimit()

    async def ok(**_):
        return _reply("  hi  ")

    llm._clients["a"].chat.completions.create = limited
    llm._clients["b"].chat.completions.create = ok
    assert await llm.chat([{"role": "user", "content": "x"}]) == "hi"
    # rate-limited provider is now tried last
    assert [p.name for p in llm._ordered()] == ["b", "a"]


async def test_raises_when_everything_fails():
    llm = _client("a")

    async def empty(**_):
        return _reply("")

    llm._clients["a"].chat.completions.create = empty
    with pytest.raises(AllProvidersFailed):
        await llm.chat([{"role": "user", "content": "x"}])


def test_no_providers_is_a_clear_error():
    with pytest.raises(ValueError):
        LLMClient([], temperature=0.5, max_tokens=50)
