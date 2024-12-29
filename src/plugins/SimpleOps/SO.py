"""
SimpleOps is a plugin used to perform simple operations with the bot.
Check its bio in its .toml companion file.
"""

# Add to python path to use local plugin files dependencies
import os
import sys
sys.path.append(os.path.dirname(__file__))

import discord
from discord import app_commands
from discord.ext import commands

from dice_parser import DiceParser
from dice_viewer import DiceEmbed


class SimpleOps(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="gw", description="Tester la latence de la gateway.")
    async def gw(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)  # Convert to ms and round
        await interaction.response.send_message(f"Latence de la gateway : {latency}ms")

    @app_commands.command(
        name="dice", description="Lancer des dés en notation JDR (ex: 2d6+3d4+5)"
    )
    @app_commands.describe(
        dice_str="Notation de lancer de dés (ex: 2d6+3d4+5)",
        private="Envoyer le résultat uniquement à toi",
    )
    async def dice(
        self, interaction: discord.Interaction, dice_str: str, private: bool = False
    ):
        try:
            # Parse the dice string then roll the dice
            dice_groups, modifiers = DiceParser.parse(dice_str)
            dice_results = DiceParser.roll(dice_groups)
            total = DiceParser.calculate_total(dice_results, modifiers)

            # Make it beautiful to display
            embed = DiceEmbed.build_dice_embed(
                dice_groups, dice_results, modifiers, total
            )
            await interaction.response.send_message(embed=embed, ephemeral=private)

        except Exception as e:
            await interaction.response.send_message(
                f"Format de dés invalide. Utilisez la notation JDR (ex: 2d6+3d4+5)",
                ephemeral=True,
            )
