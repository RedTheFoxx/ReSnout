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
from web_explorer import get_stats
from stats_view import (
    create_stats_embed,
    create_error_embed,
    create_heroes_embed,
    create_current_rank_embed,
    create_season_best_embed,
    create_all_time_best_embed,
)


class MarvelStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        try:
            # Things to initialize
            pass
        except Exception as e:
            raise commands.ExtensionFailed("MarvelStats", e)

    @app_commands.command(
        name="stats", description="Afficher les statistiques d'un joueur Marvel Rivals"
    )
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
            stats = get_stats(url)

            # Vérifier si les stats sont valides
            if not stats or stats.get("matches_played") == 0:
                embed = create_error_embed(username, "invalid_username")
                await interaction.followup.send(embed=embed)
            else:
                # Créer et envoyer l'embed principal
                embed = create_stats_embed(
                    username=username,
                    matches_played=stats.get("matches_played", 0),
                    playtime=stats.get("playtime", "0h"),
                    kills=stats.get("kills", 0),
                    kda_ratio=stats.get("kda_ratio", 0.0),
                    wins=stats.get("wins", 0),
                    win_percentage=stats.get("win_percentage", 0.0),
                    season_number=stats.get("season_number", 0),
                    season_name=stats.get("season_name", ""),
                )

                # Préparer tous les embeds
                embeds = [embed]

                # Ajouter l'embed des héros si disponible
                if stats.get("top_heroes"):
                    heroes_embed = create_heroes_embed(username, stats["top_heroes"])
                    embeds.append(heroes_embed)

                # Ajouter les embeds de rang si disponibles
                if stats.get("current_rank"):
                    current_rank_embed = create_current_rank_embed(
                        username, stats["current_rank"]
                    )
                    embeds.append(current_rank_embed)

                if stats.get("season_best"):
                    season_best_embed = create_season_best_embed(
                        username, stats["season_best"]
                    )
                    embeds.append(season_best_embed)

                if stats.get("all_time_best"):
                    all_time_best_embed = create_all_time_best_embed(
                        username, stats["all_time_best"]
                    )
                    embeds.append(all_time_best_embed)

                # Envoyer tous les embeds en une seule fois
                await interaction.followup.send(embeds=embeds)

        except Exception as e:
            # En cas d'erreur inattendue
            embed = create_error_embed(username, "api_error")
            await interaction.followup.send(embed=embed)
