"""Bot entry point: wires settings, LLM, memory and persona together, then loads cogs."""
from __future__ import annotations

import logging
import os
import pkgutil

import discord
from discord.ext import commands

from . import cogs
from .config import Settings
from .llm import LLMClient
from .memory import MemoryBackend, create_memory
from .persona import Persona
from .providers import load_providers

log = logging.getLogger("vrybot")


class VryBot(commands.Bot):
    """Shared services live on the bot object so every cog can reach them."""

    def __init__(self, settings: Settings, llm: LLMClient, memory: MemoryBackend, persona: Persona):
        intents = discord.Intents.default()
        intents.message_content = True  # must also be enabled in the Developer Portal
        super().__init__(command_prefix=settings.prefix, intents=intents, help_command=None)
        self.settings = settings
        self.llm = llm
        self.memory = memory
        self.persona = persona

    async def setup_hook(self) -> None:
        disabled = {c.strip() for c in os.getenv("DISABLED_COGS", "").split(",") if c.strip()}
        for mod in pkgutil.iter_modules(cogs.__path__):
            if mod.name.startswith("_") or mod.name in disabled:
                continue
            await self.load_extension(f"{cogs.__name__}.{mod.name}")
            log.info("Loaded cog: %s", mod.name)

    async def on_ready(self) -> None:
        names = ", ".join(f"{p.name}:{p.model}" for p in self.llm.providers)
        log.info("Online as %s | providers: %s | memory: %s", self.user, names, self.settings.memory_backend)
        await self.change_presence(activity=discord.Game(f"{self.settings.prefix}help"))

    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        if isinstance(error, commands.CommandNotFound):
            return  # "v! hello" is a chat message, not a command
        if isinstance(error, (commands.CheckFailure, commands.NotOwner)):
            await ctx.reply("You don't have permission to use that command.", mention_author=False)
            return
        log.exception("Command error", exc_info=error)

    async def close(self) -> None:
        await self.memory.close()
        await super().close()


def build_bot() -> VryBot:
    settings = Settings.from_env()  # also loads .env into the environment
    if not settings.discord_token:
        raise SystemExit("DISCORD_TOKEN is missing. Copy .env.example to .env and fill it in.")
    llm = LLMClient(load_providers(), temperature=settings.temperature, max_tokens=settings.max_tokens)
    return VryBot(settings, llm, create_memory(settings), Persona(settings.persona_file))


def main() -> None:
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
    )
    bot = build_bot()
    bot.run(bot.settings.discord_token, log_handler=None)
