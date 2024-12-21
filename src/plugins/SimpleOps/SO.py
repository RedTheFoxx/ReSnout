"""
SimpleOps is a plugin used to perform simple operations with the bot.
Check its bio in its .toml companion file.
"""

import discord
from discord import app_commands
from discord.ext import commands
import random


class SimpleOps(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="gw", description="Tester la latence de la gateway.")
    async def gw(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)  # Convert to ms and round
        await interaction.response.send_message(f"Latence de la gateway : {latency}ms")

    @app_commands.command(name="roll", description="Lancer des dés avec un nombre de faces de votre choix.")
    @app_commands.describe(
        dices="Nombre de dés à lancer",
        faces="Nombre de faces des déss",
        private="Envoyer le résultat uniquement à toi"
    )
    async def roll(self, interaction: discord.Interaction, dices: int, faces: int, private: bool = False):
        if dices <= 0 or faces <= 0:
            await interaction.response.send_message("Le nombre de dés et de faces doit être supérieur à 0.", ephemeral=True)
            return

        if dices > 100 or faces > 1000:
            await interaction.response.send_message("Vous ne pouvez lancer que 1000 dés de 100 faces maximum.", ephemeral=True)
            return

        rolls = [random.randint(1, faces) for _ in range(dices)]
        total = sum(rolls)
        rolls_str = " ; ".join([str(roll) for roll in rolls])
        message = f"Je lance **{dices}d{faces}** = **{total}** ({rolls_str})"
        await interaction.response.send_message(message, ephemeral=private)
