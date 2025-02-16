"""Farkle Game CLI Implementation"""

from src.plugins.FarkleGame.game import FarkleGame
from src.plugins.FarkleGame.display import Display
from src.plugins.FarkleGame.constants import INITIAL_DICE_COUNT

def play_turn(game: FarkleGame, display: Display):
    """Handle a single player's turn"""
    player = game.current_player
    dice = game.roll_dice(game.dice_count)

    while True:
        display.display_dice(dice)
        score_result = game.calculate_score(dice)

        if score_result['score'] == 0:
            display.display_farkle()
            game.handle_farkle(player)
            return

        display.display_turn_info(player, score_result)
        choice = display.get_player_choice()

        if choice == 'k':
            player.add_score(score_result['score'])
            game.dice_count -= len(score_result['used'])
            if game.dice_count == 0:
                game.dice_count = INITIAL_DICE_COUNT  # Correctly reset to initial value
            dice = game.roll_dice(game.dice_count)
        elif choice == 'r':
            dice = game.roll_dice(game.dice_count)
        elif choice == 'b':
            player.bank_score()
            game.next_turn()
            return

def start_game():
    """Main game loop"""
    # Initialize game with 2 players
    game = FarkleGame(["Player 1", "Player 2"])
    display = Display(game)
    display.display_welcome()
    
    while not game.game_over:
        display.display_stats()
        play_turn(game, display)
        if game.check_win_condition():
            winner = game.end_game()
            display.display_winner(winner)
            display.display_stats()
            # Option to restart the game
            if input("Play again? (y/n): ").lower() == 'y':
                game = FarkleGame(["Player 1", "Player 2"])  # Re-initialize for a new game
                display = Display(game) # Reinitialize the display
                display.display_welcome()
            else:
                break

if __name__ == "__main__":
    start_game()
