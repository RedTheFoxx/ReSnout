import discord
import datetime


RANK_IMAGES = {
    "One Above All": "https://i.postimg.cc/yYjT5Y53/one-above-all.png",
    "Eternity": "https://i.postimg.cc/90jp34CZ/eternity.png",
    "Celestial": "https://i.postimg.cc/ZRNcDPtJ/celestial.webp",
    "Grandmaster": "https://i.postimg.cc/J7bxNQ5q/grandmaster.png",
    "Diamond": "https://i.postimg.cc/02PfcJtq/diamond.png",
    "Platinum": "https://i.postimg.cc/jSjhrY0g/platine.webp",
    "Gold": "https://i.postimg.cc/P5FQXVdt/gold.webp",
    "Silver": "https://i.postimg.cc/PqpzPbq1/silver.webp",
    "Bronze": "https://i.postimg.cc/xdwGHkkh/bronze.webp"
}


def get_rank_image(rank_name: str) -> str:
    """
    Get the image URL for a given rank name.
    
    Args:
        rank_name (str): Name of the rank in format "Rank II" (e.g., "Diamond II")
        
    Returns:
        str: URL of the rank image, or None if not found
    """
    # Prendre seulement la première partie du rang (avant le II)
    base_rank = rank_name.split()[0] if rank_name else ""
    # Ajouter une vérification pour "One Above All" qui contient des espaces
    if "One Above All" in rank_name:
        base_rank = "One Above All"
    return RANK_IMAGES.get(base_rank)


def create_stats_embed(
    username: str,
    matches_played: int,
    playtime: str,
    kills: int,
    kda_ratio: float,
    wins: int,
    win_percentage: float,
    season_number: int,
    season_name: str,
) -> discord.Embed:
    """
    Create a Discord embed to display Marvel Rivals statistics

    Args:
        username (str): Player's username
        matches_played (int): Number of matches played
        playtime (str): Total playtime
        kills (int): Total kills
        kda_ratio (float): KDA ratio
        wins (int): Total wins
        win_percentage (float): Win percentage
        season_number (int): Current season number
        season_name (str): Current season name

    Returns:
        discord.Embed: Formatted embed with statistics
    """
    # Nouvelle structure d'embed avec plus de détails visuels
    embed = discord.Embed(
        title=f"🏆 Saison {season_number} - {season_name}",
        description=f"Statistiques de **{username}**",
        color=discord.Color.gold() if win_percentage > 50 else discord.Color.blue(),
    )

    # Thumbnail avec l'image fournie
    embed.set_thumbnail(
        url="https://i.ibb.co/j3xcsRh/Capture-d-cran-2025-01-25-010142.png"
    )

    # Champs réorganisés avec séparateurs visuels
    embed.add_field(
        name="🎮 Matchs joués", value=f"```{matches_played:,}```", inline=True
    )
    embed.add_field(name="⏱ Temps de jeu", value=f"```{playtime}```", inline=True)
    embed.add_field(name="\u200b", value="\u200b", inline=True)  # Séparateur

    embed.add_field(name="🔫 Kills totaux", value=f"```{kills:,}```", inline=True)
    embed.add_field(name="🎯 Ratio KDA", value=f"```{kda_ratio:.2f}```", inline=True)
    embed.add_field(name="\u200b", value="\u200b", inline=True)  # Séparateur

    # Section victoires avec mise en forme spéciale
    win_color = "#00FF00" if win_percentage > 50 else "#FF0000"
    embed.add_field(
        name="🏅 Victoires",
        value=f"**{wins}** victoires\n`{win_percentage:.1f}%` de winrate",
        inline=False,
    )

    # Footer amélioré avec timestamp
    embed.set_footer(
        text=f"tracker.gg • Saison {season_number}",
        icon_url="https://i.ibb.co/j3xcsRh/Capture-d-cran-2025-01-25-010142.png",
    )
    embed.timestamp = datetime.datetime.now()

    return embed


def create_error_embed(username: str, error_type: str) -> discord.Embed:
    """
    Create an error embed for failed stats retrieval

    Args:
        username (str): Player's username
        error_type (str): Type of error encountered

    Returns:
        discord.Embed: Formatted error embed
    """
    embed = discord.Embed(
        title="❌ Erreur de récupération", color=discord.Color.dark_red()
    )

    if error_type == "invalid_username":
        embed.description = f"Le pseudo **{username}** n'existe pas dans le tracker."
        embed.set_image(
            url="https://example.com/404-image.png"
        )  # Ajouter une image d'erreur
    else:
        embed.description = "Problème de connexion à la page de tracker.gg"
        embed.set_image(url="https://example.com/server-error.png")

    embed.add_field(
        name="Solutions possibles",
        value="- Vérifiez l'orthographe\n- Réessayez dans 5 minutes\n",
        inline=False,
    )

    embed.set_footer(
        text="tracker.gg",
        icon_url="https://i.ibb.co/j3xcsRh/Capture-d-cran-2025-01-25-010142.png",
    )

    return embed


def create_heroes_embed(username: str, top_heroes: list) -> discord.Embed:
    """
    Create a Discord embed to display top 3 heroes statistics

    Args:
        username (str): Player's username
        top_heroes (list): List of top 3 heroes with their stats

    Returns:
        discord.Embed: Formatted embed with heroes statistics
    """
    embed = discord.Embed(
        title="🌟 Top 3 Héros",
        description=f"Vos spécialités :",
        color=discord.Color.purple(),
    )

    # Ajouter les statistiques pour chaque héros avec une numérotation
    for index, hero in enumerate(top_heroes, start=1):
        embed.add_field(
            name=f"{index}. {hero['hero_name']}",
            value=f"```Winrate : {hero['win_rate']}%\nKDA : {hero['kda']:.2f}```",
            inline=False,
        )

    # Footer cohérent avec le premier embed
    embed.set_footer(
        text="tracker.gg • Statistiques avancées",
        icon_url="https://i.ibb.co/j3xcsRh/Capture-d-cran-2025-01-25-010142.png",
    )
    embed.timestamp = datetime.datetime.now()

    return embed


def create_current_rank_embed(username: str, rank_data: dict) -> discord.Embed:
    """
    Create a Discord embed to display current rank information

    Args:
        username (str): Player's username
        rank_data (dict): Dictionary containing rank information

    Returns:
        discord.Embed: Formatted embed with rank statistics
    """
    embed = discord.Embed(
        title="🎮 Rang Actuel",
        description=f"Votre classement",
        color=discord.Color.blue(),
    )

    embed.add_field(name="Division", value=f"```{rank_data['rank']}```", inline=True)
    embed.add_field(name="Points", value=f"```{rank_data['rank_points']} RS```", inline=True)

    # Ajouter l'image du rang
    rank_image = get_rank_image(rank_data['rank'])
    if rank_image:
        embed.set_thumbnail(url=rank_image)

    embed.set_footer(
        text="tracker.gg • Rang actuel",
        icon_url="https://i.ibb.co/j3xcsRh/Capture-d-cran-2025-01-25-010142.png",
    )
    embed.timestamp = datetime.datetime.now()

    return embed


def create_season_best_embed(username: str, rank_data: dict) -> discord.Embed:
    """
    Create a Discord embed to display season best rank information

    Args:
        username (str): Player's username
        rank_data (dict): Dictionary containing rank information

    Returns:
        discord.Embed: Formatted embed with rank statistics
    """
    embed = discord.Embed(
        title="🏆 Top rang de la saison",
        description=f"Votre record cette saison",
        color=discord.Color.gold(),
    )

    embed.add_field(name="Division", value=f"```{rank_data['rank']}```", inline=True)
    embed.add_field(name="Points", value=f"```{rank_data['rank_points']} RS```", inline=True)

    # Ajouter l'image du rang
    rank_image = get_rank_image(rank_data['rank'])
    if rank_image:
        embed.set_thumbnail(url=rank_image)

    embed.set_footer(
        text="tracker.gg • Record de la saison",
        icon_url="https://i.ibb.co/j3xcsRh/Capture-d-cran-2025-01-25-010142.png",
    )
    embed.timestamp = datetime.datetime.now()

    return embed


def create_all_time_best_embed(username: str, rank_data: dict) -> discord.Embed:
    """
    Create a Discord embed to display all-time best rank information

    Args:
        username (str): Player's username
        rank_data (dict): Dictionary containing rank information

    Returns:
        discord.Embed: Formatted embed with rank statistics
    """
    embed = discord.Embed(
        title="👑 Record historique",
        description=f"Votre record absolu",
        color=discord.Color.gold(),
    )

    embed.add_field(name="Division", value=f"```{rank_data['rank']}```", inline=True)
    embed.add_field(name="Points", value=f"```{rank_data['rank_points']} RS```", inline=True)

    # Ajouter l'image du rang
    rank_image = get_rank_image(rank_data['rank'])
    if rank_image:
        embed.set_thumbnail(url=rank_image)

    embed.set_footer(
        text="tracker.gg • Record historique",
        icon_url="https://i.ibb.co/j3xcsRh/Capture-d-cran-2025-01-25-010142.png",
    )
    embed.timestamp = datetime.datetime.now()

    return embed
