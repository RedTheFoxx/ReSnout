"""
MarvelStats is a plugin that implements Marvel Rivals statistics from your character directly into Discord.
It makes use of the Tracker API.
(Profile fetch example : https://api.tracker.gg/api/v2/marvel-rivals/standard/profile/ign/RedFox?)
Check its bio in its .toml companion file.
"""

import sys
import os

# Add to python path to use local plugin files dependencies
sys.path.append(os.path.dirname(__file__))

import discord
from discord import app_commands
from discord.ext import commands
from web_explorer import get_player_macro_stats
from stats_view import create_stats_embed, create_error_embed

class MarvelStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        try:
            # Things to initialize
            pass
        except Exception as e:
            raise commands.ExtensionFailed("MarvelStats", e)

    @app_commands.command(name="stats", description="Afficher les statistiques d'un joueur Marvel Rivals")
    @app_commands.describe(username="Le pseudo Marvel Rivals du joueur")
    async def marvelstats(self, interaction: discord.Interaction, username: str):
        """
        Fetch and display Marvel Rivals statistics for a given username.
        """
        await interaction.response.defer(thinking=True, ephemeral=True)
        await interaction.followup.send("Snout fait ses recherches ...", ephemeral=True)
        
        try:
            # Construire l'URL de l'API
            url = f"https://tracker.gg/marvel-rivals/profile/ign/{username}/overview"
            
            # Récupérer les statistiques
            stats = get_player_macro_stats(url)
            
            # Vérifier si les stats sont valides
            if not stats or stats.get("matches_played") == 0:
                embed = create_error_embed(username, "invalid_username")
            else:
                # Créer et envoyer l'embed
                embed = create_stats_embed(
                    username=username,
                    matches_played=stats.get("matches_played", 0),
                    playtime=stats.get("playtime", "0h")
                )
                
        except Exception as e:
            # En cas d'erreur inattendue
            embed = create_error_embed(username, "api_error")
            
        await interaction.followup.send(embed=embed)