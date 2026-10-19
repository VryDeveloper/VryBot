"""Loads the personality (system prompt) from a Markdown file."""
from __future__ import annotations

from pathlib import Path


class Persona:
    def __init__(self, path: Path):
        self.path = path
        self._raw = ""
        self.reload()

    def reload(self) -> None:
        if not self.path.is_file():
            raise FileNotFoundError(
                f"Persona file not found: {self.path}. Set PERSONA_FILE in .env (default: personas/default.md)."
            )
        self._raw = self.path.read_text(encoding="utf-8")

    def render(self, bot_name: str) -> str:
        """The file may use {bot_name}, replaced with the bot's Discord name."""
        return self._raw.replace("{bot_name}", bot_name)
