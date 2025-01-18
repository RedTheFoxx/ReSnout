"""
MarvelStats is a plugin that implements Marvel Rivals statistics from your character directly into Discord.
Check its bio in its .toml companion file.
"""

import sys
import os

sys.path.append(os.path.dirname(__file__))

import discord
from discord import app_commands
from discord.ext import commands

from navigation import ChromeRetriever

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Marvel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="stats",
        description="Affichez toutes les statistiques issues de votre compte Marvel Rivals",
    )
    async def stats(self, interaction: discord.Interaction):
        url = "https://tracker.gg/marvel-rivals"
        await interaction.response.defer(thinking=True)
        driver = await ChromeRetriever.get_driver(url)
        stats_data = await MarvelStatsHelper.stats(driver)
        await interaction.followup.send(stats_data)


# Class responsible for targetting and injecting on specific page elements
class MarvelStatsHelper:
    @staticmethod
    async def stats(driver):
        search_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".search-box"))
        )
        driver.quit()
        if search_element:
            return "OK" # The element was found
        return "Element not found"
