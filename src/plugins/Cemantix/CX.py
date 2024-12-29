"""
Cemantix is a plugin that implements the Cemantix word game through Discord.
Check its bio in its .toml companion file.
"""

import discord
from discord import app_commands
from discord.ext import commands


class Cemantix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="cem", description="Démarrer une partie de Cemantix")
    async def cem(self, interaction: discord.Interaction):
        # Create a private thread with the user
        thread = await interaction.channel.create_thread(
            name=f"Cemantix - {interaction.user.name}",
            type=discord.ChannelType.private_thread,
        )
        
        # Add the user to the thread
        await thread.add_user(interaction.user)
        
        # Send initial message
        await thread.send("Bienvenue dans votre partie de Cemantix ! (Placeholder)")
        await interaction.response.send_message("Partie créée ! Rendez-vous dans le fil privé.", ephemeral=True) 