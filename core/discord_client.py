from __future__ import annotations

import logging
from typing import Any


def create_client(settings: Any):
    import discord
    from discord.ext import commands

    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix="/", intents=intents)
    log = logging.getLogger("discord_client")

    from state import MemoryState
    from handlers.text import handle_text
    from handlers.text_with_image import handle_text_with_image
    from utils.chunk import chunk_2000

    state = MemoryState()

    @bot.event
    async def on_ready():  # type: ignore[no-redef]
        log.info("Logged in as %s (id=%s)", bot.user, bot.user.id if bot.user else "?")
        try:
            synced = await bot.tree.sync()
            log.info("Synced %d application command(s)", len(synced))
        except Exception as e:  # pragma: no cover
            log.warning("Slash command sync failed: %s", e)

    @bot.event
    async def on_message(message: discord.Message):  # type: ignore[name-defined]
        if message.author == bot.user:
            return
        try:
            if message.attachments:
                first = message.attachments[0]
                image_src = first.url
                reply = handle_text_with_image(message.content or "", image_src)
            else:
                reply = handle_text(message, state)
            for part in chunk_2000(reply):
                await message.channel.send(part)
            # Allow command processing for prefix commands if added later
            await bot.process_commands(message)
        except Exception as e:  # pragma: no cover - runtime safety
            log.exception("Failed to handle message: %s", e)
            await message.channel.send("Sorry, something went wrong.")

    return bot
