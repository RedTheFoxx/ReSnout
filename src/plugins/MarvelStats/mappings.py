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


def process_top_heroes(raw_text: str) -> Dict[str, Any]:
    """
    Process the raw text from top heroes section to extract:
    - hero_name
    - win_rate
    - kda
    """
    heroes = []
    
    # Split by individual hero sections
    hero_sections = raw_text.split('<div class="flex gap-4 items-center">')
    
    for section in hero_sections[1:]:  # Skip first empty section
        hero_data = {
            "hero_name": "",
            "win_rate": 0.0,
            "kda": 0.0
        }
        
        # Extract hero name
        name_start = section.find('text-secondary">') + len('text-secondary">')
        name_end = section.find('</span>', name_start)
        if name_start != -1 and name_end != -1:
            hero_data["hero_name"] = section[name_start:name_end].strip()
        
        # Extract win rate
        wr_start = section.find('WR</span>')
        if wr_start != -1:
            wr_value = section[wr_start:].split('<!----></span>')[0].split('>')[-1].replace('%', '')
            try:
                hero_data["win_rate"] = float(wr_value)
            except ValueError:
                print(f"Erreur conversion win rate: {wr_value}")
                
        # Extract KDA
        kda_start = section.find('KDA</span>')
        if kda_start != -1:
            kda_value = section[kda_start:].split('<!----></span>')[0].split('>')[-1]
            try:
                hero_data["kda"] = float(kda_value)
            except ValueError:
                print(f"Erreur conversion KDA: {kda_value}")
        
        heroes.append(hero_data)
    
    return {"top_heroes": heroes[:3]}  # Return only top 3 heroes


def get_rank_image(rank: str) -> str:
    """
    Get the relative path to the rank image based on the rank name.
    
    Args:
        rank (str): The rank name (e.g., 'Diamond II', 'Master III')
        
    Returns:
        str: The relative path to the rank image
    """
    # Extract the base rank (remove roman numerals)
    base_rank = rank.split()[0].lower()
    
    # Special case for ranks above Celestial
    if base_rank in ['eternal', 'one above all']:
        return 'images/ranks/eternity.png'
        
    # Map rank names to image files
    rank_images = {
        'bronze': 'images/ranks/bronze.png',
        'silver': 'images/ranks/silver.png',
        'gold': 'images/ranks/gold.png',
        'platine': 'images/ranks/platine.png',
        'diamond': 'images/ranks/diamond.png',
        'grandmaster': 'images/ranks/grandmaster.png',
        'celestial': 'images/ranks/celestial.png'
    }
    
    return rank_images.get(base_rank, 'images/ranks/bronze.png')  # Default to bronze if rank not found


def process_current_rank(raw_text: str) -> Dict[str, Any]:
    """
    Process the raw text from current rank element to extract:
    - rank (e.g., "Gold I")
    - rank_points (e.g., 3832)
    - rank_image (e.g., "images/ranks/gold.png")
    """
    rank_data = {
        "rank": "",
        "rank_points": 0,
        "rank_image": ""
    }
    
    # Extract rank name
    rank_start = raw_text.find('class="truncate">') + len('class="truncate">')
    rank_end = raw_text.find('</span>', rank_start)
    if rank_start != -1 and rank_end != -1:
        rank_data["rank"] = raw_text[rank_start:rank_end].strip()
        rank_data["rank_image"] = get_rank_image(rank_data["rank"])
    
    # Extract rank points
    points_start = raw_text.find('class="truncate">', rank_end) + len('class="truncate">')
    points_end = raw_text.find(' <span', points_start)
    if points_start != -1 and points_end != -1:
        points_value = raw_text[points_start:points_end].replace(",", "")
        try:
            rank_data["rank_points"] = int(points_value)
        except ValueError:
            print(f"Error converting rank points: {points_value}")
    
    return rank_data


def process_season_best(raw_text: str) -> Dict[str, Any]:
    """
    Process the raw text from season best element to extract:
    - rank (e.g., "Platinum II")
    - rank_points (e.g., 4039)
    - rank_image (e.g., "images/ranks/platine.png")
    """
    rank_data = {
        "rank": "",
        "rank_points": 0,
        "rank_image": ""
    }
    
    # Extract rank name
    rank_start = raw_text.find('alt="') + len('alt="')
    rank_end = raw_text.find('"', rank_start)
    if rank_start != -1 and rank_end != -1:
        rank_data["rank"] = raw_text[rank_start:rank_end].strip()
        rank_data["rank_image"] = get_rank_image(rank_data["rank"])
    
    # Extract rank points
    points_start = raw_text.find('class="stat-value')
    if points_start != -1:
        points_start = raw_text.find('class="truncate">', points_start) + len('class="truncate">')
        points_end = raw_text.find('<', points_start)
        if points_start != -1 and points_end != -1:
            points_value = raw_text[points_start:points_end].replace(",", "").strip()
            try:
                rank_data["rank_points"] = int(points_value)
            except ValueError:
                print(f"Error converting rank points: {points_value}")
    
    return rank_data


def process_all_time_best(raw_text: str) -> Dict[str, Any]:
    """
    Process the raw text from all-time best element to extract:
    - rank (e.g., "Diamond II")
    - rank_points (e.g., 4317)
    - rank_image (e.g., "images/ranks/diamond.png")
    """
    rank_data = {
        "rank": "",
        "rank_points": 0,
        "rank_image": ""
    }
    
    # Extract rank name from alt attribute
    rank_start = raw_text.find('alt="') + len('alt="')
    rank_end = raw_text.find('"', rank_start)
    if rank_start != -1 and rank_end != -1:
        rank_data["rank"] = raw_text[rank_start:rank_end].split(" // ")[0].strip()
        rank_data["rank_image"] = get_rank_image(rank_data["rank"])
    
    # Extract rank points
    points_start = raw_text.find('class="stat-value')
    if points_start != -1:
        points_start = raw_text.find('class="truncate">', points_start) + len('class="truncate">')
        points_end = raw_text.find('<', points_start)
        if points_start != -1 and points_end != -1:
            points_value = raw_text[points_start:points_end].replace(",", "").strip()
            try:
                rank_data["rank_points"] = int(points_value)
            except ValueError:
                print(f"Error converting rank points: {points_value}")
    
    return rank_data


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
    # Represents the player's top 3 heroes
    "top_heroes": XPathMapping(
        xpath="/html/body/div/div/div[2]/div[3]/div/main/div[3]/div[2]/div/div[3]/div/div[1]/section[2]/div",
        process_func=process_top_heroes,
    ),
    # Represents the player's current rank
    "current_rank": XPathMapping(
        xpath="/html/body/div/div/div[2]/div[3]/div/main/div[3]/div[2]/div/div[3]/div/div[2]/section/div/div[1]/div[1]/div[1]/div[2]/div",
        process_func=process_current_rank,
    ),
    # Represents the player's season best rank
    "season_best": XPathMapping(
        xpath="/html/body/div/div/div[2]/div[3]/div/main/div[3]/div[2]/div/div[3]/div/div[2]/section/div/div[1]/div[1]/div[1]/div[3]",
        process_func=process_season_best,
    ),
    # Represents the player's all-time best rank
    "all_time_best": XPathMapping(
        xpath="/html/body/div/div/div[2]/div[3]/div/main/div[3]/div[2]/div/div[3]/div/div[2]/section/div/div[1]/div[1]/div[1]/div[4]",
        process_func=process_all_time_best,
    ),
}
