"""
Cemantix is a plugin that implements the Cemantix word game through Discord.
Check its bio in its .toml companion file.
"""

# TODO: Add a better valid dictionnary (maybe extract from the vector model ?) / don't touch the mystery words
# TODO: Use a better vector model
# TODO: Ensure auto delete of the thread and auto game cancellation after 10 minutes of inactivity

# TODO: Bake the database system to store the players and their scores
# TODO: Add a simple leaderboard (less try to find a word = the better) + all of his commands and features
# TODO: Prepare an ELO system with rankings like in Overwatch!

import sys
import os

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
            self.history = []
        except Exception as e:
            raise commands.ExtensionFailed("CemantixGame", e)

    @app_commands.command(name="cem", description="Démarrer une partie de Cemantix")
    async def cem(self, interaction: discord.Interaction):
        # Create a private thread with the user
        thread = await interaction.channel.create_thread(
            name=f"Cemantix - {interaction.user.name}",
            type=discord.ChannelType.private_thread,
        )
        await thread.add_user(interaction.user)

        embed = self.view.create_initial_embed()

        embed_message = await thread.send(embed=embed)
        history_embed = self.view.create_history_embed(self.history)
        history_message = await thread.send(embed=history_embed)

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
                    if any(entry[0] == word for entry in self.history):
                        # Word already in history, do not add it again
                        pass
                    else:
                        self.history.insert(0, (word, similarity))
                        self.history = self.history[:20]  # Keep only the last 20 words
                    
                    # Sort history by similarity (highest first)
                    self.history.sort(key=lambda item: item[1], reverse=True)
                    
                    history_embed = self.view.create_history_embed(self.history)
                    await history_message.edit(embed=history_embed)

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
                            await thread.delete()

                        async def new_game_callback(interaction):
                            self.game.start_new_game()
                            embed = embed_message.embeds[
                                0
                            ]  # Get the current embed from the message
                            embed = self.view.update_embed_for_new_game(embed)
                            await embed_message.edit(embed=embed, view=None)
                            self.history = []
                            history_embed = self.view.create_history_embed(self.history)
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

        # Start first game
        self.game.start_new_game()
        await interaction.response.send_message(
            "Partie créée ! Rendez-vous dans le fil privé.", ephemeral=True
        )
