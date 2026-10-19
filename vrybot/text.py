"""Pure text helpers (no Discord objects), kept separate so they are easy to test."""
from __future__ import annotations

import re

DISCORD_LIMIT = 2000


def strip_name_prefix(text: str, names: list[str]) -> str:
    """Models sometimes start a reply with 'BotName:' mimicking the history format."""
    for name in filter(None, names):
        pattern = rf"^\s*\**\s*{re.escape(name)}\s*\**\s*:\s*\**\s*"
        text = re.sub(pattern, "", text, count=1, flags=re.IGNORECASE)
    return text.strip()


def split_message(text: str, limit: int = DISCORD_LIMIT - 100) -> list[str]:
    """Split long replies on line breaks or spaces so nothing is cut mid-word."""
    parts: list[str] = []
    while len(text) > limit:
        cut = text.rfind("\n", 0, limit)
        if cut < limit // 2:
            cut = text.rfind(" ", 0, limit)
        if cut <= 0:
            cut = limit
        parts.append(text[:cut].rstrip())
        text = text[cut:].lstrip()
    if text:
        parts.append(text)
    return parts
