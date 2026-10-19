# Extending and scaling

## Add an LLM provider

If it has an OpenAI-compatible endpoint (most do), add one entry to `PRESETS` in `vrybot/providers.py`:

```python
"mistral": Preset(
    base_url="https://api.mistral.ai/v1",
    default_model="mistral-small-latest",
    signup_url="https://console.mistral.ai/api-keys",
),
```

That's it. Users can now set `MISTRAL_API_KEY`, `MISTRAL_MODEL` and add `mistral` to `PROVIDERS`. Without code changes, the `custom` provider already covers one extra endpoint.

## Add a memory backend

Implement the three methods of `MemoryBackend` (`vrybot/memory/base.py`) and register it in `create_memory()`:

```python
# vrybot/memory/redis.py
import json
import redis.asyncio as redis
from .base import MemoryBackend, Message

class RedisBackend(MemoryBackend):
    def __init__(self, history_size: int, url: str):
        super().__init__(history_size)
        self.r = redis.from_url(url)

    async def add(self, channel_id: int, role: str, content: str) -> None:
        key = f"vrybot:history:{channel_id}"
        await self.r.rpush(key, json.dumps({"role": role, "content": content}))
        await self.r.ltrim(key, -self.history_size, -1)

    async def history(self, channel_id: int) -> list[Message]:
        return [json.loads(x) for x in await self.r.lrange(f"vrybot:history:{channel_id}", 0, -1)]

    async def clear(self, channel_id: int) -> None:
        await self.r.delete(f"vrybot:history:{channel_id}")

    async def close(self) -> None:
        await self.r.aclose()
```

```python
# vrybot/memory/__init__.py → create_memory()
if settings.memory_backend == "redis":
    return RedisBackend(settings.history_size, os.environ["REDIS_URL"])
```

Add the dependency to `requirements.txt` and a test to `tests/test_memory.py` (the existing tests run against every backend in the fixture).

## Add a feature (cog)

Create a file in `vrybot/cogs/` with a `setup` function. It is loaded automatically on startup and has access to all shared services through `bot`:

```python
# vrybot/cogs/fun.py
from __future__ import annotations
from discord.ext import commands

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def roast(self, ctx: commands.Context, *, target: str):
        """v!roast <thing> — a friendly one-liner about anything."""
        reply = await self.bot.llm.chat([
            {"role": "system", "content": self.bot.persona.render(ctx.me.display_name)},
            {"role": "user", "content": f"{ctx.author.display_name}: give a friendly one-line roast of {target}"},
        ])
        await ctx.reply(reply, mention_author=False)

async def setup(bot):
    await bot.add_cog(Fun(bot))
```

Disable any cog without deleting it: `DISABLED_COGS=fun`.

## Ideas on the roadmap

- **Slash commands** — convert commands to `commands.hybrid_command` and sync the tree in `setup_hook`.
- **Long-term memory** — store facts per user (name, likes) in a separate table and inject a short summary into the prompt.
- **Conversation summaries** — when history gets long, summarize old messages instead of dropping them.
- **Per-server personas** — map guild IDs to persona files.
- **Vision** — pass image attachments to multimodal models.
- **Model lists per provider** — try several models on the same provider before moving to the next (useful where limits are per model, like Groq).

## Scaling

One process comfortably handles dozens of servers; the real limit is the free LLM quota, not the bot.

| Stage | What to change |
|---|---|
| A few servers | Defaults. Add 2–3 provider keys. |
| Busy servers | `MEMORY_BACKEND=sqlite`, raise `USER_COOLDOWN`, restrict `ALLOWED_CHANNEL_IDS`, keep `CHIME_IN_CHANCE` low — every reply costs one request. |
| Quota is the bottleneck | Add providers (or a paid one as last fallback), shorten the persona and `HISTORY_SIZE` to cut tokens per request. |
| Hundreds of servers / multiple processes | Move memory to Redis or Postgres (shared between processes) and enable discord.py sharding with `commands.AutoShardedBot`. Discord requires sharding above 2,500 servers. |
| Many bots with different personalities | Run one container per bot, each with its own `.env` and persona — the code is the same. |
