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
        name="notifyall", description="Envoyer une notification à tout le monde (everyone) formaté dans un embed."
    )
    @app_commands.describe(
        message="Le contenu principal de l'embed",
        title="Le titre de l'embed (optionnel)",
        color="La couleur de l'embed (par exemple, rouge, bleu, vert, ou un code hexa, optionnel)",
        footer="Le texte du pied de page de l'embed (optionnel)",
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
                    "Code couleur invalide. Veuillez fournir un code couleur valide (par exemple, 0xFF0000 pour rouge).",
                    ephemeral=True,
                )
                return
        else:
            embed.color = discord.Color.blue()

        if footer:
            embed.set_footer(text=footer)

        # Send the embed to the channel where the command was used
        await interaction.response.send_message(content=f"@everyone", embed=embed)
