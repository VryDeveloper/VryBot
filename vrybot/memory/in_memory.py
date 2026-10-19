from __future__ import annotations

from collections import defaultdict, deque

from .base import MemoryBackend, Message


class InMemoryBackend(MemoryBackend):
    """Fast and zero-setup. Forgets everything when the bot restarts."""

    def __init__(self, history_size: int):
        super().__init__(history_size)
        self._store: dict[int, deque[Message]] = defaultdict(lambda: deque(maxlen=self.history_size))

    async def add(self, channel_id: int, role: str, content: str) -> None:
        self._store[channel_id].append({"role": role, "content": content})

    async def history(self, channel_id: int) -> list[Message]:
        return list(self._store.get(channel_id, ()))

    async def clear(self, channel_id: int) -> None:
        self._store.pop(channel_id, None)
