"""A ReSnout plugin. Check its bio in its .toml companion file."""

import discord
from discord import app_commands
from discord.ext import commands

class SimpleOps(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="gw",
        description="Test the gateway latency"
    )
    async def gw(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)  # Convert to ms and round
        await interaction.response.send_message(f"Gateway latency : {latency}ms")
