"""A ReSnout plugin. Check its bio in its .toml companion file."""

import discord.ext.commands as commands

class SimpleOps(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Test the gateway latency
    @commands.command()
    async def gw(self, ctx):
        latency = round(self.bot.latency * 1000)  # Convert to ms and round
        await ctx.send(f"Gateway latency: {latency}ms")
