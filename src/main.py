"""The main entry point for the bot : init, loads basic commands and asks Discord gateway.
ReSnout is a rework of Snout, a multi-tool wrapped in a Python bot for Discord.
During ancient times, we were working with C# and .NET.
Project architecture is a using "plugins" which can be plugged into the bot. Simple as that.

A ReSnout plugin is designed to present itself with some serializable metadata.
This metadata is a string representation of the plugin, and is used to load the plugin.

__HOW TO ?__

At launch, or when asked a reloading, the bot will scan its plugins directory and seek the plugin store .toml file.
Any correctly declared and activated plugin will be dynamically loaded at runtime.
Some time may be required for the command tree to be fully loaded, so be patient (it's a Discord thing).

__PLUGIN STRUCTURE :__

- A .toml companion file (metadata) for the plugin exposing its informations.
- An entrypoint file for the plugin. Naming convention is the first letter of each word of the plugin name, in uppercase.
- An optional dependencies directory containing the dependencies of the plugin.

__IN-HOUSE MASTER PLUGINS LIST (by Red) :__

- SimpleOps (lightweight ops like dices, stats, pings etc.) - THIS PLUGIN IS MANDATORY
- RichNotifier (build embeds and special notifications on the fly)
- MusicPlayer (play audio from any YT link and more)
"""

import os
import discord
from discord.ext import commands
from core.addins_loader import AddinLoader

# ReSnout is an omniscient bot, but it is not an admin
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

BOT_TOKEN = os.getenv("ENV_BOT_TOKEN")

bot = commands.Bot(command_prefix="/", intents=intents)
plugin_loader = AddinLoader(bot)


async def sync_commands():
    try:
        await bot.tree.sync()
        print(f"✅ Synced {len(bot.tree.get_commands())} commands!")
    except Exception as e:
        print(f"❌ Failed to sync commands. Error: {e}")


@bot.event
async def on_ready():
    print(f"🤖 {bot.user} is now online!")

    try:
        await plugin_loader.load_plugins()
        await sync_commands()

    except Exception as e:
        print(f"❌ {e}")
        await bot.close()


bot.run(BOT_TOKEN)
