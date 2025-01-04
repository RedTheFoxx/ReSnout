"""
Cemantix is a plugin that implements the Cemantix word game through Discord.
Check its bio in its .toml companion file.
"""

# TODO: Bake the database system to store the players and their scores
# TODO: Add a simple leaderboard (less try to find a word = the better) + all of his commands and features
# TODO: Prepare an ELO system with rankings like in Overwatch!

import sys
import os
import asyncio
import time

# Add to python path to use local plugin files dependencies
sys.path.append(os.path.dirname(__file__))

import discord
from discord import app_commands
from discord.ext import commands
from cemantix_core import GameManager
from cemantix_view import GameView


class CemantixGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        try:
            self.game = GameManager()
            self.view = GameView()
            self.history = {}
            self.active_games = {}
            self.game_timers = {}
            self.game_start_times = {}
            self.game_attempts = {}
        except Exception as e:
            raise commands.ExtensionFailed("CemantixGame", e)

        # Register the message event handler once
        self.bot.event(self.on_message)

    @app_commands.command(name="cem", description="Démarrer une partie de Cemantix")
    async def cem(self, interaction: discord.Interaction):
        await self.start_new_game(interaction)

    async def start_new_game(self, interaction: discord.Interaction):
        # Create a private thread with the user
        thread = await interaction.channel.create_thread(
            name=f"Cemantix - {interaction.user.name} #{len([t for t in self.active_games.values() if t.startswith(str(interaction.user.id))]) + 1}",
            type=discord.ChannelType.private_thread,
        )
        await thread.add_user(interaction.user)

        # Initialize game state for this thread
        self.history[thread.id] = []
        self.active_games[thread.id] = str(interaction.user.id)
        self.game_start_times[thread.id] = time.time()
        self.game_attempts[thread.id] = 0

        # Create initial embeds
        embed = self.view.create_initial_embed()
        history_embed = self.view.create_history_embed(self.history[thread.id])

        # Send initial messages
        embed_message = await thread.send(embed=embed)
        history_message = await thread.send(embed=history_embed)

        # Start first game
        self.game.start_new_game()
        await interaction.response.send_message(
            f"Partie créée ! Rendez-vous dans le fil privé {thread.mention}.",
            ephemeral=True,
        )

        # Start timer for the game
        self.game_timers[thread.id] = asyncio.create_task(
            self.close_game_timer(thread.id, interaction.user.id)
        )

    async def close_game_timer(self, thread_id, user_id):
        await asyncio.sleep(300)  # 5 minutes before auto closing the game
        await self.close_game(thread_id, user_id)

    async def close_game(self, thread_id, user_id):
        thread = self.bot.get_channel(thread_id)
        if thread:
            # Calculate game duration
            start_time = self.game_start_times.get(thread_id)
            if start_time:
                end_time = time.time()
                duration = end_time - start_time
                minutes = int(duration // 60)
                seconds = int(duration % 60)
                duration_str = f"{minutes} minutes et {seconds} secondes"
            else:
                duration_str = "Temps inconnu"

            # Get the number of attempts
            attempts = self.game_attempts.get(thread_id, 0)

            # Get the parent channel (where /cem was invoked)
            parent_channel = thread.parent

            # Create and send the summary embed to the parent channel
            if parent_channel:
                summary_embed = self.view.create_summary_embed(attempts, duration_str)
                await parent_channel.send(embed=summary_embed)

            # Delete the thread
            await thread.delete()

        # Finally, clean up game data
        self.cleanup_game_data(thread_id)

    async def on_message(self, message):
        """Handle messages in active game threads"""
        if not message.author.bot and message.channel.id in self.history:
            thread_id = message.channel.id
            word = message.content.lower().strip()

            if not self.game.is_word_valid(word):
                # Get the embed message from the thread
                messages = [m async for m in message.channel.history(limit=10)]
                embed_message = next(
                    (
                        m
                        for m in messages
                        if m.embeds and m.embeds[0].title == "Cemantix"
                    ),
                    None,
                )

                if embed_message:
                    embed = embed_message.embeds[0]
                    embed = self.view.update_embed_for_invalid_word(embed, word)
                    await embed_message.edit(embed=embed)
                await message.delete()
                return

            similarity = self.game.calculate_similarity(word)

            if similarity is None:
                # Get the embed message from the thread
                messages = [m async for m in message.channel.history(limit=10)]
                embed_message = next(
                    (
                        m
                        for m in messages
                        if m.embeds and m.embeds[0].title == "Cemantix"
                    ),
                    None,
                )

                if embed_message:
                    embed = embed_message.embeds[0]
                    embed = self.view.update_embed_for_invalid_word(embed, word)
                    await embed_message.edit(embed=embed)
                await message.delete()
            else:
                # Get the embed message from the thread
                messages = [m async for m in message.channel.history(limit=10)]
                embed_message = next(
                    (
                        m
                        for m in messages
                        if m.embeds and m.embeds[0].title == "Cemantix"
                    ),
                    None,
                )
                history_message = next(
                    (
                        m
                        for m in messages
                        if m.embeds and m.embeds[0].title == "Historique"
                    ),
                    None,
                )

                if embed_message:
                    embed = embed_message.embeds[0]
                    embed = self.view.update_embed_for_similarity(
                        embed, word, similarity
                    )
                    await embed_message.edit(embed=embed)
                    await message.delete()

                    # Update history
                    if any(entry[0] == word for entry in self.history[thread_id]):
                        # Word already in history, do not add it again
                        pass
                    else:
                        self.history[thread_id].insert(0, (word, similarity))
                        self.history[thread_id] = self.history[thread_id][
                            :20
                        ]  # Keep only the last 20 words

                    # Sort history by similarity (highest first)
                    self.history[thread_id].sort(key=lambda item: item[1], reverse=True)

                    if history_message:
                        history_embed = self.view.create_history_embed(
                            self.history[thread_id]
                        )
                        await history_message.edit(embed=history_embed)

                    # Increment attempts
                    self.game_attempts[thread_id] += 1

                    # Check if word is correct
                    if word == self.game.current_mystery_word:
                        embed = embed_message.embeds[0]
                        embed = self.view.update_embed_for_correct_word(embed)
                        # Ask user if they want to close the thread or start a new game
                        view, close_button, new_game_button = (
                            self.view.create_end_game_buttons()
                        )

                        async def close_callback(interaction):
                            await self.close_game(thread_id, message.author.id)

                        async def new_game_callback(interaction):
                            self.game.start_new_game()
                            embed = embed_message.embeds[0]
                            embed = self.view.update_embed_for_new_game(embed)
                            await embed_message.edit(embed=embed, view=None)
                            self.history[thread_id] = []
                            history_embed = self.view.create_history_embed(
                                self.history[thread_id]
                            )
                            await history_message.edit(embed=history_embed)
                            await interaction.response.defer()

                        close_button.callback = close_callback
                        new_game_button.callback = new_game_callback

                        await embed_message.edit(embed=embed, view=view)
                        try:
                            await message.delete()
                        except discord.errors.NotFound:
                            pass

                # Reset timer on each message
                if thread_id in self.game_timers:
                    self.game_timers[thread_id].cancel()
                self.game_timers[thread_id] = asyncio.create_task(
                    self.close_game_timer(thread_id, message.author.id)
                )

    def cleanup_game_data(self, thread_id):
        """Cleans up game data for a given thread_id."""
        if thread_id in self.history:
            del self.history[thread_id]
        if thread_id in self.active_games:
            del self.active_games[thread_id]
        if thread_id in self.game_timers:
            self.game_timers[thread_id].cancel()
            del self.game_timers[thread_id]
        if thread_id in self.game_start_times:
            del self.game_start_times[thread_id]
        if thread_id in self.game_attempts:
            del self.game_attempts[thread_id]
