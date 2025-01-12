"""Module related to the view of the Cemantix game plugin. Manages the embeds and user interface."""

import discord
import random


class GameView:
    def __init__(self, bot):
        self.bot = bot  # Discord bot instance needed to fetch usernames
        
    def create_initial_embed(self):
        """Create the initial embed for the Cemantix game."""
        embed = discord.Embed(
            title="Cemantix",
            description="Bienvenue dans votre partie de Cemantix !\nEntrez un mot, trouvez le mot mystère avec le moins de tentatives possibles !\nNous cherchons plutôt des noms communs, le plus souvent au singulier et sans prise en charge de la casse.\nAttention, le temps ainsi que le nombre de coups sont comptés dans le calcul de vos performances ! C'est partit !",
            color=self._get_random_color(),
        )
        embed.add_field(name="Tentatives", value="0", inline=True)
        return embed

    def create_close_button(self):
        """Create a view with a close button for the initial embed."""
        view = discord.ui.View()
        close_button = discord.ui.Button(
            label="Abandonner", 
            style=discord.ButtonStyle.red,
            custom_id="close_game"
        )
        view.add_item(close_button)
        return view, close_button

    def create_game_mode_buttons(self):
        """Create a view with buttons to select game mode (ranked or unranked)."""
        view = discord.ui.View()
        ranked_button = discord.ui.Button(
            label="Partie classée", 
            style=discord.ButtonStyle.primary,
            custom_id="ranked_game"
        )
        unranked_button = discord.ui.Button(
            label="Partie non classée", 
            style=discord.ButtonStyle.secondary,
            custom_id="unranked_game"
        )
        view.add_item(ranked_button)
        view.add_item(unranked_button)
        return view, ranked_button, unranked_button

    def create_game_mode_embed(self):
        """Create the embed for game mode selection."""
        return discord.Embed(
            title="Cemantix - Sélection du mode",
            description="Choisissez votre mode de jeu :\n\n🏆 **Partie classée**\n- Votre score ELO évoluera\n- Le thread expirera après 5 minutes d'inactivité\n\n🎲 **Partie non classée**\n- Pas d'évolution de votre score ELO\n- Le thread n'expire pas automatiquement",
            color=self._get_random_color()
        )

    def update_embed_for_invalid_word(self, embed, word):
        """Update the embed when an invalid word is entered."""
        embed.description = f"Le mot '{word}' m'est inconnu ... 🤷"
        return embed

    def update_embed_for_similarity(self, embed, word, similarity):
        """Update the embed with the similarity score and temperature scale."""
        emoji = self._get_similarity_emoji(similarity)
        per_mille_text = f"{similarity} ‰"
        temperature = self._get_temperature(similarity)

        # Get current attempt count from embed fields if it exists
        attempts = 0
        for field in embed.fields:
            if field.name == "Tentatives":
                attempts = int(field.value) + 1
                break

        embed.clear_fields()
        embed.description = f"Vous proposez : **'{word}'**"
        embed.add_field(
            name="Similarité", value=f"{emoji} **{per_mille_text}**", inline=True
        )
        embed.add_field(name="Température", value=f"**{temperature}°C**", inline=True)
        embed.add_field(name="Tentatives", value=str(attempts), inline=True)
        embed.set_footer(text="Continuez à chercher !")
        return embed

    def update_embed_for_correct_word(self, embed):
        """Update the embed when the correct word is guessed."""
        embed.description = "Félicitations ! Vous avez trouvé le mot mystère ! 🎉"
        embed.clear_fields()
        embed.set_footer(text="Bien joué !")
        return embed

    def update_embed_for_new_game(self, embed):
        """Update the embed when a new game is started."""
        embed.description = "Nouvelle partie lancée ! 🎲\nEntrez un mot et rapprochez vous du mot mystère avec le moins de tentatives possibles !"
        embed.clear_fields()
        embed.set_footer(text="Bonne chance !")
        return embed

    def create_end_game_buttons(self):
        """Create the buttons for the end of the game."""
        view = discord.ui.View()
        close_button = discord.ui.Button(label="Fermer", style=discord.ButtonStyle.red)
        new_game_button = discord.ui.Button(
            label="Nouvelle partie", style=discord.ButtonStyle.green
        )
        view.add_item(close_button)
        view.add_item(new_game_button)
        return view, close_button, new_game_button

    def _get_similarity_emoji(self, similarity):
        """Get the emoji corresponding to the similarity score."""
        if similarity == 1000:
            return "🔥"  # Perfect match
        elif similarity >= 990:
            return "🔥"  # Very hot
        elif similarity >= 950:
            return "🔥"  # Hot
        elif similarity >= 900:
            return "🔥"  # Warm
        elif similarity >= 800:
            return "🔥"  # Getting warmer
        elif similarity >= 600:
            return "🔥"  # Lukewarm
        elif similarity >= 500:
            return "🔥"  # Getting cooler
        elif similarity >= 400:
            return "😊"  # Cool
        elif similarity >= 250:
            return "😊" 
        elif similarity >= 200:
            return "😐"  # Cold
        elif similarity >= 100:
            return "❄️"  # Very cold
        else:
            return "🧊"  # Ice cold

    def _get_temperature(self, similarity):
        """
        Get the temperature in Celsius based on similarity.
        Uses a smooth curve to map similarity (0-1000) to temperature (-100 to 100°C).
        Make an interpolation to match the similarity to the temperature.
        """
        if similarity == 1000:
            return 100.00
        elif similarity <= 0:
            return -100.00

        normalized = similarity / 1000
        curved = normalized * normalized
        temperature = (curved * 200) - 100

        return round(temperature, 2)

    def _get_random_color(self):
        """Get a random color for the embed."""
        return discord.Color(random.randint(0, 0xFFFFFF))

    def create_history_embed(self, history):
        """Create the embed for the game history, using columns."""
        embed = discord.Embed(
            title="Historique", color=discord.Color.light_grey()
        )
        if not history:
            embed.description = "Aucun mot proposé pour le moment."
            return embed

        words = []
        emojis = []
        per_milles = []

        for word, similarity in history:
            emoji = self._get_similarity_emoji(similarity)
            per_mille_text = f"{similarity} ‰"
            temperature = self._get_temperature(similarity)
            words.append(word)
            emojis.append(emoji)
            per_milles.append(per_mille_text)

        embed.add_field(name="Mot", value="\n".join(words), inline=True)
        embed.add_field(name="Temp.", value="\n".join(emojis), inline=True)
        embed.add_field(name="Similarité", value="\n".join(per_milles), inline=True)

        return embed
    
    def create_summary_embed(self, attempts, duration):
        """Create the embed for the game summary."""
        embed = discord.Embed(
            title="Résumé de la partie",
            color=self._get_random_color(),
        )
        embed.add_field(name="Tentatives", value=str(attempts), inline=True)
        embed.add_field(name="Temps total", value=duration, inline=True)
        embed.set_footer(text="Merci d'avoir joué !")
        return embed

    async def create_ranking_embed(self, player_id: str, player_data: dict, nearby_players: list = None, top_players: list = None):
        """
        Create an embed to display player ranking and leaderboard.
        
        Args:
            player_id: ID of the player requesting the rank
            player_data: Dictionary containing player's rank info
            nearby_players: List of nearby players with their ranks (rank, pid, grade, tier, points)
            top_players: List of top players (pid, grade, tier, points)
        """
        embed = discord.Embed(
            title="🏆 Classement Cemantix",
            color=self._get_random_color()
        )

        # Player's current rank section
        embed.add_field(
            name="📊 Votre classement",
            value=(
                f"**Grade**: {player_data['rank']}\n"
                f"**Points**: {player_data['points']}\n"
                f"**Classement Global**: #{player_data['global_rank']}\n"
                f"**Parties jouées**: {player_data['games_played']}"
            ),
            inline=False
        )

        # Nearby players section
        if nearby_players:
            nearby_text = "```\n"
            for rank, pid, grade, tier, points in nearby_players:
                prefix = "→" if pid == player_id else " "
                try:
                    user = await self.bot.fetch_user(int(pid))
                    username = user.name
                except:
                    username = "Utilisateur inconnu"
                nearby_text += f"{prefix} #{rank:<4} | {username:<20} | {grade} {tier} | {points} pts\n"
            nearby_text += "```"
            embed.add_field(
                name="🎯 Classement local",
                value=nearby_text,
                inline=False
            )

        # Top players section
        if top_players:
            top_text = "```\n"
            for i, (pid, grade, tier, points) in enumerate(top_players, 1):
                medal = ["🥇", "🥈", "🥉"][i-1]
                try:
                    user = await self.bot.fetch_user(int(pid))
                    username = user.name
                except:
                    username = "Utilisateur inconnu"
                top_text += f"{medal} #{i:<2} | {username:<20} | {grade} {tier} | {points} pts\n"
            top_text += "```"
            embed.add_field(
                name="👑 Top 3",
                value=top_text,
                inline=False
            )

        # Progress to next rank
        progress_bar = self._create_progress_bar(player_data['points'] % 100)
        embed.add_field(
            name="📈 Progression vers le prochain rang",
            value=f"{progress_bar} {player_data['points'] % 100}/100",
            inline=False
        )

        embed.set_footer(text="Continuez à jouer pour améliorer votre classement !")
        return embed

    def _create_progress_bar(self, value: int, max_value: int = 100, length: int = 10) -> str:
        """
        Create a text-based progress bar.
        
        Args:
            value: Current value
            max_value: Maximum value
            length: Length of the progress bar
        
        Returns:
            str: A text-based progress bar
        """
        filled = int((value / max_value) * length)
        return f"[{'█' * filled}{'░' * (length - filled)}]"
