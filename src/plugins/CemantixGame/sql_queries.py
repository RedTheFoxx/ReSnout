# Query to create the main rankings table
# Fields:
# - discord_id: Player's Discord ID (primary key)
# - rank: Player's rank title
# - tier: Numerical tier within rank
# - points: Total points earned
# - games_played: Number of games completed
# - last_game_date: Timestamp of most recent game
# - shadow_mmr: Hidden matchmaking rating (0.0-1.0)
CREATE_RANKINGS_TABLE = '''
    CREATE TABLE IF NOT EXISTS player_rankings (
        discord_id TEXT PRIMARY KEY,
        rank TEXT,
        tier INTEGER,
        points INTEGER DEFAULT 0,
        games_played INTEGER DEFAULT 0,
        last_game_date TEXT,
        shadow_mmr REAL DEFAULT 0.5
    )
'''

# Retrieves basic ranking data for all players
# Returns: List of (discord_id, rank, tier, points, shadow_mmr)
GET_PLAYERS = '''
    SELECT discord_id, rank, tier, points, shadow_mmr 
    FROM player_rankings
'''

# Saves or updates a player's ranking data
# Parameters:
# 1-5: discord_id, rank, tier, points, shadow_mmr (for INSERT)
# 6-9: rank, tier, points, shadow_mmr (for UPDATE)
# Note: Automatically increments games_played and updates last_game_date
SAVE_PLAYER = '''
    INSERT INTO player_rankings
    (discord_id, rank, tier, points, last_game_date, shadow_mmr)
    VALUES (?, ?, ?, ?, DATETIME('now'), ?)
    ON CONFLICT(discord_id) DO UPDATE SET
        rank = ?,
        tier = ?,
        points = ?,
        games_played = games_played + 1,
        last_game_date = DATETIME('now'),
        shadow_mmr = ?
'''

# Gets a player's position in the global rankings
# Parameters:
# 1: discord_id
# Returns: Player's position (1-based ranking)
GET_PLAYER_RANK = '''
    SELECT COUNT(*) + 1 FROM player_rankings
    WHERE points > (
        SELECT points FROM player_rankings WHERE discord_id = ?
    )
'''

# Retrieves players ranked near a target player
# Parameters:
# 1: discord_id - Target player's Discord ID
# 2: Range before target rank
# 3: Range after target rank
# Returns: List of (rank, discord_id, grade, tier, points) for nearby players
GET_NEARBY_PLAYERS = '''
    WITH player_rank AS (
        SELECT
            ROW_NUMBER() OVER (ORDER BY points DESC) as rank,
            discord_id,
            rank as grade,
            tier,
            points
        FROM player_rankings
    ),
    target_rank AS (
        SELECT rank
        FROM player_rank
        WHERE discord_id = ?
    )
    SELECT
        rank,
        discord_id,
        grade,
        tier,
        points
    FROM player_rank
    WHERE rank BETWEEN (SELECT rank FROM target_rank) - ?
                    AND (SELECT rank FROM target_rank) + ?
    ORDER BY rank
'''

# Retrieves the top N players by points
# Parameters:
# 1: limit - Number of top players to return
# Returns: List of (discord_id, rank, tier, points) for top players
GET_TOP_PLAYERS = '''
    SELECT
        discord_id,
        rank,
        tier,
        points
    FROM player_rankings
    ORDER BY points DESC
    LIMIT ?
''' 