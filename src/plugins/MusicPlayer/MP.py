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
        await interaction.response.defer()
        
        if not self.is_paused: # Check if the music is already paused
            await self.music_player.audio_manager.pause_music(interaction)
            self.is_paused = True
            button.disabled = True
            self.resume_button.disabled = False
            await self.music_player.update_info_message(interaction, "Lecture en pause")
        
        try:
            await interaction.message.edit(view=self)
        except discord.NotFound:
            pass

    @discord.ui.button(label="▶️ Play", style=discord.ButtonStyle.success)
    async def resume_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer()
        
        if self.is_paused: # Check if the music is paused before resuming
            await self.music_player.audio_manager.resume_music(interaction)
            self.is_paused = False
            button.disabled = True
            self.pause_button.disabled = False
            await self.music_player.update_info_message(interaction, "Lecture en cours ...")
        
        try:
            await interaction.message.edit(view=self)
        except discord.NotFound:
            pass

    @discord.ui.button(label="⏹️ Stop", style=discord.ButtonStyle.danger)
    async def stop_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer()
        
        await self.music_player.audio_manager.stop_music(interaction)
        await self.music_player.delete_info_message()
        # Disable all buttons after stopping
        for child in self.children:
            child.disabled = True
            
        try:
            await interaction.message.edit(view=self)
        except discord.NotFound:
            pass

    @discord.ui.button(label="⏭️ Skip", style=discord.ButtonStyle.primary)
    async def skip_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer()
        
        if not self.music_player.playlist:
            try:
                await interaction.followup.send(
                    "Il n'y a rien en file d'attente.", ephemeral=True
                )
            except discord.NotFound:
                pass
            return

        # Stop the current song and play the next one
        await self.music_player.audio_manager.skip_music(interaction)
        next_url = self.music_player.playlist.popleft()
        await self.music_player.audio_manager.play_music(interaction, next_url)
        await self.music_player.update_info_message(interaction, "Lecture de la vidéo suivante ...")

class MusicPlayer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.audio_manager = AudioManager(bot)
        self.playlist = deque()  # File d'attente pour les URLs
        self.info_message = None  # Message d'information qui sera mis à jour

    async def delete_info_message(self):
        if self.info_message:
            try:
                await self.info_message.delete()
            except discord.NotFound:
                pass
            finally:
                self.info_message = None

    async def update_info_message(self, interaction: discord.Interaction, content: str):
        if self.info_message:
            try:
                await self.info_message.edit(content=f"Information : {content}")
            except discord.NotFound:
                self.info_message = await interaction.channel.send(f"Information : {content}")
        else:
            self.info_message = await interaction.channel.send(f"Information : {content}")

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
        await self.update_info_message(interaction, "Lecture en cours ...")

    @app_commands.command(
        name="stop", description="Arrêter la vidéo en cours de lecture."
    )
    async def stop(self, interaction: discord.Interaction):
        await self.audio_manager.stop_music(interaction)
        await self.delete_info_message()

    @app_commands.command(
        name="pause", description="Mettre en pause la vidéo en cours de lecture."
    )
    async def pause(self, interaction: discord.Interaction):
        await self.audio_manager.pause_music(interaction)
        await self.update_info_message(interaction, "Lecture en pause")

    @app_commands.command(
        name="resume", description="Reprendre la lecture de la vidéo en pause."
    )
    async def resume(self, interaction: discord.Interaction):
        await self.audio_manager.resume_music(interaction)
        await self.update_info_message(interaction, "Lecture en cours ...")

    @app_commands.command(
        name="skip", description="Passer à la vidéo suivante dans la file d'attente."
    )
    async def skip(self, interaction: discord.Interaction):
        if not self.playlist:
            await interaction.response.send_message(
                "Il n'y a rien en file d'attente.", ephemeral=True
            )
            return

        # Stop the current song and play the next one
        await self.audio_manager.skip_music(interaction)
        next_url = self.playlist.popleft()
        await self.audio_manager.play_music(interaction, next_url)
        await self.update_info_message(interaction, "Lecture de la vidéo suivante ...")


async def setup(bot):
    await bot.add_cog(MusicPlayer(bot))
