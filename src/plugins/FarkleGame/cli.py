"""Contains the complete CLI version of the Farkle game."""
import random
from enum import Enum
from datetime import datetime
from typing import List, Dict

class GameState(Enum):
    WAITING_FOR_PLAYERS = 1
    PLAYER_TURN = 2
    ROLLING_DICE = 3
    SELECTING_DICE = 4
    BANKING_SCORE = 5
    GAME_OVER = 6

class Player:
    def __init__(self, name: str):
        self.name = name
        self.total_score = 0
        self.games_played = 0
        self.average_score = 0.0

    def update_stats(self):
        if self.games_played > 0:
            self.average_score = self.total_score / self.games_played

class GameHistory:
    def __init__(self, players: List[Player]):
        self.players = players
        self.scores = {player.name: player.total_score for player in players}
        self.date = datetime.now()

class FarkleGame:
    def __init__(self, start_score: int = 10000):
        self.players: List[Player] = []
        self.current_player: Player = None
        self.dice = [random.randint(1, 6) for _ in range(6)]
        self.current_roll: List[int] = []
        self.kept_dice: List[int] = []
        self.total_score = 0
        self.current_score = 0
        self.game_state = GameState.WAITING_FOR_PLAYERS
        self.start_score = start_score
        self.history: List[GameHistory] = []

    def display_game_state(self):
        """Affiche l'état actuel du jeu"""
        print("\n--- État du jeu ---")
        print(f"Joueur actuel: {self.current_player.name}")
        print(f"Score total: {self.current_player.total_score}")
        print(f"Score du tour: {self.current_score}")
        print(f"Dés gardés: {self.kept_dice}")
        print(f"Dés lancés: {self.current_roll}")
        print(f"État du jeu: {self.game_state.name}")
        print("------------------\n")

    def start_game(self, players: List[str]):
        self.players = [Player(name) for name in players]
        self.current_player = self.players[0]
        self.game_state = GameState.PLAYER_TURN
        print(f"Game started with players: {', '.join(players)}")
        self.display_game_state()

    def roll_dice(self):
        if self.game_state != GameState.PLAYER_TURN:
            raise ValueError("Not the right time to roll dice")
        
        num_dice = 6 - len(self.kept_dice)
        self.current_roll = [random.randint(1, 6) for _ in range(num_dice)]
        self.game_state = GameState.ROLLING_DICE
        print(f"Rolled: {self.current_roll}")
        self.display_game_state()
        
        if self.is_farkle(self.current_roll):
            print("Farkle! No points this turn.")
            self.next_player()
        else:
            self.game_state = GameState.SELECTING_DICE
            self.display_game_state()

    def select_dice(self, dice_values: List[int]):
        if not self.is_valid_selection(dice_values):
            raise ValueError("Invalid dice selection")
        
        self.kept_dice.extend(dice_values)
        self.current_score += self.calculate_score(dice_values)
        self.current_roll = [d for d in self.current_roll if d not in dice_values]
        print(f"Selected dice: {dice_values}, Current score: {self.current_score}")
        self.display_game_state()

    def bank_score(self):
        self.current_player.total_score += self.current_score
        self.total_score = self.current_score
        self.current_score = 0
        self.kept_dice = []
        self.next_player()
        print(f"Score banked. {self.current_player.name}'s total: {self.current_player.total_score}")
        self.display_game_state()

    def calculate_score(self, dice_values: List[int]) -> int:
        score = 0
        counts = {x: dice_values.count(x) for x in set(dice_values)}
        
        # Check for straight 1-6
        if set(dice_values) == {1,2,3,4,5,6}:
            return 1500
        
        # Check for three pairs
        if len([count for count in counts.values() if count == 2]) == 3:
            return 1500
        
        # Check for partial straights
        if set(dice_values) == {1,2,3,4,5}:
            return 500
        if set(dice_values) == {2,3,4,5,6}:
            return 750
        
        # Handle multiple of a kind
        for num, count in counts.items():
            if count >= 3:
                if num == 1:
                    score += 1000
                else:
                    score += num * 100
                # Handle 4,5,6 of a kind
                if count == 4:
                    score *= 2
                elif count == 5:
                    score *= 4
                elif count == 6:
                    score *= 8
        
        # Handle single 1s and 5s
        if len(dice_values) < 3:
            score += dice_values.count(1) * 100
            score += dice_values.count(5) * 50
        
        return score

    def is_farkle(self, dice_values: List[int]) -> bool:
        # Check if any scoring combination exists
        if self.calculate_score(dice_values) > 0:
            return False
        
        # Special case: straight or three pairs
        counts = {x: dice_values.count(x) for x in set(dice_values)}
        if set(dice_values) == {1,2,3,4,5,6}:
            return False
        if len([count for count in counts.values() if count == 2]) == 3:
            return False
        if set(dice_values) == {1,2,3,4,5}:
            return False
        if set(dice_values) == {2,3,4,5,6}:
            return False
        
        # Check for individual 1s and 5s
        if 1 in dice_values or 5 in dice_values:
            return False
            
        return True

    def is_valid_selection(self, dice_values: List[int]) -> bool:
        return all(d in self.current_roll for d in dice_values)

    def next_player(self):
        current_index = self.players.index(self.current_player)
        next_index = (current_index + 1) % len(self.players)
        self.current_player = self.players[next_index]
        self.current_score = 0
        self.kept_dice = []
        self.game_state = GameState.PLAYER_TURN
        print(f"It's now {self.current_player.name}'s turn")

    def save_game_state(self):
        pass

    def load_game_state(self):
        pass

    def get_leaderboard(self) -> List[Player]:
        return sorted(self.players, key=lambda p: p.total_score, reverse=True)

def main():
    """Main function to run the CLI version of the Farkle game."""
    game = FarkleGame()
    print("Welcome to the Farkle game!")
    print("To start a new game, type 'new'.")
    print("To load a saved game, type 'load'.")
    print("To quit, type 'quit'.")

    while True:
        command = input("> ").lower()

        if command == 'new':
            players = input("Enter player names separated by commas: ").split(',')
            game.start_game(players)
        elif command == 'roll' and game.game_state == GameState.PLAYER_TURN:
            game.roll_dice()
        elif command.startswith('select') and game.game_state == GameState.SELECTING_DICE:
            dice = list(map(int, command.split()[1:]))
            game.select_dice(dice)
        elif command == 'bank' and game.game_state == GameState.SELECTING_DICE:
            game.bank_score()
        elif command == 'quit':
            break
        else:
            print("Invalid command")

if __name__ == "__main__":
    main()
