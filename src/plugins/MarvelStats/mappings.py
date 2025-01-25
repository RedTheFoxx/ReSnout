"""
This module contains all the XPATH mappings and their associated processing functions
for extracting data from web pages.

Each mapping specifies an XPATH expression used to locate elements in the HTML structure
and a corresponding processing function to handle the data extracted from those elements.

!!! Warning, mappings are not always accurate and may evolve with the website updates.
!!! LAST VALID DATE : 2025-01-21
"""

from typing import Dict, Any, Callable
from dataclasses import dataclass


@dataclass
class XPathMapping:
    """
    Class to store XPATH and its associated processing function.

    Attributes:
        xpath (str): The XPATH expression to locate the element.
        process_func (Callable[[str], Any]): The function to process the extracted data.
        wait_time (int): The time to wait after locating the element (default is 2 seconds).

    Notes:
        The XPATH expression should be a valid XPath 1.0 expression.
        The processing function should take a string as input and return a dictionary.
    """

    xpath: str
    process_func: Callable[[str], Any]
    wait_time: int = 2  # Default wait time in seconds after finding element


def process_player_macro_stats(raw_text: str) -> Dict[str, Any]:
    """
    Process the raw text from player macro stats.

    Args:
        raw_text (str): The raw text extracted from the player stats element.

    Returns:
        Dict[str, Any]: A dictionary containing 'matches_played' and 'playtime'.
    """
    stats = {"matches_played": 0, "playtime": "0h"}

    parts = raw_text.split("//")

    matches_text = parts[0].strip()
    if "Matches Played" in matches_text:
        matches = matches_text.replace("Matches Played", "").strip()
        try:
            stats["matches_played"] = int(matches)
        except ValueError:
            print(f"Impossible de convertir '{matches}' en nombre")

    # Extraire le temps de jeu (deuxième partie)
    if len(parts) > 1:
        playtime = parts[1].strip()
        playtime = playtime.replace("h Playtime", "").strip()
        stats["playtime"] = playtime

    return stats


def process_player_kkww_stats(raw_text: str) -> Dict[str, Any]:
    """
    Process the raw text from player KKWW stats to extract:
    - Kills
    - KDA Ratio
    - Wins
    - Win %
    """
    stats = {
        "kills": 0,
        "kda_ratio": 0.0,
        "wins": 0,
        "win_percentage": 0.0
    }

    # Split the raw text into sections for each stat
    sections = raw_text.split('<span data-v-61e89f95="" class="truncate">')
    
    for section in sections:
        if "Kills</span>" in section:
            # Extract kills value
            kills_value = section.split('<span data-v-044b198d="" class="truncate">')[1].split(' <!---->')[0]
            stats["kills"] = int(kills_value.replace(",", ""))
            
        elif "KDA Ratio</span>" in section:
            # Extract KDA ratio value
            kda_value = section.split('<span data-v-044b198d="" class="truncate">')[1].split(' <!---->')[0]
            stats["kda_ratio"] = float(kda_value)
            
        elif "Wins</span>" in section:
            # Extract wins value
            wins_value = section.split('<span data-v-044b198d="" class="truncate">')[1].split(' <!---->')[0]
            stats["wins"] = int(wins_value)
            
        elif "Win %</span>" in section:
            # Extract win percentage value
            win_percent = section.split('<span data-v-044b198d="" class="truncate">')[1].split(' <!---->')[0]
            stats["win_percentage"] = float(win_percent.replace("%", ""))

    return stats


def process_season(raw_text: str) -> Dict[str, Any]:
    """
    Process the raw text from season button to extract:
    - season_number
    - season_name
    """
    season_data = {
        "season_number": 0,
        "season_name": ""
    }
    
    # Exemple de raw_text: "S1: Eternal Night Falls"
    if ":" in raw_text:
        parts = raw_text.split(":", 1)  # Split seulement sur la première occurrence
        if len(parts) == 2:
            # Partie gauche: numéro de saison
            season_part = parts[0].strip()
            if season_part.startswith("S"):
                try:
                    season_data["season_number"] = int(season_part[1:])
                except ValueError:
                    print(f"Erreur conversion numéro saison: {season_part[1:]}")
            
            # Partie droite: nom de la saison
            season_data["season_name"] = parts[1].strip()
    
    return season_data


# Dictionary of all XPATH mappings
XPATH_MAPPINGS = {
    # Represents current season number and name
    "season": XPathMapping(
        xpath="/html/body/div/div/div[2]/div[3]/div/main/div[3]/div[2]/div/div[1]/div[2]",
        process_func=process_season,
    ),
    # Represents Matches Played and Playtime for the current season
    "macro_stats": XPathMapping(
        xpath="/html/body/div/div/div[2]/div[3]/div/main/div[3]/div[2]/div/div[3]/div/div[2]/section/header/span",
        process_func=process_player_macro_stats,
    ),
    # Represents Kills, KDA Ratio, Wins and Win % for the current season
    "kkww": XPathMapping(
        xpath="//div[contains(@class, 'v3-card__body')]//div[contains(@class, 'grid-cols-4')]",
        process_func=process_player_kkww_stats,
    ),
}
