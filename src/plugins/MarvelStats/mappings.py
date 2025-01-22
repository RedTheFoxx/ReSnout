"""
This module contains all the XPATH mappings and their associated processing functions
for extracting data from web pages.

Each mapping specifies an XPATH expression used to locate elements in the HTML structure
and a corresponding processing function to handle the data extracted from those elements.

/!\ Warning, mappings are not always accurate and may evolve with the website updates.
/!\ LAST VALID DATE : 2025-01-21
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
    Process the raw text from player KKWW stats.
    """
    return {"kkww": raw_text}


# Dictionary of all XPATH mappings
XPATH_MAPPINGS = {
    # Represents Matches Played and Playtime for the current season
    "macro_stats": XPathMapping(
        xpath="/html/body/div/div/div[2]/div[3]/div/main/div[3]/div[2]/div/div[3]/div/div[2]/section/header/span",
        process_func=process_player_macro_stats,
    ),
    # Represents Kills, KDA Ratio, Wins and Win % for the current season
    "kkww": XPathMapping(
        xpath="/html/body/div/div/div[2]/div[3]/div/main/div[3]/div[2]/div/div[3]/div/div[2]/section/div/div[2]/div/div[1]/div/div/div[2]",
        process_func=process_player_kkww_stats,
    ),
}
