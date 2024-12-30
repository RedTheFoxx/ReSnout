"""Module related to the view of the Cemantix game plugin. Manages the embeds and user interface."""

import discord

class CemantixView:
    def __init__(self):
        pass

    def create_initial_embed(self):
        """Create the initial embed for the Cemantix game."""
        embed = discord.Embed(
            title="🧊 Cemantix 🧊",
            description="Bienvenue dans votre partie de Cemantix !\nEntrez un mot et je vous dirai à quel point il est proche du mot mystère.",
            color=discord.Color.blue(),
        )
        return embed

    def update_embed_for_invalid_word(self, embed, word):
        """Update the embed when an invalid word is entered."""
        embed.description = f"Le mot '{word}' m'est inconnu ... 🤷"
        return embed

    def update_embed_for_similarity(self, embed, word, similarity):
        """Update the embed with the similarity score."""
        emoji = self._get_similarity_emoji(similarity)
        per_mille_text = f"{similarity} ‰"
        embed.description = f"Mot proposé : '{word}'\nProximité : {emoji} {per_mille_text}"
        return embed

    def update_embed_for_correct_word(self, embed):
        """Update the embed when the correct word is guessed."""
        embed.description = "Félicitations ! Vous avez trouvé le mot mystère ! 🎉"
        return embed

    def update_embed_for_new_game(self, embed):
        """Update the embed when a new game is started."""
        embed.description = "Nouvelle partie lancée ! 🎲\nEntrez un mot et je vous dirai à quel point il est proche du nouveau mot mystère."
        return embed
    
    def create_end_game_buttons(self):
        """Create the buttons for the end of the game."""
        view = discord.ui.View()
        close_button = discord.ui.Button(
            label="Fermer", style=discord.ButtonStyle.red
        )
        new_game_button = discord.ui.Button(
            label="Nouvelle partie", style=discord.ButtonStyle.green
        )
        view.add_item(close_button)
        view.add_item(new_game_button)
        return view, close_button, new_game_button
    
    def _get_similarity_emoji(self, similarity):
        """Get the emoji corresponding to the similarity score."""
        if similarity < 100:
            return "🧊"
        elif similarity < 300:
            return "❄️"
        elif similarity < 500:
            return "💧"
        elif similarity < 700:
            return "🔥"
        else:
            return "🌋"