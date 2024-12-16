"""The main entry point for the bot : init, loads basic commands and asks Discord gateway.
ReSnout is a rework of Snout, a multi-tool wrapped in a Python bot for Discord.
During ancient times, we were working with C# and .NET.
Project architecture is a using "plugins" which can be plugged into the bot. Simple as that.

A ReSnout plugin is designed to present itself with some serializable metadata.
This metadata is a string representation of the plugin, and is used to load the plugin.

__HOW TO ?__

At launch, or when asked a reloading, the bot will scan its plugins directory and seek the plugin store .toml file.
Any decoded metadata string in the .toml config file will instruct the bot to load the corresponding plugin.

__PLUGIN STRUCTURE :__

- A .toml companion file (metadata) for the plugin. ReSnout use those files to load the plugins and one plugin may use it to discover its dependencies.
- An entrypoint file for the plugin. Naming convention is the first letter of each word of the plugin name, in uppercase
- (if required) A dependencies directory containing the dependencies of the plugin

__IN-HOUSE MASTER PLUGINS LIST (by Red) :__

- SimpleOps (lightweight ops like dices, stats, pings etc.) - THIS PLUGIN IS MANDATORY
- MyLittleBanking (a banking system for discord users, mimics some real life things but it's just a game, right?)
- TSME (They see me rollin' dices for any local RP in your Discord server)
- More to come ...
"""

import os
import discord
from discord.ext import commands

# ReSnout is an omniscient bot, but it is not an admin
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

BOT_TOKEN = os.getenv('ENV_BOT_TOKEN')
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} est en ligne !')

bot.run(BOT_TOKEN)