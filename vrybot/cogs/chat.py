"""The conversation itself: decides when to answer, builds the prompt, sends the reply."""
from __future__ import annotations

import logging
import random
import re
import time
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

from ..llm import AllProvidersFailed
from ..text import split_message, strip_name_prefix

if TYPE_CHECKING:
    from ..bot import VryBot

log = logging.getLogger(__name__)


class Chat(commands.Cog):
    def __init__(self, bot: VryBot):
        self.bot = bot
        self.settings = bot.settings
        self._last_reply_at: dict[int, float] = {}  # user id -> monotonic time

    # ---- helpers -------------------------------------------------------

    def _clean(self, msg: discord.Message) -> str:
        """Turn <@id> mentions into @names, drop the bot's own mention and the prefix."""
        text = msg.content
        for user in msg.mentions:
            replacement = "" if user == self.bot.user else f"@{user.display_name}"
            text = re.sub(rf"<@!?{user.id}>", replacement, text)
        text = text.strip()
        if text.startswith(self.settings.prefix):
            text = text[len(self.settings.prefix):]
        return text.strip()

    def _is_addressed(self, msg: discord.Message) -> bool:
        if isinstance(msg.channel, discord.DMChannel):
            return True
        if self.bot.user in msg.mentions or msg.content.startswith(self.settings.prefix):
            return True
        ref = msg.reference.resolved if msg.reference else None
        return isinstance(ref, discord.Message) and ref.author == self.bot.user

    def _channel_allowed(self, msg: discord.Message) -> bool:
        allowed = self.settings.allowed_channel_ids
        if not allowed or isinstance(msg.channel, discord.DMChannel):
            return True
        parent = getattr(msg.channel, "parent_id", None)  # threads inherit their parent channel
        return msg.channel.id in allowed or parent in allowed

    def _on_cooldown(self, user_id: int) -> bool:
        now = time.monotonic()
        if now - self._last_reply_at.get(user_id, 0) < self.settings.user_cooldown:
            return True
        self._last_reply_at[user_id] = now
        return False

    # ---- listener ------------------------------------------------------

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message) -> None:
        if msg.author.bot or not self._channel_allowed(msg):
            return
        if (await self.bot.get_context(msg)).valid:
            return  # it's a command like v!reset, handled elsewhere

        text = self._clean(msg) or ("[sent an attachment]" if msg.attachments else "")
        if not text:
            return

        # Remember everything said in the channel, so the bot can follow group conversations.
        await self.bot.memory.add(msg.channel.id, "user", f"{msg.author.display_name}: {text}")

        addressed = self._is_addressed(msg)
        if not addressed and random.random() >= self.settings.chime_in_chance:
            return
        if self._on_cooldown(msg.author.id):
            if addressed and self.settings.msg_cooldown:
                await msg.reply(self.settings.msg_cooldown, mention_author=False)
            return

        bot_name = self.bot.user.display_name if self.bot.user else "Bot"
        messages = [
            {"role": "system", "content": self.bot.persona.render(bot_name)},
            *await self.bot.memory.history(msg.channel.id),
        ]

        async with msg.channel.typing():
            try:
                reply = await self.bot.llm.chat(messages)
            except AllProvidersFailed as e:
                log.warning("All providers failed: %s", e)
                await msg.reply(self.settings.msg_error, mention_author=False)
                return

        reply = strip_name_prefix(reply, [bot_name, self.bot.user.name if self.bot.user else ""])
        if not reply:
            return
        await self.bot.memory.add(msg.channel.id, "assistant", reply)

        chunks = split_message(reply)
        await msg.reply(chunks[0], mention_author=False)
        for chunk in chunks[1:]:
            await msg.channel.send(chunk)


async def setup(bot: VryBot) -> None:
    await bot.add_cog(Chat(bot))
