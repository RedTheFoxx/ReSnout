"""Module related to the view of the Farkle game plugin. Manages the embeds and user interface."""

import discord
import random

class FarkleView:
    def __init__(self, bot):
        self.bot = bot
    
    def create_initial_embed(self):
        """Create the initial embed for the Farkle game."""
        embed = discord.Embed(
            title="Farkle",
            description="Bienvenue dans votre partie de Farkle !\nLancez les dés et accumulez des points en évitant de faire un Farkle !",
            color=self._get_random_color(),
        )
        embed.add_field(name="Score Total", value="0", inline=True)
        embed.add_field(name="Score du Tour", value="0", inline=True)
        return embed

    def update_game_state_embed(self, embed, current_roll, kept_dice, total_score, current_score):
        """Update the embed with current game state."""
        embed.clear_fields()
        
        # Display current roll
        if current_roll:
            dice_str = " ".join([str(die) for die in current_roll])
            embed.add_field(
                name="🎲 Dés Lancés",
                value=f"```{dice_str}```",
                inline=False
            )
        
        # Display kept dice
        if kept_dice:
            kept_str = " ".join([str(die) for die in kept_dice])
            embed.add_field(
                name="✨ Dés Conservés",
                value=f"```{kept_str}```",
                inline=False
            )
        
        # Display scores
        embed.add_field(name="💰 Score Total", value=str(total_score), inline=True)
        embed.add_field(name="🎯 Score du Tour", value=str(current_score), inline=True)
        
        return embed

    def create_game_buttons(self, can_bank=False):
        """Create the buttons for game actions."""
        view = discord.ui.View()
        
        # Roll button
        roll_button = discord.ui.Button(
            label="Lancer les dés",
            style=discord.ButtonStyle.primary,
            custom_id="roll_dice"
        )
        
        # Bank score button
        bank_button = discord.ui.Button(
            label="Banquer les points",
            style=discord.ButtonStyle.success,
            custom_id="bank_score",
            disabled=not can_bank
        )
        
        # End game button
        end_button = discord.ui.Button(
            label="Terminer la partie",
            style=discord.ButtonStyle.danger,
            custom_id="end_game"
        )
        
        view.add_item(roll_button)
        if can_bank:
            view.add_item(bank_button)
        view.add_item(end_button)
        
        return view, roll_button, bank_button, end_button

    def create_dice_selection_buttons(self, available_dice):
        """Create buttons for selecting dice from the current roll."""
        view = discord.ui.View()
        
        for die in available_dice:
            button = discord.ui.Button(
                label=str(die),
                style=discord.ButtonStyle.secondary,
                custom_id=f"select_die_{die}"
            )
            view.add_item(button)
        
        return view

    def create_end_game_embed(self, final_score):
        """Create the embed for the end of the game."""
        embed = discord.Embed(
            title="Fin de la partie",
            description=f"Partie terminée ! Votre score final est de {final_score} points !",
            color=self._get_random_color()
        )
        return embed

    def create_farkle_embed(self, total_score):
        """Create the embed when player rolls a Farkle."""
        embed = discord.Embed(
            title="FARKLE !",
            description="Oh non ! Vous avez fait un Farkle et perdu vos points du tour !",
            color=discord.Color.red()
        )
        embed.add_field(name="Score Total", value=str(total_score), inline=True)
        return embed

    def _get_random_color(self):
        """Get a random color for the embed."""
        return discord.Color(random.randint(0, 0xFFFFFF))