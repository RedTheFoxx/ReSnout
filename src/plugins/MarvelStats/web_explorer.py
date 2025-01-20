"""
This module is used to fetch the stats of a player from the web.
It implements the required Selenium logic to fetch the stats, including the drivers and content extraction.

This module relies on the `undetected_chromedriver` package to handle web scraping,
allowing for the extraction of player statistics from specified URLs.
"""

import undetected_chromedriver as webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from mappings import XPATH_MAPPINGS


def get_player_macro_stats(url) -> dict:
    """
    Fetches the macro statistics of a player from the given URL.
    Macro stats include total playtime of the season and the number of matches played.

    Args:
        url (str): The URL of the player's profile page to fetch stats from.

    Returns:
        dict: A dictionary containing 'matches_played' and 'playtime'.
    """
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--use_subprocess")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    # Attendre que la page soit complètement chargée
    time.sleep(5)

    stats = {"matches_played": 0, "playtime": "0h"}

    try:
        mapping = XPATH_MAPPINGS["macro_stats"]
        element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, mapping.xpath))
        )

        # Attendre le temps spécifié dans le mapping
        time.sleep(mapping.wait_time)

        # Extraire et traiter le texte
        stats_text = element.text

        # Utiliser la fonction de traitement associée
        stats = mapping.process_func(stats_text)

        return stats

    except Exception as e:
        return stats
    finally:
        time.sleep(5)  # Attendre 5 secondes avant de fermer le navigateur
        driver.quit()


# Example usage
url = "https://tracker.gg/marvel-rivals/profile/ign/AsukaM/overview"
print(get_player_macro_stats(url))
