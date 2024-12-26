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
from player_view import MusicControlButtons
import yt_dlp


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
                await self.info_message.edit(content=f"Statut du lecteur : {content}")
            except discord.NotFound:
                self.info_message = await interaction.channel.send(
                    f"Statut du lecteur : {content}"
                )
        else:
            self.info_message = await interaction.channel.send(
                f"Statut du lecteur : {content}"
            )

    @app_commands.command(
        name="add", description="Ajouter une vidéo ou une playlist YouTube à la file d'attente"
    )
    @app_commands.describe(url="L'URL YouTube à ajouter à la file d'attente.")
    async def add(self, interaction: discord.Interaction, url: str):
        if "youtube.com" not in url:
            await interaction.response.send_message(
                "URL invalide. Veuillez fournir une URL YouTube valide.", ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        try:
            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "noplaylist": False,  # S'assurer que les playlists sont traitées
                "extract_flat": False,  # Ne pas utiliser l'extraction plate pour avoir toutes les entrées
                "ignoreerrors": True,
                "no_color": True
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if "entries" in info:  # C'est une playlist
                    added_count = 0
                    for entry in info["entries"]:
                        if entry and "id" in entry:
                            video_url = f"https://www.youtube.com/watch?v={entry['id']}"
                            self.playlist.append(video_url)
                            added_count += 1
                    
                    await interaction.followup.send(
                        f"{added_count} vidéos de la playlist ont été ajoutées à la file d'attente.", 
                        ephemeral=True
                    )
                else:  # C'est une vidéo unique
                    self.playlist.append(url)
                    position = len(self.playlist)
                    await interaction.followup.send(
                        f"Vidéo ajoutée à la file d'attente en position {position}.", 
                        ephemeral=True
                    )
        except Exception as e:
            await interaction.followup.send(
                f"Une erreur est survenue lors de l'ajout : {str(e)}", 
                ephemeral=True
            )

    @app_commands.command(name="list", description="Afficher la file d'attente.")
    async def list(self, interaction: discord.Interaction):
        if not self.playlist:
            await interaction.response.send_message(
                "La file d'attente est vide.", ephemeral=True
            )
            return

        # Create a string with all the URLs in the playlist
        playlist_str = "\n".join(
            [f"{i+1}. {url}" for i, url in enumerate(self.playlist)]
        )
        await interaction.response.send_message(
            f"File d'attente:\n{playlist_str}", ephemeral=True
        )

    @app_commands.command(name="clear", description="Vider la file d'attente.")
    async def clear(self, interaction: discord.Interaction):
        if not self.playlist:
            await interaction.response.send_message(
                "La file d'attente est déjà vide.", ephemeral=True
            )
            return

        self.playlist.clear()
        await interaction.response.send_message(
            "La file d'attente a été vidée.", ephemeral=True
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
