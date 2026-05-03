import psycopg2
from config import DB_CONFIG

def get_connection():
    # Set up the bridge between Python and the Postgres database
    return psycopg2.connect(**DB_CONFIG)

def create_tables():
    # Define the structure for storing players and their game history
    sql = """
    CREATE TABLE IF NOT EXISTS players (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL
    );

    CREATE TABLE IF NOT EXISTS game_sessions (
        id SERIAL PRIMARY KEY,
        player_id INTEGER REFERENCES players(id),
        score INTEGER NOT NULL,
        level_reached INTEGER NOT NULL,
        played_at TIMESTAMP DEFAULT NOW()
    );
    """

    # Open connection, run the SQL, and save changes
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()

def get_or_create_player(username):
    # Logic to find a user or sign them up if they are new
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Try to insert; if name exists, do nothing
            cur.execute(
                "INSERT INTO players(username) VALUES (%s) ON CONFLICT (username) DO NOTHING",
                (username,)
            )

            # Pull the ID for the given username
            cur.execute(
                "SELECT id FROM players WHERE username = %s",
                (username,)
            )

            player_id = cur.fetchone()[0]

        conn.commit()

    return player_id

def save_result(username, score, level):
    # Get the ID first, then log the session stats
    player_id = get_or_create_player(username)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO game_sessions(player_id, score, level_reached)
                VALUES (%s, %s, %s)
                """,
                (player_id, score, level)
            )
        conn.commit()

def get_personal_best(username):
    # Query the highest score linked to this specific user
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT COALESCE(MAX(gs.score), 0)
                FROM game_sessions gs
                JOIN players p ON gs.player_id = p.id
                WHERE p.username = %s
                """,
                (username,)
            )

            best = cur.fetchone()[0]

    return best

def get_top_scores(limit=10):
    # Fetch the global high scores list for the leaderboard
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    p.username,
                    gs.score,
                    gs.level_reached,
                    TO_CHAR(gs.played_at, 'YYYY-MM-DD HH24:MI')
                FROM game_sessions gs
                JOIN players p ON gs.player_id = p.id
                ORDER BY gs.score DESC, gs.level_reached DESC, gs.played_at ASC
                LIMIT %s
                """,
                (limit,)
            )

            rows = cur.fetchall()

    return rows