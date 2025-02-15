"""Farkle Game is a dice game where the player rolls a combination of dice to try and get as high of a score as possible.
It is designed to be played with 6 dice. Check the rules in the associated farklerules.md file."""

import discord
from discord import app_commands
from discord.ext import commands

class FarkleGame(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="farkle", description="Lancer une partie de Farkle contre l'IA"
    )
    async def farkle(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True, ephemeral=True)
        await interaction.followup.send("Farkle game is not implemented yet.")
