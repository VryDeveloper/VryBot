"""All runtime settings, read once from environment variables (or a .env file).

Every option has a safe default, so the only thing strictly required is
DISCORD_TOKEN plus one LLM provider key. See docs/configuration.md.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent


def _str(name: str, default: str) -> str:
    """Like os.getenv, but an empty value (NAME=) also falls back to the default."""
    return os.getenv(name, "").strip() or default


def _int(name: str, default: int) -> int:
    return int(_str(name, str(default)))


def _float(name: str, default: float) -> float:
    return float(_str(name, str(default)))


def _ids(name: str) -> frozenset[int]:
    raw = os.getenv(name, "")
    return frozenset(int(x) for x in raw.replace(" ", "").split(",") if x)


@dataclass(frozen=True)
class Settings:
    # Discord
    discord_token: str
    prefix: str
    allowed_channel_ids: frozenset[int]  # empty = every channel the bot can see

    # Personality
    persona_file: Path

    # Conversation behavior
    history_size: int
    chime_in_chance: float
    user_cooldown: float

    # Generation
    temperature: float
    max_tokens: int

    # Memory backend
    memory_backend: str
    sqlite_path: Path

    # Canned replies (used when the model can't be reached, etc.)
    msg_error: str
    msg_reset: str
    msg_cooldown: str

    @classmethod
    def from_env(cls) -> Settings:
        load_dotenv(ROOT / ".env")
        persona = Path(_str("PERSONA_FILE", "personas/default.md"))
        sqlite = Path(_str("SQLITE_PATH", "data/memory.db"))
        return cls(
            discord_token=os.getenv("DISCORD_TOKEN", "").strip(),
            prefix=_str("PREFIX", "v!"),
            allowed_channel_ids=_ids("ALLOWED_CHANNEL_IDS"),
            persona_file=persona if persona.is_absolute() else ROOT / persona,
            history_size=_int("HISTORY_SIZE", 30),
            chime_in_chance=_float("CHIME_IN_CHANCE", 0.0),
            user_cooldown=_float("USER_COOLDOWN", 3.0),
            temperature=_float("TEMPERATURE", 0.8),
            max_tokens=_int("MAX_TOKENS", 400),
            memory_backend=_str("MEMORY_BACKEND", "memory").lower(),
            sqlite_path=sqlite if sqlite.is_absolute() else ROOT / sqlite,
            msg_error=_str("MSG_ERROR", "Sorry, I couldn't think of an answer right now. Try again in a moment."),
            msg_reset=_str("MSG_RESET", "Done, I've cleared our conversation in this channel."),
            msg_cooldown=os.getenv("MSG_COOLDOWN", ""),
        )
