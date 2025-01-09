import os
from pathlib import Path
from db_context import DatabaseContext
from sql_queries import *

class RankingDatabase:
    def __init__(self):
        self.db_path = Path(__file__).parent / "data/rankings.db"
        self.db_context = DatabaseContext(self.db_path)
        self._init_database()

    def _init_database(self):
        """Initialize the SQLite database and create tables if they don't exist."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with self.db_context.get_cursor() as cursor:
            cursor.execute(CREATE_RANKINGS_TABLE)

    def load_players(self):
        """Load all players from database into memory."""
        players = {}
        with self.db_context.get_cursor() as cursor:
            cursor.execute(GET_PLAYERS)
            for discord_id, rank_str, tier, points, shadow_mmr in cursor.fetchall():
                players[discord_id] = {
                    'rank': rank_str,
                    'tier': tier,
                    'points': points,
                    'shadow_mmr': shadow_mmr
                }
        return players

    def save_player(self, player_id: str, player_data: dict):
        """Save player's current rank data to database."""
        with self.db_context.get_cursor() as cursor:
            cursor.execute(SAVE_PLAYER, (
                player_id,
                player_data['rank'],
                player_data['tier'],
                player_data['points'],
                player_data['shadow_mmr'],
                player_data['rank'],
                player_data['tier'],
                player_data['points'],
                player_data['shadow_mmr']
            ))

    def get_player_stats(self, player_id: str) -> dict:
        """Get complete player statistics including global rank."""
        with self.db_context.get_cursor() as cursor:
            cursor.execute(GET_PLAYER_RANK, (player_id,))
            global_rank = cursor.fetchone()[0]

            cursor.execute('SELECT games_played, shadow_mmr FROM player_rankings WHERE discord_id = ?', (player_id,))
            result = cursor.fetchone()
            games_played = result[0] if result else 0
            shadow_mmr = result[1] if result else 0.5

            return {
                'global_rank': global_rank,
                'games_played': games_played,
                'shadow_mmr': shadow_mmr
            }

    def get_nearby_players(self, player_id: str, range: int = 1) -> list:
        """Get players ranked near the specified player."""
        with self.db_context.get_cursor() as cursor:
            cursor.execute(GET_NEARBY_PLAYERS, (player_id, range, range))
            return cursor.fetchall()

    def get_top_players(self, limit: int = 3) -> list:
        """Get top ranked players."""
        with self.db_context.get_cursor() as cursor:
            cursor.execute(GET_TOP_PLAYERS, (limit,))
            return cursor.fetchall() 