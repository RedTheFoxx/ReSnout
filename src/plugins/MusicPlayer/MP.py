import sys
import os
# Add to python path to use local plugin files dependencies
sys.path.append(os.path.dirname(__file__))

import discord
from discord import app_commands
from discord.ext import commands

from audio_stream import AudioManager


class MusicPlayer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.audio_manager = AudioManager(bot)

    @app_commands.command(name="play", description="Lire le son d'une vidéo YouTube")
    @app_commands.describe(url="L'URL YouTube à lire.")
    async def play(self, interaction: discord.Interaction, url: str):
        if "youtube.com" not in url:
            await interaction.response.send_message(
                "URL invalide. Veuillez fournir une URL YouTube valide.", ephemeral=True
            )
            return
        await self.audio_manager.play_music(interaction, url)

    @app_commands.command(
        name="stop", description="Arrêter la musique en cours de lecture."
    )
    async def stop(self, interaction: discord.Interaction):
        await self.audio_manager.stop_music(interaction)

    @app_commands.command(
        name="pause", description="Mettre en pause la musique en cours de lecture."
    )
    async def pause(self, interaction: discord.Interaction):
        await self.audio_manager.pause_music(interaction)

    @app_commands.command(
        name="resume", description="Reprendre la lecture de la musique en pause."
    )
    async def resume(self, interaction: discord.Interaction):
        await self.audio_manager.resume_music(interaction)


async def setup(bot):
    await bot.add_cog(MusicPlayer(bot))
