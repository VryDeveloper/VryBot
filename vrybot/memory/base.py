"""Memory backend interface.

The bot only talks to this interface, so swapping storage (RAM, SQLite,
Redis, Postgres...) never touches the chat logic. All methods are async so
network-backed stores fit without changes.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypedDict


class Message(TypedDict):
    role: str      # "user" or "assistant"
    content: str


class MemoryBackend(ABC):
    def __init__(self, history_size: int):
        self.history_size = history_size

    @abstractmethod
    async def add(self, channel_id: int, role: str, content: str) -> None: ...

    @abstractmethod
    async def history(self, channel_id: int) -> list[Message]:
        """Most recent `history_size` messages for the channel, oldest first."""

    @abstractmethod
    async def clear(self, channel_id: int) -> None: ...

    async def close(self) -> None:  # optional hook
        return None
