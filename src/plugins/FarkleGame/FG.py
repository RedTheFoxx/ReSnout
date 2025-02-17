"""Farkle Game"""

import discord
from discord.ext import commands
from discord import app_commands, Interaction

class FarkleGame(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(
        name="farkle", description="Lancer une partie de Farkle"
    )
    async def farkle(self, interaction: Interaction):
        """
        Lancer une partie de Farkle
        """
        await interaction.response.defer(thinking=True, ephemeral=True)
        await interaction.followup.send("Farkle Game is not available yet", ephemeral=True)