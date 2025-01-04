"""
Cemantix Game Ranking System Implementation

This module implements the ranking system documented in ranking.txt
"""

from enum import Enum

class Rank(Enum):
    BRONZE = "Bronze"
    SILVER = "Silver"
    GOLD = "Gold"
    PLATINUM = "Platinum"
    MASTER = "Master"

class Tier(Enum):
    I = 1
    II = 2
    III = 3

class PlayerRank:
    def __init__(self):
        self.rank = Rank.BRONZE
        self.tier = Tier.III
        self.points = 0
        
        # Performance weights - adjusted for attempts and time only
        self._w1 = 0.0  # accuracy weight (unused)
        self._w2 = 0.9  # attempts weight (increased)
        self._w3 = 0.9  # time weight (increased)
        self._w4 = 0.0  # difficulty weight (unused)
        
        # ELO constants
        self._K = 20  # ELO adjustment factor
        self._S_mean = 0.5  # Expected average performance
        
        # Rank thresholds
        self._rank_thresholds = {
            (Rank.BRONZE, Tier.III): 0,
            (Rank.BRONZE, Tier.II): 100,
            (Rank.BRONZE, Tier.I): 200,
            (Rank.SILVER, Tier.III): 300,
            (Rank.SILVER, Tier.II): 400,
            (Rank.SILVER, Tier.I): 500,
            (Rank.GOLD, Tier.III): 600,
            (Rank.GOLD, Tier.II): 700,
            (Rank.GOLD, Tier.I): 800,
            (Rank.PLATINUM, Tier.III): 900,
            (Rank.PLATINUM, Tier.II): 1000,
            (Rank.PLATINUM, Tier.I): 1100,
            (Rank.MASTER, Tier.III): 1200,
            (Rank.MASTER, Tier.II): 1300,
            (Rank.MASTER, Tier.I): 1400,
        }

    def calculate_elo(self, accuracy: float, attempts: int, time_taken: float, difficulty: float) -> int:
        """
        Calculate ELO points based on game performance using the formula from ranking.txt
        
        Args:
            accuracy: Percentage of correct guesses (0.0 - 1.0)
            attempts: Number of attempts made
            time_taken: Time taken to solve in seconds
            difficulty: Word difficulty rating (1-5)
            
        Returns:
            int: Points to add/subtract from current score
        """
        # Normalize inputs
        normalized_attempts = min(1.0 / max(attempts, 1), 1.0)
        normalized_time = min(1.0 / max(time_taken, 1), 1.0)
        normalized_difficulty = (difficulty - 1) / 4  # Convert 1-5 to 0-1 range
        
        # Calculate performance score S
        S = (accuracy * self._w1 + 
             normalized_attempts * self._w2 +
             normalized_time * self._w3 +
             normalized_difficulty * self._w4)
        
        # Calculate ELO change
        delta_elo = self._K * (S - self._S_mean)
        
        return round(delta_elo)

    def update_rank(self, points: int):
        """
        Update player's rank based on earned points
        
        Args:
            points: Points to add to current score
        """
        self.points += points
        
        # Find the appropriate rank and tier based on total points
        current_rank = self.rank
        current_tier = self.tier
        
        for (rank, tier), threshold in sorted(
            self._rank_thresholds.items(),
            key=lambda x: x[1],
            reverse=True
        ):
            if self.points >= threshold:
                self.rank = rank
                self.tier = tier
                break
                
        # Return True if rank changed
        return (current_rank, current_tier) != (self.rank, self.tier)

    def get_rank_display(self) -> str:
        """
        Get formatted rank display string
        
        Returns:
            str: Formatted rank (e.g. "Gold II")
        """
        return f"{self.rank.value} {self.tier.name}"

# Placeholder for future implementations
class RankingSystem:
    def __init__(self):
        self.players = {}  # player_id: PlayerRank
        
    def add_player(self, player_id: str):
        """Add new player to ranking system"""
        self.players[player_id] = PlayerRank()
        
    def update_player_rank(self, player_id: str, game_data: dict):
        """
        Update player's rank based on game performance
        
        Args:
            player_id: ID of player to update
            game_data: Dictionary containing game performance metrics
                      Required keys: accuracy, attempts, time_taken, difficulty
        Returns:
            tuple: (points_earned, new_rank_display, rank_changed)
        """
        if player_id not in self.players:
            self.add_player(player_id)
            
        player = self.players[player_id]
        
        # Calculate ELO change
        points = player.calculate_elo(
            game_data['accuracy'],
            game_data['attempts'],
            game_data['time_taken'],
            game_data['difficulty']
        )
        
        # Update rank and check if it changed
        rank_changed = player.update_rank(points)
        
        return (points, player.get_rank_display(), rank_changed)
