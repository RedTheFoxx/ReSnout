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

GET_PLAYERS = '''
    SELECT discord_id, rank, tier, points, shadow_mmr 
    FROM player_rankings
'''

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

GET_PLAYER_RANK = '''
    SELECT COUNT(*) + 1 FROM player_rankings
    WHERE points > (
        SELECT points FROM player_rankings WHERE discord_id = ?
    )
'''

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