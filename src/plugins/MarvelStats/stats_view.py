import discord
import datetime

def create_stats_embed(
    username: str, 
    matches_played: int, 
    playtime: str,
    kills: int,
    kda_ratio: float,
    wins: int,
    win_percentage: float,
    season_number: int,
    season_name: str
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
        color=discord.Color.gold() if win_percentage > 50 else discord.Color.blue()
    )
    
    # Thumbnail avec l'image fournie
    embed.set_thumbnail(url="https://i.ibb.co/j3xcsRh/Capture-d-cran-2025-01-25-010142.png")
    
    # Champs réorganisés avec séparateurs visuels
    embed.add_field(name="🎮 Matchs joués", value=f"```{matches_played:,}```", inline=True)
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
        inline=False
    )
    
    # Footer amélioré avec timestamp
    embed.set_footer(
        text=f"tracker.gg • Saison {season_number}",
        icon_url="https://i.ibb.co/j3xcsRh/Capture-d-cran-2025-01-25-010142.png"
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
        title="❌ Erreur de récupération",
        color=discord.Color.dark_red()
    )
    
    if error_type == "invalid_username":
        embed.description = f"Le pseudo **{username}** n'existe pas dans le tracker."
        embed.set_image(url="https://example.com/404-image.png")  # Ajouter une image d'erreur
    else:
        embed.description = "Problème de connexion à la page de tracker.gg"
        embed.set_image(url="https://example.com/server-error.png")
    
    embed.add_field(
        name="Solutions possibles",
        value="- Vérifiez l'orthographe\n- Réessayez dans 5 minutes\n",
        inline=False
    )
    
    embed.set_footer(
        text="tracker.gg",
        icon_url="https://i.ibb.co/j3xcsRh/Capture-d-cran-2025-01-25-010142.png"
    )
    
    return embed 