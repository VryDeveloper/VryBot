"""LLM provider registry.

Every provider here exposes an OpenAI-compatible Chat Completions endpoint,
so one client handles all of them. To add a new one, add an entry to
PRESETS — no other code changes needed (see docs/extending.md).
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Provider:
    name: str
    base_url: str
    api_key: str
    model: str
    extra_body: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Preset:
    base_url: str
    default_model: str
    signup_url: str = ""


PRESETS: dict[str, Preset] = {
    "groq": Preset(
        base_url="https://api.groq.com/openai/v1",
        default_model="openai/gpt-oss-120b",
        signup_url="https://console.groq.com/keys",
    ),
    "gemini": Preset(
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        default_model="gemini-flash-latest",
        signup_url="https://aistudio.google.com/apikey",
    ),
    "openrouter": Preset(
        base_url="https://openrouter.ai/api/v1",
        default_model="meta-llama/llama-3.3-70b-instruct:free",
        signup_url="https://openrouter.ai/keys",
    ),
    # Any other OpenAI-compatible server: Ollama, LM Studio, vLLM, a paid API...
    # Its base URL comes from CUSTOM_BASE_URL.
    "custom": Preset(base_url="", default_model=""),
}


def _extra_body_for(model: str) -> dict:
    # Reasoning models (gpt-oss family) "think" before answering. Low effort
    # keeps chat replies fast; other models reject this field, so only send it here.
    if "gpt-oss" in model:
        return {"reasoning_effort": os.getenv("REASONING_EFFORT", "low")}
    return {}


def load_providers() -> list[Provider]:
    """Build the provider list from the environment, in PROVIDERS order.

    A provider without an API key is silently skipped, so users only fill in
    the ones they want.
    """
    raw = os.getenv("PROVIDERS", "").strip() or "groq,gemini,openrouter"
    order = [p.strip().lower() for p in raw.split(",") if p.strip()]
    providers: list[Provider] = []
    for name in order:
        preset = PRESETS.get(name)
        if preset is None:
            raise ValueError(f"Unknown provider '{name}' in PROVIDERS. Known: {', '.join(PRESETS)}")
        prefix = name.upper()
        key = os.getenv(f"{prefix}_API_KEY", "").strip()
        base_url = os.getenv(f"{prefix}_BASE_URL", "").strip() or preset.base_url
        model = os.getenv(f"{prefix}_MODEL", "").strip() or preset.default_model
        if name == "custom" and base_url and not key:
            key = "not-needed"  # local servers like Ollama ignore the key
        if not key or not base_url or not model:
            continue
        providers.append(Provider(name, base_url, key, model, _extra_body_for(model)))
    return providers
