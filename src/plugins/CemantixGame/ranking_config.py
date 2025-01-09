from dataclasses import dataclass
from enum import Enum
from typing import Dict, Tuple

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

@dataclass
class RankingConfig:
    # Performance weights
    ACCURACY_WEIGHT: float = 0.0
    ATTEMPTS_WEIGHT: float = 2.0
    TIME_WEIGHT: float = 0.5
    DIFFICULTY_WEIGHT: float = 0.0
    
    # ELO constants
    K_FACTOR: float = 50
    EXPECTED_PERFORMANCE: float = 0.3
    
    # Performance thresholds
    PENALTY_THRESHOLD: float = 0.2
    PENALTY_MULTIPLIER: float = 1.5
    BONUS_THRESHOLD: float = 0.8
    BONUS_MULTIPLIER: float = 2.0
    
    # Rank thresholds
    RANK_THRESHOLDS: Dict[Tuple[Rank, Tier], int] = {
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