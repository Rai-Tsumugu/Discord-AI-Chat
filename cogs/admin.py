from __future__ import annotations

from discord.ext import commands
from discord import app_commands, Interaction


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Healthcheck")
    async def ping(self, interaction: Interaction):  # type: ignore[override]
        await interaction.response.send_message("pong")


async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))

