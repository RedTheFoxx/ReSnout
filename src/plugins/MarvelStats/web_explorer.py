"""
This module is used to fetch the stats of a player from the web.
It implements all the required Selenium logic to fetch the stats, as well as the drivers and content extraction.
"""

import undetected_chromedriver as webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def get_player_stats(url):
    """
    Fetches the stats of a player from the given URL.
    """
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--use_subprocess")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    # Wait for the page to load and extract information
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class, 'v3-grid')]")
            )
        )
        print("v3-grid element found. Page loaded successfully.")
        page_loaded = True
    except Exception as e:
        print(f"An error occurred: {e}")
        page_loaded = False
    finally:
        driver.quit()

    return page_loaded


# Example usage
url = "https://tracker.gg/marvel-rivals/profile/ign/RedFox/overview"
get_player_stats(url)
