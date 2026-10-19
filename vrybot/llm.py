"""Chat client that walks the provider list until one answers."""
from __future__ import annotations

import logging
import time

import openai
from openai import AsyncOpenAI

from .providers import Provider

log = logging.getLogger(__name__)

# Errors where trying the next provider makes sense.
_FALLBACK_ERRORS = (
    openai.RateLimitError,
    openai.APIConnectionError,
    openai.APITimeoutError,
    openai.InternalServerError,
    openai.NotFoundError,
    openai.AuthenticationError,
    openai.PermissionDeniedError,
)

RATE_LIMIT_COOLDOWN = 60  # seconds a rate-limited provider is moved to the back of the queue


class AllProvidersFailed(RuntimeError):
    pass


class LLMClient:
    def __init__(self, providers: list[Provider], *, temperature: float, max_tokens: int):
        if not providers:
            raise ValueError("No LLM provider configured. Set at least one *_API_KEY in your .env file.")
        self.providers = providers
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._clients = {p.name: AsyncOpenAI(api_key=p.api_key, base_url=p.base_url, timeout=40) for p in providers}
        self._cooldown_until: dict[str, float] = {}

    def _ordered(self) -> list[Provider]:
        now = time.monotonic()
        # Stable sort: providers cooling down go last but are still tried.
        return sorted(self.providers, key=lambda p: self._cooldown_until.get(p.name, 0) > now)

    async def chat(self, messages: list[dict]) -> str:
        errors: list[str] = []
        for p in self._ordered():
            try:
                resp = await self._clients[p.name].chat.completions.create(
                    model=p.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    extra_body=p.extra_body or None,
                )
            except openai.RateLimitError:
                self._cooldown_until[p.name] = time.monotonic() + RATE_LIMIT_COOLDOWN
                errors.append(f"{p.name}: rate limited")
                continue
            except _FALLBACK_ERRORS as e:
                errors.append(f"{p.name}: {type(e).__name__}")
                continue
            except openai.APIStatusError as e:
                errors.append(f"{p.name}: HTTP {e.status_code}")
                continue

            text = (resp.choices[0].message.content or "").strip() if resp.choices else ""
            if text:
                log.debug("Answered by %s (%s)", p.name, p.model)
                return text
            errors.append(f"{p.name}: empty reply")

        raise AllProvidersFailed(" | ".join(errors))
