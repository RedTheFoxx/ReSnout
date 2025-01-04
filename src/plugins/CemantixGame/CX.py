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
            self.active_games = {} # Track active games per user
            self.game_timers = {} # Track timers for active games
            self.game_start_times = {} # Track start times for active games
            self.game_attempts = {} # Track attempts for active games
        except Exception as e:
            raise commands.ExtensionFailed("CemantixGame", e)

    @app_commands.command(name="cem", description="Démarrer une partie de Cemantix")
    async def cem(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        if user_id in self.active_games:
            # User already has an active game
            thread_id = self.active_games[user_id]
            thread = self.bot.get_channel(thread_id)
            if thread:
                await interaction.response.send_message(f"Vous avez déjà une partie en cours dans le fil {thread.mention}.", ephemeral=True)
            else:
                # The thread was deleted, remove from active games
                del self.active_games[user_id]
                await self.start_new_game(interaction)
            return
        else:
            await self.start_new_game(interaction)

    async def start_new_game(self, interaction: discord.Interaction):
        # Create a private thread with the user
        thread = await interaction.channel.create_thread(
            name=f"Cemantix - {interaction.user.name}",
            type=discord.ChannelType.private_thread,
        )
        await thread.add_user(interaction.user)

        embed = self.view.create_initial_embed()

        embed_message = await thread.send(embed=embed)
        
        # Initialize history for this thread
        self.history[thread.id] = []
        history_embed = self.view.create_history_embed(self.history[thread.id])
        history_message = await thread.send(embed=history_embed)

        # Track the active game
        self.active_games[interaction.user.id] = thread.id
        self.game_start_times[thread.id] = time.time()
        self.game_attempts[thread.id] = 0

        # User message event interceptor
        @self.bot.event
        async def on_message(message):
            if message.channel.id == thread.id and not message.author.bot:
                word = message.content.lower().strip()

                if not self.game.is_word_valid(word):
                    embed = embed_message.embeds[
                        0
                    ]  # Get the current embed from the message
                    embed = self.view.update_embed_for_invalid_word(embed, word)
                    await embed_message.edit(embed=embed)
                    await message.delete()
                    return

                similarity = self.game.calculate_similarity(word)

                if similarity is None:
                    embed = embed_message.embeds[
                        0
                    ]  # Get the current embed from the message
                    embed = self.view.update_embed_for_invalid_word(embed, word)
                    await embed_message.edit(embed=embed)
                    await message.delete()
                else:
                    # Get the current embed from the message
                    embed = embed_message.embeds[0]
                    embed = self.view.update_embed_for_similarity(
                        embed, word, similarity
                    )
                    await embed_message.edit(embed=embed)
                    await message.delete()

                    # Update history
                    if any(entry[0] == word for entry in self.history[thread.id]):
                        # Word already in history, do not add it again
                        pass
                    else:
                        self.history[thread.id].insert(0, (word, similarity))
                        self.history[thread.id] = self.history[thread.id][:20]  # Keep only the last 20 words
                    
                    # Sort history by similarity (highest first)
                    self.history[thread.id].sort(key=lambda item: item[1], reverse=True)
                    
                    history_embed = self.view.create_history_embed(self.history[thread.id])
                    await history_message.edit(embed=history_embed)

                    # Increment attempts
                    self.game_attempts[thread.id] += 1

                    # Check if word is correct
                    if word == self.game.current_mystery_word:
                        embed = embed_message.embeds[
                            0
                        ]  # Get the current embed from the message
                        embed = self.view.update_embed_for_correct_word(embed)
                        # Ask user if they want to close the thread or start a new game
                        view, close_button, new_game_button = (
                            self.view.create_end_game_buttons()
                        )

                        async def close_callback(interaction):
                            await self.close_game(thread.id, interaction.user.id)

                        async def new_game_callback(interaction):
                            self.game.start_new_game()
                            embed = embed_message.embeds[
                                0
                            ]  # Get the current embed from the message
                            embed = self.view.update_embed_for_new_game(embed)
                            await embed_message.edit(embed=embed, view=None)
                            self.history[thread.id] = []
                            history_embed = self.view.create_history_embed(self.history[thread.id])
                            await history_message.edit(embed=history_embed)
                            await interaction.response.defer()

                        close_button.callback = close_callback
                        new_game_button.callback = new_game_callback

                        await embed_message.edit(
                            embed=embed,
                            view=view,
                        )
                        try:
                            await message.delete()
                        except discord.errors.NotFound:
                            pass
                
                # Reset timer on each message
                if thread.id in self.game_timers:
                    self.game_timers[thread.id].cancel()
                self.game_timers[thread.id] = asyncio.create_task(self.close_game_timer(thread.id, interaction.user.id))

        # Start first game
        self.game.start_new_game()
        await interaction.response.send_message(
            "Partie créée ! Rendez-vous dans le fil privé.", ephemeral=True
        )
        # Start timer for the game
        self.game_timers[thread.id] = asyncio.create_task(self.close_game_timer(thread.id, interaction.user.id))

    async def close_game_timer(self, thread_id, user_id):
        await asyncio.sleep(300) # 5 minutes before auto closing the game
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

        # Clean up game data
        if thread_id in self.history:
            del self.history[thread_id]
        if user_id in self.active_games:
            del self.active_games[user_id]
        if thread_id in self.game_timers:
            self.game_timers[thread_id].cancel()
            del self.game_timers[thread_id]
        if thread_id in self.game_start_times:
            del self.game_start_times[thread_id]
        if thread_id in self.game_attempts:
            del self.game_attempts[thread_id]
