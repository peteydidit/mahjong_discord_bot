import discord
from datetime import datetime, timedelta
import config
import formulas
import strings

# Global Cache Variables sitting in local system RAM
LEADERBOARD_CACHE = None
CACHE_TIMESTAMP = None
CACHE_DURATION = timedelta(minutes=10) # Auto-refresh every 10 mins fallback

def force_cache_refresh():
    """Forces the system to clear its cache memory after a fresh game log or deletion."""
    global LEADERBOARD_CACHE, CACHE_TIMESTAMP
    LEADERBOARD_CACHE = None
    CACHE_TIMESTAMP = None

def generate_leaderboard_embed(flag: str = None) -> tuple:
    """
    Queries data records from the sheet matrix.
    Returns (discord.Embed, list_of_player_data) or (None, error_string)
    """
    all_rows = config.SHEET_LEADERBOARD.get_all_values()
    if len(all_rows) <= 1:
        return None, strings.LEADERBOARD_EMPTY

    headers = all_rows[0]
    records = all_rows[1:]

    season_code = config.get_current_season_code()
    show_all_time = (flag == "--all")

    if flag and not flag.startswith("-"):
        season_code = flag.upper()

    if show_all_time:
        title_text = "🪭 All-Time Ledger Report 🪭"
        g_idx, n_idx, a_idx = 2, 3, 4
    else:
        readable_season = formulas.format_season_code_readable(season_code)
        title_text = f"🐦‍🔥 Seasonal KPIs: {readable_season} 🐦‍🔥"
        try:
            g_idx = headers.index(f"{season_code} Games Played")
            n_idx = g_idx + 1
            a_idx = g_idx + 2
        except ValueError:
            return None, strings.SEASON_NOT_FOUND.format(season_code=season_code)

    parsed_leaderboard = []
    for row in records:
        if len(row) <= max(g_idx, n_idx, a_idx) or not row[1].strip():
            continue

        games_played = int(row[g_idx]) if row[g_idx] else 0
        if not show_all_time and games_played == 0:
            continue

        parsed_leaderboard.append({
            "id": row[1].strip(),
            "games": games_played,
            "net": float(row[n_idx]) if row[n_idx] else 0.0,
            "adjusted": float(row[a_idx]) if row[a_idx] else 0.0
        })

    parsed_leaderboard.sort(key=lambda x: x["adjusted"], reverse=True)
    if not parsed_leaderboard:
        return None, "📭 **No active performance metrics recorded within this index profile.**"

    embed = discord.Embed(title=title_text, color=0x1E4D2B)
    return embed, parsed_leaderboard

def delete_game_log_by_id(game_id: str) -> bool:
    """
    Scans Column B (Index 1) of Game_Logs for the given short ID.
    If found, deletes that exact row and returns True. Otherwise, returns False.
    """
    # Fetch all values currently sitting inside the log tab
    all_logs = config.SHEET_LOGS.get_all_values()

    # Loop over log rows skipping the header (Row 1)
    for row_idx, row in enumerate(all_logs, start=1):
        if len(row) > 1 and row[1].strip() == game_id.strip():
            # Delete the matching row number from the sheet matrix
            config.SHEET_LOGS.delete_rows(row_idx)
            # Force our fast in-memory leaderboard cache to clear and refresh
            force_cache_refresh()
            return True

    return False
