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


def get_stats(url) -> dict:
    """
    Fetches all player statistics from the given URL.
    Combines macro stats (playtime, matches played), KKWW stats (kills, kda, wins, win percentage)
    and season information (number and name).

    Args:
        url (str): The URL of the player's profile page to fetch stats from.

    Returns:
        dict: A dictionary containing macro, KKWW statistics and season information.
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

    stats = {
        "matches_played": 0,
        "playtime": "0h",
        "kills": 0,
        "kda_ratio": 0.0,
        "wins": 0,
        "win_percentage": 0.0,
        "season_number": 0,
        "season_name": "",
        "top_heroes": [],
        "current_rank": {
            "rank": "",
            "rank_points": 0,
            "rank_image": ""
        },
        "season_best": {
            "rank": "",
            "rank_points": 0,
            "rank_image": ""
        },
        "all_time_best": {
            "rank": "",
            "rank_points": 0,
            "rank_image": ""
        }
    }

    try:
        # Récupérer les informations de la saison
        season_mapping = XPATH_MAPPINGS["season"]
        season_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, season_mapping.xpath))
        )
        time.sleep(season_mapping.wait_time)
        season_stats = season_mapping.process_func(season_element.text)
        stats.update(season_stats)

        # Récupérer les statistiques macro
        macro_mapping = XPATH_MAPPINGS["macro_stats"]
        macro_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, macro_mapping.xpath))
        )
        time.sleep(macro_mapping.wait_time)
        macro_stats = macro_mapping.process_func(macro_element.text)
        stats.update(macro_stats)

        # Récupérer les statistiques KKWW
        kkww_mapping = XPATH_MAPPINGS["kkww"]
        kkww_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, kkww_mapping.xpath))
        )
        time.sleep(kkww_mapping.wait_time)
        kkww_stats = kkww_mapping.process_func(kkww_element.get_attribute("innerHTML"))
        stats.update(kkww_stats)

        # Récupérer les top héros
        top_heroes_mapping = XPATH_MAPPINGS["top_heroes"]
        top_heroes_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, top_heroes_mapping.xpath))
        )
        time.sleep(top_heroes_mapping.wait_time)
        top_heroes_stats = top_heroes_mapping.process_func(top_heroes_element.get_attribute("innerHTML"))
        stats.update(top_heroes_stats)

        # Récupérer le current rank
        current_rank_mapping = XPATH_MAPPINGS["current_rank"]
        current_rank_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, current_rank_mapping.xpath))
        )
        time.sleep(current_rank_mapping.wait_time)
        current_rank_stats = current_rank_mapping.process_func(current_rank_element.get_attribute("innerHTML"))
        stats["current_rank"].update(current_rank_stats)

        # Récupérer le season best rank
        season_best_mapping = XPATH_MAPPINGS["season_best"]
        season_best_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, season_best_mapping.xpath))
        )
        time.sleep(season_best_mapping.wait_time)
        season_best_stats = season_best_mapping.process_func(season_best_element.get_attribute("innerHTML"))
        stats["season_best"].update(season_best_stats)

        # Récupérer le all-time best rank
        all_time_best_mapping = XPATH_MAPPINGS["all_time_best"]
        all_time_best_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, all_time_best_mapping.xpath))
        )
        time.sleep(all_time_best_mapping.wait_time)
        all_time_best_stats = all_time_best_mapping.process_func(all_time_best_element.get_attribute("innerHTML"))
        stats["all_time_best"].update(all_time_best_stats)

        return stats

    except Exception as e:
        return stats
    finally:
        driver.quit()


if __name__ == "__main__":
    # Example usage
    url = "https://tracker.gg/marvel-rivals/profile/ign/RedFox/overview"
    print(get_stats(url))
