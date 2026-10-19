"""Utility commands: help, reset, and owner-only maintenance."""
from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord.ext import commands

if TYPE_CHECKING:
    from ..bot import VryBot


def can_reset():
    """In DMs anyone can reset; in servers it needs Manage Messages."""
    async def predicate(ctx: commands.Context) -> bool:
        if ctx.guild is None:
            return True
        return ctx.channel.permissions_for(ctx.author).manage_messages
    return commands.check(predicate)


class Admin(commands.Cog):
    def __init__(self, bot: VryBot):
        self.bot = bot

    @commands.command(name="help")
    async def help_(self, ctx: commands.Context) -> None:
        """How to talk to the bot."""
        p = self.bot.settings.prefix
        embed = discord.Embed(
            title=f"How to talk to {ctx.me.display_name}",
            description=(
                f"• Mention me: {ctx.me.mention} hi!\n"
                f"• Use the prefix: `{p} hi!`\n"
                "• Reply to one of my messages\n"
                "• Or send me a DM"
            ),
        )
        embed.add_field(name="Commands", value=(
            f"`{p}reset` — clear this channel's conversation (Manage Messages)\n"
            f"`{p}persona` — reload the personality file (owner)\n"
            f"`{p}status` — show providers and memory (owner)"
        ), inline=False)
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command()
    @can_reset()
    async def reset(self, ctx: commands.Context) -> None:
        """Forget the conversation in this channel."""
        await self.bot.memory.clear(ctx.channel.id)
        await ctx.reply(self.bot.settings.msg_reset, mention_author=False)

    @commands.command()
    @commands.is_owner()
    async def persona(self, ctx: commands.Context) -> None:
        """Reload the persona file without restarting."""
        self.bot.persona.reload()
        await ctx.reply(f"Persona reloaded from `{self.bot.persona.path.name}`.", mention_author=False)

    @commands.command()
    @commands.is_owner()
    async def status(self, ctx: commands.Context) -> None:
        """Show which providers and memory backend are active (never shows keys)."""
        s = self.bot.settings
        providers = "\n".join(f"{i}. **{p.name}** — `{p.model}`" for i, p in enumerate(self.bot.llm.providers, 1))
        embed = discord.Embed(title="Status")
        embed.add_field(name="Providers (fallback order)", value=providers or "none", inline=False)
        embed.add_field(name="Memory", value=f"{s.memory_backend} · last {s.history_size} msgs/channel")
        embed.add_field(name="Persona", value=s.persona_file.name)
        embed.add_field(name="Latency", value=f"{self.bot.latency * 1000:.0f} ms")
        await ctx.reply(embed=embed, mention_author=False)


async def setup(bot: VryBot) -> None:
    await bot.add_cog(Admin(bot))
