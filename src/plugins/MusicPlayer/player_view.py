import discord


class MusicControlButtons(discord.ui.View):
    """
    A Discord UI View that provides interactive buttons for music playback control.
    Includes buttons for play/pause, stop, and skip functionality.
    """

    def __init__(self, music_player):
        """
        Initialize the music control buttons view.
        
        Args:
            music_player: The MusicPlayer instance these controls are attached to
        """
        super().__init__(timeout=None)
        self.music_player = music_player
        self.is_paused = False

    @discord.ui.button(label="⏸️ Pause", style=discord.ButtonStyle.secondary)
    async def pause_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """
        Handle the pause button click event.
        Pauses the currently playing track and updates button states.
        
        Args:
            interaction: The Discord interaction that triggered this button
            button: The button that was clicked
        """
        await interaction.response.defer()

        if not self.is_paused:  # Check if the music is already paused
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
        """
        Handle the play/resume button click event.
        Resumes playing a paused track and updates button states.
        
        Args:
            interaction: The Discord interaction that triggered this button
            button: The button that was clicked
        """
        await interaction.response.defer()

        if self.is_paused:  # Check if the music is paused before resuming
            await self.music_player.audio_manager.resume_music(interaction)
            self.is_paused = False
            button.disabled = True
            self.pause_button.disabled = False
            await self.music_player.update_info_message(
                interaction, "Lecture en cours ..."
            )

        try:
            await interaction.message.edit(view=self)
        except discord.NotFound:
            pass

    @discord.ui.button(label="⏹️ Stop", style=discord.ButtonStyle.danger)
    async def stop_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """
        Handle the stop button click event.
        Stops playback, disconnects from voice, and disables all buttons.
        
        Args:
            interaction: The Discord interaction that triggered this button
            button: The button that was clicked
        """
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
        """
        Handle the skip button click event.
        Skips the current track and plays the next item in queue if available.
        
        Args:
            interaction: The Discord interaction that triggered this button
            button: The button that was clicked
        """
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
        await self.music_player.update_info_message(
            interaction, "Lecture de la vidéo suivante ..."
        )
