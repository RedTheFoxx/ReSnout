"""Farkle Game"""

import sys
import os

# Add to python path to use local plugin files dependencies
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

import discord
from discord.ext import commands
from discord import app_commands, Interaction
from plugins.FarkleGame.farkle_view import FarkleView

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
        game_view = FarkleView(self.bot)
        embed = game_view.create_initial_embed()
        view, roll_button, bank_button, end_button = game_view.create_game_buttons()
        
        await interaction.response.send_message(embed=embed, view=view)