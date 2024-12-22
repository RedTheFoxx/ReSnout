import discord
import yt_dlp


class AudioManager:
    def __init__(self, bot):
        self.bot = bot
        self.voice_clients = {}

    async def connect_to_voice_channel(self, interaction: discord.Interaction):
        if not interaction.user.voice:
            await interaction.response.send_message(
                "Vous n'êtes pas connecté à aucun salon vocal.", ephemeral=True
            )
            return None

        voice_channel = interaction.user.voice.channel
        if (
            interaction.guild.id not in self.voice_clients
            or not self.voice_clients[interaction.guild.id].is_connected()
        ):
            try:
                voice_client = await voice_channel.connect()
                self.voice_clients[interaction.guild.id] = voice_client
                return voice_client
            except Exception as e:
                await interaction.response.send_message(
                    f"Échec de la connexion au salon vocal : {e}", ephemeral=True
                )
                return None
        else:
            return self.voice_clients[interaction.guild.id]

    async def play_music(self, interaction: discord.Interaction, url: str):
        voice_client = await self.connect_to_voice_channel(interaction)
        if not voice_client:
            return

        try:
            ydl_opts = {
                "format": "bestaudio/best",
                "noplaylist": True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if "entries" in info:
                    info = info["entries"][0]
                audio_url = info["url"]

            ffmpeg_options = {"options": "-vn"}
            voice_client.play(
                discord.FFmpegPCMAudio(audio_url, **ffmpeg_options),
                after=lambda e: print(f"Player error: {e}") if e else None,
            )
            await interaction.response.send_message(
                f"Lecture en cours : {info['title']}"
            )
        except Exception as e:
            await interaction.response.send_message(
                f"Erreur de lecture de la musique : {e}", ephemeral=True
            )

    async def stop_music(self, interaction: discord.Interaction):
        if (
            interaction.guild.id in self.voice_clients
            and self.voice_clients[interaction.guild.id].is_connected()
        ):
            await self.voice_clients[interaction.guild.id].disconnect()
            del self.voice_clients[interaction.guild.id]
            await interaction.response.send_message("Lecture arrêtée.", ephemeral=True)
        else:
            await interaction.response.send_message(
                "Aucune musique en cours de lecture.", ephemeral=True
            )

    async def pause_music(self, interaction: discord.Interaction):
        if (
            interaction.guild.id in self.voice_clients
            and self.voice_clients[interaction.guild.id].is_playing()
        ):
            self.voice_clients[interaction.guild.id].pause()
            await interaction.response.send_message("Musique en pause.", ephemeral=True)
        else:
            await interaction.response.send_message(
                "Aucune musique en cours de lecture.", ephemeral=True
            )

    async def resume_music(self, interaction: discord.Interaction):
        if (
            interaction.guild.id in self.voice_clients
            and self.voice_clients[interaction.guild.id].is_paused()
        ):
            self.voice_clients[interaction.guild.id].resume()
            await interaction.response.send_message("Lecture reprise.", ephemeral=True)
        else:
            await interaction.response.send_message(
                "Aucune musique en pause.", ephemeral=True
            )
