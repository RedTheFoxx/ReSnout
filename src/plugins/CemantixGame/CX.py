"""
Cemantix is a plugin that implements the Cemantix word game through Discord.
Check its bio in its .toml companion file.
"""

# TODO: Add a better valid dictionnary (maybe extract from the vector model ?) / don't touch the mystery words
# TODO: Make the UI with embeds and message edits, no spamming in the thread
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


class CemantixGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        try:
            self.game = GameManager()
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

        # Define message handler for the thread
        @self.bot.event
        async def on_message(message):
            if message.channel.id == thread.id and not message.author.bot:
                word = message.content.lower().strip()

                # Check if word is valid
                if not self.game.is_word_valid(word):
                    await message.reply(
                        "Je ne connais pas ce mot."
                    )
                    return

                # Calculate similarity
                similarity = self.game.calculate_similarity(word)

                if similarity is None:
                    await message.reply("Je ne connais pas ce mot.")
                else:
                    await message.reply(f"Similarité : {similarity} ‰")

                    # Check if word is correct
                    if word == self.game.current_mystery_word:
                        await message.reply(
                            "Félicitations ! Vous avez trouvé le mot mystère !"
                        )

                        # Ask user if they want to close the thread or start a new game
                        view = discord.ui.View()
                        close_button = discord.ui.Button(
                            label="Fermer", style=discord.ButtonStyle.red
                        )
                        new_game_button = discord.ui.Button(
                            label="Nouvelle partie", style=discord.ButtonStyle.green
                        )

                        async def close_callback(interaction):
                            # Send response before deleting the thread
                            await thread.delete()

                        async def new_game_callback(interaction):
                            self.game.start_new_game()
                            await interaction.response.send_message(
                                "Nouvelle partie lancée !\n"
                                "Entrez un mot et je vous dirai à quel point il est proche du nouveau mot mystère."
                            )

                        close_button.callback = close_callback
                        new_game_button.callback = new_game_callback

                        view.add_item(close_button)
                        view.add_item(new_game_button)

                        await message.reply(
                            "Souhaitez-vous fermer ce thread ou lancer une nouvelle partie ?",
                            view=view,
                        )

        # Start first game
        self.game.start_new_game()
        await thread.send(
            "Bienvenue dans votre partie de Cemantix !\n"
            "Entrez un mot et je vous dirai à quel point il est proche du mot mystère."
        )
        await interaction.response.send_message(
            "Partie créée ! Rendez-vous dans le fil privé.", ephemeral=True
        )
