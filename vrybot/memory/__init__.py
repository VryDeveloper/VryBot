"""Memory backends. Pick one with MEMORY_BACKEND in .env."""
from __future__ import annotations

from ..config import Settings
from .base import MemoryBackend, Message
from .in_memory import InMemoryBackend
from .sqlite import SQLiteBackend

__all__ = ["MemoryBackend", "Message", "InMemoryBackend", "SQLiteBackend", "create_memory"]


def create_memory(settings: Settings) -> MemoryBackend:
    if settings.memory_backend == "memory":
        return InMemoryBackend(settings.history_size)
    if settings.memory_backend == "sqlite":
        return SQLiteBackend(settings.history_size, settings.sqlite_path)
    raise ValueError(f"Unknown MEMORY_BACKEND '{settings.memory_backend}'. Use 'memory' or 'sqlite'.")
