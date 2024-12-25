import sys
import os
from collections import deque
from typing import Optional

# Add to python path to use local plugin files dependencies
sys.path.append(os.path.dirname(__file__))

import discord
from discord import app_commands
from discord.ext import commands

from streaming import AudioManager


class MusicControlButtons(discord.ui.View):
    def __init__(self, music_player):
        super().__init__(timeout=None)
        self.music_player = music_player
        self.is_paused = False

    @discord.ui.button(label="⏸️ Pause", style=discord.ButtonStyle.secondary)
    async def pause_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if not self.is_paused:
            await self.music_player.audio_manager.pause_music(interaction)
            button.label = "▶️ Resume"
            self.is_paused = True
        else:
            await self.music_player.audio_manager.resume_music(interaction)
            button.label = "⏸️ Pause"
            self.is_paused = False
        await interaction.followup.edit_message(
            message_id=interaction.message.id, view=self
        )

    @discord.ui.button(label="⏹️ Stop", style=discord.ButtonStyle.danger)
    async def stop_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.music_player.audio_manager.stop_music(interaction)
        # Disable all buttons after stopping
        for child in self.children:
            child.disabled = True
        await interaction.followup.edit_message(
            message_id=interaction.message.id, view=self
        )


class MusicPlayer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.audio_manager = AudioManager(bot)
        self.playlist = deque()  # File d'attente pour les URLs

    @app_commands.command(
        name="add", description="Ajouter une vidéo YouTube à la file d'attente"
    )
    @app_commands.describe(url="L'URL YouTube à ajouter à la file d'attente.")
    async def add(self, interaction: discord.Interaction, url: str):
        if "youtube.com" not in url:
            await interaction.response.send_message(
                "URL invalide. Veuillez fournir une URL YouTube valide.", ephemeral=True
            )
            return

        self.playlist.append(url)
        position = len(self.playlist)
        await interaction.response.send_message(
            f"Vidéo ajoutée à la file d'attente en position {position}.", ephemeral=True
        )

    @app_commands.command(name="play", description="Lire le son d'une vidéo YouTube")
    @app_commands.describe(url="L'URL YouTube à lire (optionnel).")
    async def play(self, interaction: discord.Interaction, url: Optional[str] = None):
        # Tell Discord GW that the response will be long (music will play)
        await interaction.response.defer(ephemeral=True)

        if url is None:
            if not self.playlist:
                await interaction.followup.send(
                    "La file d'attente est vide. Veuillez fournir une URL ou ajouter des vidéos avec /add.",
                    ephemeral=True,
                )
                return
            url = self.playlist.popleft()

        elif "youtube.com" not in url:
            await interaction.followup.send(
                "URL invalide. Veuillez fournir une URL YouTube valide.", ephemeral=True
            )
            return

        # Build the buttons for the music player
        view = MusicControlButtons(self)
        await self.audio_manager.play_music(interaction, url)
        await interaction.followup.send(
            "Contrôles de lecture:", view=view, ephemeral=True
        )

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
