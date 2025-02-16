import random
from typing import List, Dict
from src.plugins.FarkleGame.player import Player
from src.plugins.FarkleGame.constants import WINNING_SCORE, INITIAL_DICE_COUNT


class FarkleGame:
    """Main Farkle game class"""

    def __init__(self, players: List[str]):
        self.players = [Player(name) for name in players]
        self.current_player_index = 0
        self.dice_count = INITIAL_DICE_COUNT
        self.winning_score = WINNING_SCORE
        self.game_over = False

    def calculate_score(self, dice: List[int]) -> Dict[str, int]:
        """Calculate score for given dice combination"""
        score = 0
        counts = {i: dice.count(i) for i in range(1, 7)}

        # Check for special combinations
        if all(count == 1 for count in counts.values()):
            return {'score': 1500, 'used': dice}

        if len([count for count in counts.values() if count == 2]) == 3:
            return {'score': 1500, 'used': dice}

        # Calculate individual and multiple scores
        used_dice = []
        for num, count in counts.items():
            if count >= 3:
                if num == 1:
                    score += 1000 * (count - 2)
                else:
                    score += num * 100 * (count - 2)
                used_dice.extend([num] * count)
            elif num == 1 and count > 0:
                score += 100 * count
                used_dice.extend([1] * count)
            elif num == 5 and count > 0:
                score += 50 * count
                used_dice.extend([5] * count)

        return {'score': score, 'used': used_dice}
    
    def handle_farkle(self, player: Player):
        """Handle Farkle condition"""
        player.farkles += 1
        player.reset_turn()
        self.next_turn()

    def check_win_condition(self) -> bool:
        """Check if any player has reached winning score"""
        for player in self.players:
            if player.total_score >= self.winning_score:
                self.game_over = True
                return True
        return False

    def end_game(self):
        """Handle game end"""
        winner = max(self.players, key=lambda p: p.total_score)
        self.game_over = False  # Reset game_over for potential new games.
        return winner

    @property
    def current_player(self) -> Player:
        """Get current player"""
        return self.players[self.current_player_index]

    def next_turn(self):
        """Advance to next player's turn"""
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.dice_count = INITIAL_DICE_COUNT # Reset dice count
        

    def roll_dice(self, count: int) -> List[int]:
        """Roll specified number of dice"""
        return [random.randint(1, 6) for _ in range(count)] 