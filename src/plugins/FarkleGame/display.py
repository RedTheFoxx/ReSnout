from colorama import Fore, Style
from src.plugins.FarkleGame.player import Player
from src.plugins.FarkleGame.game import FarkleGame
from typing import List, Dict

class Display:
    """Handles all display and input for Farkle game"""

    def __init__(self, game: FarkleGame):
        self.game = game

    def display_dice(self, dice: List[int]):
        """Display dice roll with color coding"""
        print(f"\n{Fore.CYAN}=== Dice Roll ==={Style.RESET_ALL}")
        for i, die in enumerate(dice, 1):
            color = Fore.GREEN if die in [1, 5] else Fore.WHITE
            print(f"{Fore.YELLOW}Die {i}:{Style.RESET_ALL} {color}[{die}]{Style.RESET_ALL}")
        print()

        # Provide strategy suggestions
        score_result = self.game.calculate_score(dice)
        if score_result['score'] >= 1000:
            print(f"{Fore.GREEN}Strategy: This is a high-scoring roll! Consider keeping all scoring dice.{Style.RESET_ALL}")
        elif score_result['score'] >= 500:
            print(f"{Fore.YELLOW}Strategy: Good scoring potential. Evaluate risk before rolling again.{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Strategy: Low scoring roll. Consider being cautious.{Style.RESET_ALL}")

    def get_player_choice(self) -> str:
        """Get player's decision"""
        while True:
            choice = input("Choose: (K)eep dice, (R)oll again, or (B)ank points? ").lower()
            if choice in ['k', 'r', 'b']:
                return choice
            print("Invalid choice. Please enter K, R, or B.")

    def display_stats(self):
        """Display game statistics"""
        print("\nCurrent Game Stats:")
        for player in self.game.players:
            print(f"{player.name}: {player.total_score} points")
            print(f"  Turns Played: {player.turns_played}")
            print(f"  Farkles: {player.farkles}\n")

    def display_farkle(self):
        """Display Farkle message"""
        print("\nFARKLE! No scoring dice. Turn over.")
        
    def display_welcome(self):
        """Display welcome message"""
        print("\nWelcome to Farkle!\n")
        
    def display_winner(self, winner: Player):
        """Display winner message"""
        print(f"\nGame Over! {winner.name} wins with {winner.total_score} points!\n")

    def display_turn_info(self, player: Player, score_result: Dict[str, int]):
        """Displays current turn information."""
        print(f"Potential Score: {score_result['score']}")
        print(f"Current Turn Score: {player.turn_score}")
        print(f"Total Score: {player.total_score}\n") 