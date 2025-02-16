from dataclasses import dataclass

@dataclass
class Player:
    """Represents a Farkle player"""
    name: str
    total_score: int = 0
    turn_score: int = 0
    turns_played: int = 0
    farkles: int = 0

    def reset_turn(self):
        """Reset turn-specific stats"""
        self.turn_score = 0

    def add_score(self, points: int):
        """Add points to player's score"""
        self.turn_score += points

    def bank_score(self):
        """Bank turn score to total score"""
        self.total_score += self.turn_score
        self.turns_played += 1
        self.reset_turn() 