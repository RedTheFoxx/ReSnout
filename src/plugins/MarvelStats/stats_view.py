import discord

def create_stats_embed(username: str, matches_played: int, playtime: str) -> discord.Embed:
    """
    Create a Discord embed to display Marvel Rivals statistics
    
    Args:
        username (str): Player's username
        matches_played (int): Number of matches played
        playtime (str): Total playtime
        
    Returns:
        discord.Embed: Formatted embed with statistics
    """
    embed = discord.Embed(
        title=f"Statistiques de {username}",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="Matchs joués", value=matches_played, inline=True)
    embed.add_field(name="Temps de jeu", value=playtime, inline=True)
    
    embed.set_footer(text="Statistiques de la saison en cours")
    
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
        title=f"Erreur lors de la récupération des stats",
        color=discord.Color.red()
    )
    
    if error_type == "invalid_username":
        description = f"Le pseudo '{username}' n'a pas été trouvé."
    else:
        description = f"Une erreur est survenue lors de la récupération des statistiques pour '{username}'."
    
    embed.description = description
    embed.set_footer(text="Veuillez réessayer plus tard")
    
    return embed 