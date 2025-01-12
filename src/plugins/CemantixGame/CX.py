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
from ranking import RankingSystem, PlayerRank


class CemantixGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        try:
            self.game = GameManager()
            self.view = GameView(bot)
            self.history = {}
            self.active_games = {}
            self.game_timers = {}
            self.game_start_times = {}
            self.game_attempts = {}
            self.game_modes = {}  # Store if game is ranked or not
            self.ranking_system = RankingSystem()
        except Exception as e:
            raise commands.ExtensionFailed("CemantixGame", e)

        # Register the message event handler once
        self.bot.event(self.on_message)

    @app_commands.command(name="cem", description="Démarrer une partie de Cemantix")
    async def cem(self, interaction: discord.Interaction):
        # Create initial embed for game mode selection
        embed = self.view.create_game_mode_embed()
        
        # Create mode selection buttons
        view, ranked_button, unranked_button = self.view.create_game_mode_buttons()
        
        async def ranked_callback(interaction):
            await self.start_new_game(interaction, ranked=True)
            
        async def unranked_callback(interaction):
            await self.start_new_game(interaction, ranked=False)
            
        ranked_button.callback = ranked_callback
        unranked_button.callback = unranked_callback
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def start_new_game(self, interaction: discord.Interaction, ranked: bool = True):
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
        self.game_modes[thread.id] = ranked  # Store game mode

        # Create initial embeds
        embed = self.view.create_initial_embed()
        if ranked:
            embed.add_field(name="Mode", value="🏆 Partie classée", inline=True)
        else:
            embed.add_field(name="Mode", value="🎲 Partie non classée", inline=True)
            
        history_embed = self.view.create_history_embed(self.history[thread.id])

        # Create close button view
        view, close_button = self.view.create_close_button()

        async def close_callback(interaction):
            await interaction.response.send_message(f"Partie abandonnée ! Le mot mystère était : **{self.game.current_mystery_word}**\nLe canal sera supprimé dans 5 secondes...")
            await asyncio.sleep(5)
            await self.close_game(thread.id, interaction.user.id)

        close_button.callback = close_callback

        # Send initial messages
        embed_message = await thread.send(embed=embed, view=view)
        history_message = await thread.send(embed=history_embed)

        # Start first game
        self.game.start_new_game()
        await interaction.response.send_message(
            f"Partie créée ! Rendez-vous dans le fil privé {thread.mention}.",
            ephemeral=True,
        )

        # Start timer for the game only if it's a ranked game
        if ranked:
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

            # Try to send the summary embed to the parent channel
            if parent_channel:
                try:
                    summary_embed = self.view.create_summary_embed(attempts, duration_str)
                    await parent_channel.send(embed=summary_embed)
                except discord.errors.Forbidden:
                    # Ignore permission errors - the bot can't send messages in the parent channel
                    pass

            # Delete the thread
            await thread.delete()

        # Clean up game data
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
                        # Calculate game stats for ranking
                        duration = time.time() - self.game_start_times[thread_id]
                        attempts = self.game_attempts[thread_id]
                        
                        # Update player ranking only if game is ranked
                        if self.game_modes[thread_id]:
                            game_data = {
                                'accuracy': 1.0,  # Always 1.0 when word is found
                                'attempts': attempts,
                                'time_taken': duration,
                                'difficulty': 3.0  # Using median difficulty for now
                            }
                            
                            points, new_rank, rank_changed = self.ranking_system.update_player_rank(
                                str(message.author.id), 
                                game_data
                            )
                            
                            # Save player data to database
                            self.ranking_system.save_player(str(message.author.id))
                            
                            # Update embed with ranking information
                            embed = embed_message.embeds[0]
                            embed = self.view.update_embed_for_correct_word(embed)
                            
                            # Add ranking information to embed only for ranked games
                            embed.add_field(
                                name="Classement", 
                                value=f"Points gagnés: {points:+d}\nRang actuel: {new_rank}"
                                + ("\n⭐ Nouveau rang!" if rank_changed else ""),
                                inline=False
                            )
                        else:
                            # Update embed without ranking information for unranked games
                            embed = embed_message.embeds[0]
                            embed = self.view.update_embed_for_correct_word(embed)

                        # Ask user if they want to close the thread or start a new game
                        view, close_button, new_game_button = (
                            self.view.create_end_game_buttons()
                        )

                        async def close_callback(interaction):
                            await self.close_game(thread_id, message.author.id)

                        async def new_game_callback(interaction):
                            # Create initial embed for game mode selection
                            embed = self.view.create_game_mode_embed()
                            
                            # Create mode selection buttons
                            view, ranked_button, unranked_button = self.view.create_game_mode_buttons()
                            
                            async def ranked_callback(interaction):
                                self.game.start_new_game()
                                embed = embed_message.embeds[0]
                                embed = self.view.update_embed_for_new_game(embed)
                                embed.add_field(name="Mode", value="🏆 Partie classée", inline=True)
                                await embed_message.edit(embed=embed, view=None)
                                self.history[thread_id] = []
                                self.game_modes[thread_id] = True
                                history_embed = self.view.create_history_embed(self.history[thread_id])
                                await history_message.edit(embed=history_embed)
                                
                                # Start timer for ranked game
                                if thread_id in self.game_timers:
                                    self.game_timers[thread_id].cancel()
                                self.game_timers[thread_id] = asyncio.create_task(
                                    self.close_game_timer(thread_id, message.author.id)
                                )
                                await interaction.response.defer()
                                
                            async def unranked_callback(interaction):
                                self.game.start_new_game()
                                embed = embed_message.embeds[0]
                                embed = self.view.update_embed_for_new_game(embed)
                                embed.add_field(name="Mode", value="🎲 Partie non classée", inline=True)
                                await embed_message.edit(embed=embed, view=None)
                                self.history[thread_id] = []
                                self.game_modes[thread_id] = False
                                history_embed = self.view.create_history_embed(self.history[thread_id])
                                await history_message.edit(embed=history_embed)
                                
                                # Remove timer for unranked game
                                if thread_id in self.game_timers:
                                    self.game_timers[thread_id].cancel()
                                    del self.game_timers[thread_id]
                                await interaction.response.defer()
                            
                            ranked_button.callback = ranked_callback
                            unranked_button.callback = unranked_callback
                            
                            await embed_message.edit(embed=embed, view=view)
                            await interaction.response.defer()

                        close_button.callback = close_callback
                        new_game_button.callback = new_game_callback

                        await embed_message.edit(embed=embed, view=view)
                        try:
                            await message.delete()
                        except discord.errors.NotFound:
                            pass

                # Reset timer on each message only if game is ranked
                if thread_id in self.game_timers and self.game_modes[thread_id]:
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
        if thread_id in self.game_modes:
            del self.game_modes[thread_id]

    @app_commands.command(
        name="cemrank",
        description="Afficher votre classement et les meilleurs joueurs de Cemantix"
    )
    async def cemrank(self, interaction: discord.Interaction):
        """Display the player's rank and the leaderboard."""
        player_id = str(interaction.user.id)
        
        # Get player stats
        player_stats = self.ranking_system.get_player_stats(player_id)
        
        # Get nearby players
        nearby_players = self.ranking_system.get_nearby_players(player_id, range=1)
        
        # Get top players
        top_players = self.ranking_system.get_top_players(limit=3)
        
        # Create and send the ranking embed
        embed = await self.view.create_ranking_embed(
            player_id=player_id,
            player_data=player_stats,
            nearby_players=nearby_players,
            top_players=top_players
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="cemquit",
        description="Abandonner la partie de Cemantix en cours"
    )
    async def cemquit(self, interaction: discord.Interaction):
        """Quit the current Cemantix game."""
        # Check if the user has an active game
        thread_id = None
        for tid, user_id in self.active_games.items():
            if user_id == str(interaction.user.id):
                thread_id = tid
                break

        if thread_id is None:
            await interaction.response.send_message("Vous n'avez pas de partie en cours.", ephemeral=True)
            return

        # Get the thread
        thread = self.bot.get_channel(thread_id)
        if thread is None:
            await interaction.response.send_message("Impossible de trouver votre partie.", ephemeral=True)
            return

        # Send abandon message and close the game
        await interaction.response.send_message(f"Partie abandonnée ! Le mot mystère était : **{self.game.current_mystery_word}**\nLe canal sera supprimé dans 5 secondes...")
        await asyncio.sleep(5)
        await self.close_game(thread_id, interaction.user.id)
