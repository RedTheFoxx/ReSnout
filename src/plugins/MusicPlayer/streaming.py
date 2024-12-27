import discord
import yt_dlp


class YTDLSource(discord.PCMVolumeTransformer):
    """
    A custom audio source class for YouTube audio playback.
    Handles downloading and transforming YouTube audio for Discord playback.
    """

    def __init__(self, source, *, data, volume=0.5):
        """
        Initialize the YTDLSource.
        
        Args:
            source: The audio source to transform
            data: Metadata about the YouTube video
            volume: The initial volume level (0.0 to 1.0)
        """
        super().__init__(source, volume)
        self.data = data
        self.title = data.get("title")

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        """
        Create a YTDLSource instance from a YouTube URL.
        
        Args:
            url: The YouTube URL to download/stream from
            loop: Optional; The event loop to use
            stream: Whether to stream the audio instead of downloading
            
        Returns:
            A new YTDLSource instance configured for the given URL
        """
        ydl_opts = {"format": "bestaudio/best", "noplaylist": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            data = ydl.extract_info(url, download=not stream)
            if "entries" in data:
                data = data["entries"][0]
            filename = data["url"] if stream else ydl.prepare_filename(data)
            return cls(discord.FFmpegPCMAudio(filename), data=data)


class AudioManager:
    """
    Manages audio playback across different Discord voice channels.
    Handles connecting to voice channels and controlling audio playback.
    """

    def __init__(self, bot):
        """
        Initialize the AudioManager.
        
        Args:
            bot: The Discord bot instance this manager is attached to
        """
        self.bot = bot
        self.voice_clients = {}
        self.skip_flag = False

    async def connect_to_voice_channel(self, interaction: discord.Interaction):
        """
        Connect to a voice channel or return existing connection.
        
        Args:
            interaction: The Discord interaction that triggered this connection request
            
        Returns:
            The voice client if connection successful, None otherwise
        """
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
        """
        Play audio from a YouTube URL in a voice channel.
        
        Args:
            interaction: The Discord interaction that triggered this playback request
            url: The YouTube URL to play
        """
        # Check if user is in a voice channel
        if not interaction.user.voice:
            if interaction.response.is_done():
                await interaction.followup.send(
                    "Vous devez être dans un salon vocal pour utiliser cette commande.",
                    ephemeral=True,
                )
            else:
                await interaction.response.send_message(
                    "Vous devez être dans un salon vocal pour utiliser cette commande.",
                    ephemeral=True,
                )
            return

        channel = interaction.user.voice.channel
        voice_client = await self.connect_to_voice_channel(interaction)
        if not voice_client:
            return

        # Download and play the audio
        try:
            source = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            if voice_client.is_playing():
                voice_client.stop()
            self.skip_flag = False
            voice_client.play(source, after=lambda e: self.after_play(interaction, e))

            # Use followup if interaction is already responded
            if interaction.response.is_done():
                await interaction.followup.send(
                    f"Lecture en cours : {source.title}", ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    f"Lecture en cours : {source.title}", ephemeral=True
                )

        except Exception as e:
            if interaction.response.is_done():
                await interaction.followup.send(
                    f"Une erreur est survenue lors de la lecture : {str(e)}",
                    ephemeral=True,
                )
            else:
                await interaction.response.send_message(
                    f"Une erreur est survenue lors de la lecture : {str(e)}",
                    ephemeral=True,
                )

    def after_play(self, interaction: discord.Interaction, error):
        """
        Callback function called after a track finishes playing.
        Handles errors and plays the next track in queue if available.
        
        Args:
            interaction: The Discord interaction that triggered the original playback
            error: Any error that occurred during playback
        """
        if error:
            print(f"Erreur lors de la lecture : {error}")
        elif self.skip_flag:
            return
        else:
            # Get the music player instance from the bot
            music_player = self.bot.get_cog("MusicPlayer")
            if music_player and music_player.playlist:
                next_url = music_player.playlist.popleft()
                self.bot.loop.create_task(self.play_music(interaction, next_url))
                self.bot.loop.create_task(music_player.update_info_message(interaction, "Lecture de la vidéo suivante ..."))
            else:
                self.bot.loop.create_task(music_player.update_info_message(interaction, "File d'attente terminée"))

    async def skip_music(self, interaction: discord.Interaction):
        """
        Skip the currently playing track.
        
        Args:
            interaction: The Discord interaction that triggered this skip request
        """
        voice_client = self.voice_clients.get(interaction.guild.id)
        if voice_client and voice_client.is_playing():
            self.skip_flag = True
            voice_client.stop()

    async def stop_music(self, interaction: discord.Interaction):
        """
        Stop playback and disconnect from voice channel.
        
        Args:
            interaction: The Discord interaction that triggered this stop request
        """
        voice_client = self.voice_clients.get(interaction.guild.id)
        if voice_client and voice_client.is_connected():
            await voice_client.disconnect()
            del self.voice_clients[interaction.guild.id]
        else:
            await interaction.response.send_message(
                "Aucune musique en cours de lecture.", ephemeral=True
            )

    async def pause_music(self, interaction: discord.Interaction):
        """
        Pause the currently playing track.
        
        Args:
            interaction: The Discord interaction that triggered this pause request
        """
        voice_client = self.voice_clients.get(interaction.guild.id)
        if voice_client and voice_client.is_playing():
            voice_client.pause()
        else:
            await interaction.response.send_message(
                "Aucune musique en cours de lecture.", ephemeral=True
            )

    async def resume_music(self, interaction: discord.Interaction):
        """
        Resume playing a paused track.
        
        Args:
            interaction: The Discord interaction that triggered this resume request
        """
        voice_client = self.voice_clients.get(interaction.guild.id)
        if voice_client and voice_client.is_paused():
            voice_client.resume()
        else:
            await interaction.response.send_message(
                "Aucune musique en pause.", ephemeral=True
            )
