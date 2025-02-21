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
        # Create a new thread for the game
        thread = await interaction.channel.create_thread(
            name=f"Partie de Farkle de {interaction.user.display_name}",
            type=discord.ChannelType.public_thread,
            auto_archive_duration=60
        )
        
        # Notify the user about the new thread
        await interaction.response.send_message(
            f"Une nouvelle partie de Farkle a été créée ! Rendez-vous dans {thread.mention} pour jouer !",
            ephemeral=True
        )
        
        # Start the game in the thread
        game_view = FarkleView(self.bot)
        embed = game_view.create_initial_embed()
        view, roll_button, bank_button, end_button = game_view.create_game_buttons()
        await thread.send(embed=embed, view=view)