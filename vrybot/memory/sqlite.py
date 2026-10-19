from __future__ import annotations

import asyncio
import sqlite3
from pathlib import Path

from .base import MemoryBackend, Message

_SCHEMA = """
CREATE TABLE IF NOT EXISTS messages (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_id INTEGER NOT NULL,
    role       TEXT    NOT NULL,
    content    TEXT    NOT NULL,
    created_at TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_messages_channel ON messages(channel_id, id);
"""


class SQLiteBackend(MemoryBackend):
    """Persistent memory in a single file. Survives restarts; no server needed.

    Uses the standard-library sqlite3 in a worker thread so the event loop
    never blocks. Old rows beyond `history_size` are pruned on write.
    """

    def __init__(self, history_size: int, path: Path):
        super().__init__(history_size)
        path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.executescript(_SCHEMA)
        self._lock = asyncio.Lock()

    def _add(self, channel_id: int, role: str, content: str) -> None:
        with self._conn:
            self._conn.execute(
                "INSERT INTO messages (channel_id, role, content) VALUES (?, ?, ?)", (channel_id, role, content)
            )
            self._conn.execute(
                """DELETE FROM messages WHERE channel_id = ? AND id NOT IN (
                       SELECT id FROM messages WHERE channel_id = ? ORDER BY id DESC LIMIT ?)""",
                (channel_id, channel_id, self.history_size),
            )

    def _history(self, channel_id: int) -> list[Message]:
        rows = self._conn.execute(
            "SELECT role, content FROM messages WHERE channel_id = ? ORDER BY id DESC LIMIT ?",
            (channel_id, self.history_size),
        ).fetchall()
        return [{"role": r, "content": c} for r, c in reversed(rows)]

    def _clear(self, channel_id: int) -> None:
        with self._conn:
            self._conn.execute("DELETE FROM messages WHERE channel_id = ?", (channel_id,))

    async def add(self, channel_id: int, role: str, content: str) -> None:
        async with self._lock:
            await asyncio.to_thread(self._add, channel_id, role, content)

    async def history(self, channel_id: int) -> list[Message]:
        async with self._lock:
            return await asyncio.to_thread(self._history, channel_id)

    async def clear(self, channel_id: int) -> None:
        async with self._lock:
            await asyncio.to_thread(self._clear, channel_id)

    async def close(self) -> None:
        self._conn.close()
