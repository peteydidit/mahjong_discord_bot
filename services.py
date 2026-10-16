import discord
from datetime import datetime, timedelta
import config
import formulas
import strings

# Global Cache Variables sitting in local system RAM
LEADERBOARD_CACHE = None
CACHE_TIMESTAMP = None
CACHE_DURATION = timedelta(minutes=10)

def force_cache_refresh():
    """Forces the system to clear its cache memory after a fresh game log or deletion."""
    global LEADERBOARD_CACHE, CACHE_TIMESTAMP
    LEADERBOARD_CACHE = None
    CACHE_TIMESTAMP = None

def generate_leaderboard_embed(flag: str = None) -> tuple:
    """
    Queries data records from the sheet matrix cache.
    Returns (discord.Embed, list_of_player_data) or (None, error_string)
    """
    global LEADERBOARD_CACHE, CACHE_TIMESTAMP
    now = datetime.now()

    if LEADERBOARD_CACHE is None or CACHE_TIMESTAMP is None or (now - CACHE_TIMESTAMP) > CACHE_DURATION:
        try:
            LEADERBOARD_CACHE = config.SHEET_LEADERBOARD.get_all_values()
            CACHE_TIMESTAMP = now
        except Exception as e:
            print(f"Google Sheets Network API Fault: {e}")
            return None, strings.AUDIT_FAILURE

    all_rows = LEADERBOARD_CACHE
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
    """Scans Column B of Game_Logs for the given ID. Deletes row if matched."""
    all_logs = config.SHEET_LOGS.get_all_values()

    for row_idx, row in enumerate(all_logs, start=1):
        if len(row) > 1 and row[1].strip() == game_id.strip():
            config.SHEET_LOGS.delete_rows(row_idx)
            force_cache_refresh()
            return True
    return False

def render_table_string(ctx_or_channel, data_matrix, display_limit: int, header_type: str = "Rank") -> str:
    """Shared formatting component to safely render backslash-free ASCII leaderboard matrices."""
    # Handle guild extraction polymorphically from both context types and scheduled guild task streams
    guild = ctx_or_channel.guild if hasattr(ctx_or_channel, 'guild') else ctx_or_channel.guild

    table_content = f"```\n{header_type} | Player          | Games | Net Pts | Adjusted\n---------------------------------------------------\n"
    for idx, row in enumerate(data_matrix[:display_limit], start=1):
        member = guild.get_member(int(row["id"])) if guild else None
        name = member.display_name if member else f"User({row['id'][:6]})"
        name_fixed = (name[:15] + "..") if len(name) > 15 else name.ljust(15)

        net_formatted = f"{row['net']:+.1f}".ljust(7)
        adj_formatted = f"{row['adjusted']:+.1f}"
        games_str = str(row['games']).ljust(5)
        rank_str = str(idx).ljust(4 if header_type == "Rank" else 5)

        table_content += f"{rank_str} | {name_fixed} | {games_str} | {net_formatted} | {adj_formatted}\n"
    return table_content + "```"

def build_weekly_report(data_matrix) -> discord.Embed:
    # Capture the exact date of execution formatted as MM/DD/YYYY
    date_str = datetime.now().strftime("%m/%d/")
    season_code = config.get_current_season_code()
    readable_season = formulas.format_season_code_readable(season_code)
    title_text = f"📊 FML Weekly Operations Review for {date_str}{readable_season} 📊"

    embed = discord.Embed(title=title_text, color=0x1E4D2B)
    return embed


def build_seasonal_report(data_matrix, closing_season: str, champ_mention: str) -> tuple:
    embed = discord.Embed(title=f"🏆 FML Championship Finals: {formulas.format_season_code_readable(closing_season)} 🏆", color=0x1E4D2B)
    congrats = strings.SEASON_CHAMPION_ANNOUNCEMENT.format(season=formulas.format_season_code_readable(closing_season), champion=champ_mention)
    return embed, congrats
