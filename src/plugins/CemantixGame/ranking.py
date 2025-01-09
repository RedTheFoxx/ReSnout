"""
Cemantix Game Ranking System Implementation

This module implements the ranking system documented in ranking.txt
"""

from enum import Enum
from pathlib import Path
from ranking_db import RankingDatabase

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
        
        # Performance weights - attempts are most important
        self._w1 = 0.0  # accuracy weight (unused)
        self._w2 = 2.0  # attempts weight (highest weight for Cemantix)
        self._w3 = 0.5  # time weight (less important)
        self._w4 = 0.0  # difficulty weight (unused)
        
        # ELO constants
        self._K = 50  # Higher adjustment factor for more dramatic changes
        self._S_mean = 0.3  # Lower expected performance for Cemantix
        
        # Performance thresholds
        self._penalty_threshold = 0.2  # Performance score below this triggers penalty
        self._penalty_multiplier = 1.5  # Multiplier for poor performance penalties
        self._bonus_threshold = 0.8  # Performance score above this triggers bonus
        self._bonus_multiplier = 2.0  # Multiplier for exceptional performance
        
        # Rank thresholds
        self._rank_thresholds = {
            (Rank.BRONZE, Tier.III): 0,
            (Rank.BRONZE, Tier.II): 100,
            (Rank.BRONZE, Tier.I): 200,
            (Rank.SILVER, Tier.III): 350,
            (Rank.SILVER, Tier.II): 525,
            (Rank.SILVER, Tier.I): 750,
            (Rank.GOLD, Tier.III): 1000,
            (Rank.GOLD, Tier.II): 1300,
            (Rank.GOLD, Tier.I): 1600,
            (Rank.PLATINUM, Tier.III): 2000,
            (Rank.PLATINUM, Tier.II): 2500,
            (Rank.PLATINUM, Tier.I): 3000,
            (Rank.MASTER, Tier.III): 3600,
            (Rank.MASTER, Tier.II): 4300,
            (Rank.MASTER, Tier.I): 5100,
        }
        
        self.shadow_mmr = 0.3 # Initialize shadow MMR (lower for Cemantix's difficulty)

    def calculate_performance_score(self, accuracy: float, attempts: int, time_taken: float, difficulty: float) -> float:
        """
        Calculate a performance score based on game data.
        
        Args:
            accuracy: Percentage of correct guesses (0.0 - 1.0)
            attempts: Number of attempts made
            time_taken: Time taken to solve in seconds
            difficulty: Word difficulty rating (1-5)
            
        Returns:
            float: Performance score
        """
        # Normalize attempts with special bonus for low attempts
        if attempts <= 5:  # Exceptional performance
            normalized_attempts = 1.0
        else:
            normalized_attempts = max(0.1, min(0.8, 20.0 / max(attempts, 1)))
            
        # Normalize time with less aggressive penalty
        normalized_time = min(1.0, 3600.0 / max(time_taken, 1))
        normalized_difficulty = (difficulty - 1) / 4  # Convert 1-5 to 0-1 range
        
        # Calculate performance score S
        S = (accuracy * self._w1 + 
             normalized_attempts * self._w2 +
             normalized_time * self._w3 +
             normalized_difficulty * self._w4)
        
        return max(0.0, min(1.0, S))  # Clamp between 0 and 1

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
        
        S = self.calculate_performance_score(accuracy, attempts, time_taken, difficulty)
        
        # Calculate base ELO change based on performance relative to shadow MMR
        delta_elo = self._K * (S - self.shadow_mmr)
        
        # Apply multipliers based on performance
        if S < self._penalty_threshold:
            delta_elo *= self._penalty_multiplier
        elif S > self._bonus_threshold:
            delta_elo *= self._bonus_multiplier
            
        # Additional bonus for exceptional attempts (≤ 5)
        if attempts <= 5:
            delta_elo *= 2.5  # Significant bonus for extremely rare performance
        
        return round(delta_elo)

    def update_rank(self, points: int):
        """
        Update player's rank based on earned points
        
        Args:
            points: Points to add to current score
        """
        # Empêcher les points de descendre en dessous de 0 (Bronze III)
        self.points = max(0, self.points + points)
        
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
        
        # S'assurer que le rang minimum est Bronze III
        if self.points == 0:
            self.rank = Rank.BRONZE
            self.tier = Tier.III
        
        # Return True if rank changed
        return (current_rank, current_tier) != (self.rank, self.tier)

    def get_rank_display(self) -> str:
        """
        Get formatted rank display string
        
        Returns:
            str: Formatted rank (e.g. "Gold II")
        """
        return f"{self.rank.value} {self.tier.name}"

class RankingSystem:
    def __init__(self):
        self.players = {}  # player_id: PlayerRank
        self.db = RankingDatabase()
        self._load_players()
        
    def _load_players(self):
        """Load all players from database into memory."""
        player_data = self.db.load_players()
        for discord_id, data in player_data.items():
            player = PlayerRank()
            player.rank = Rank[data['rank']]
            player.tier = Tier(data['tier'])
            player.points = data['points']
            player.shadow_mmr = data['shadow_mmr']
            self.players[discord_id] = player
            
    def save_player(self, player_id: str):
        """Save player's current rank data to database."""
        player = self.players[player_id]
        player_data = {
            'rank': player.rank.name,
            'tier': player.tier.value,
            'points': player.points,
            'shadow_mmr': player.shadow_mmr
        }
        self.db.save_player(player_id, player_data)
            
    def get_player_stats(self, player_id: str) -> dict:
        """Get complete player statistics including global rank."""
        if player_id not in self.players:
            self.add_player(player_id)
            
        db_stats = self.db.get_player_stats(player_id)
        
        return {
            'rank': self.players[player_id].get_rank_display(),
            'points': self.players[player_id].points,
            'global_rank': db_stats['global_rank'],
            'games_played': db_stats['games_played'],
            'shadow_mmr': self.players[player_id].shadow_mmr
        }
            
    def get_nearby_players(self, player_id: str, range: int = 1) -> list:
        """Get players ranked near the specified player."""
        return self.db.get_nearby_players(player_id, range)
            
    def get_top_players(self, limit: int = 3) -> list:
        """Get top ranked players."""
        return self.db.get_top_players(limit)

    def add_player(self, player_id: str):
        """Add new player to ranking system"""
        self.players[player_id] = PlayerRank()
        self.save_player(player_id)
        
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
        
        # Update shadow MMR
        performance_score = player.calculate_performance_score(
            game_data['accuracy'],
            game_data['attempts'],
            game_data['time_taken'],
            game_data['difficulty']
        )
        
        player.shadow_mmr = (player.shadow_mmr * 0.95) + (performance_score * 0.05) # Moving average
        
        # Update rank and check if it changed
        rank_changed = player.update_rank(points)
        
        return (points, player.get_rank_display(), rank_changed)
