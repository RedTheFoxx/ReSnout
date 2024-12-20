"""
RichNotifier is a plugin used to build and send beautiful pings wrapped with embeds.
Check its bio in its .toml companion file.
"""

import discord
from discord import app_commands
from discord.ext import commands


class RichNotifier(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="notifyall", description="Notify all users with a customizable embed"
    )
    @app_commands.describe(
        message="The main content of the notification",
        title="The title of the embed (optional)",
        color="The color of the embed (e.g., red, blue, green, or a hex code, optional)",
        footer="The footer text of the embed (optional)",
    )
    async def notifyall(
        self,
        interaction: discord.Interaction,
        message: str,
        title: str = None,
        color: str = None,
        footer: str = None,
    ):
        embed = discord.Embed(description=message)

        if title:
            embed.title = title

        if color:
            try:
                embed.color = (
                    discord.Color(int(color, 16))
                    if color.startswith("0x")
                    else getattr(discord.Color, color)()
                )
            except (ValueError, AttributeError):
                await interaction.response.send_message(
                    "Invalid color format. Please use a valid color name (e.g., red, blue) or a hex code (e.g., 0xFF0000).",
                    ephemeral=True,
                )
                return
        else:
            embed.color = discord.Color.blue()

        if footer:
            embed.set_footer(text=footer)

        # Send the embed to the channel where the command was used
        await interaction.response.send_message(content=f"@everyone", embed=embed)
