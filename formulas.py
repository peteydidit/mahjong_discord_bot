import config

def calculate_match_ladder_points(raw_score: int, uma_tier: float) -> float:
    return ((raw_score - 25000) / 1000.0) + uma_tier


def get_column_letter(col_idx: int) -> str:
    result = ""
    while col_idx > 0:
        col_idx, remainder = divmod(col_idx - 1, 26)
        result = chr(65 + remainder) + result
    return result


def format_season_code_readable(season_code: str) -> str:
    if len(season_code) < 3:
        return season_code
    round_type = "East Round" if season_code[0].upper() == "E" else "South Round"
    year_full = f"20{season_code[1:]}"
    return f"{year_full} - {round_type}"


def maintain_database_schema(season_code: str):
    headers = config.SHEET_LEADERBOARD.row_values(1)
    expected_header = f"{season_code} Games Played"

    if expected_header in headers:
        return

    print(f"[FML]: Expanding ledger schema for territory sector: {season_code}")
    new_headers = [f"{season_code} Games Played", f"{season_code} Net Points", f"{season_code} Adjusted Points"]
    start_col_idx = len(headers) + 1
    start_letter = get_column_letter(start_col_idx)
    end_letter = get_column_letter(start_col_idx + 2)

    config.SHEET_LEADERBOARD.update(range_name=f"{start_letter}1:{end_letter}1", values=[new_headers])
    headers.extend(new_headers)

    all_values = config.SHEET_LEADERBOARD.get_all_values()
    if len(all_values) > 1:
        updates = []
        for row_idx, row in enumerate(all_values[1:], start=2):
            g_letter = get_column_letter(start_col_idx)
            n_letter = get_column_letter(start_col_idx + 1)
            a_letter = get_column_letter(start_col_idx + 2)

            s_games = f'=IF(B{row_idx}="", 0, COUNTIFS(Game_Logs!$C:$C, B{row_idx}, Game_Logs!$O:$O, "{season_code}") + COUNTIFS(Game_Logs!$F:$F, B{row_idx}, Game_Logs!$O:$O, "{season_code}") + COUNTIFS(Game_Logs!$I:$I, B{row_idx}, Game_Logs!$O:$O, "{season_code}") + COUNTIFS(Game_Logs!$L:$L, B{row_idx}, Game_Logs!$O:$O, "{season_code}"))'
            s_net = f'=IF(B{row_idx}="", 0, SUMIFS(Game_Logs!$E:$E, Game_Logs!$C:$C, B{row_idx}, Game_Logs!$O:$O, "{season_code}") + SUMIFS(Game_Logs!$H:$H, Game_Logs!$F:$F, B{row_idx}, Game_Logs!$O:$O, "{season_code}") + SUMIFS(Game_Logs!$K:$K, Game_Logs!$I:$I, B{row_idx}, Game_Logs!$O:$O, "{season_code}") + SUMIFS(Game_Logs!$N:$N, Game_Logs!$L:$L, B{row_idx}, Game_Logs!$O:$O, "{season_code}"))'
            s_adj = f'=IF({g_letter}{row_idx}=0, 0, {n_letter}{row_idx} + ({g_letter}{row_idx} * Variables!$B$2))'

            updates.append({'range': f"{g_letter}{row_idx}:{a_letter}{row_idx}", 'values': [[s_games, s_net, s_adj]]})
            updates.append({'range': f"A{row_idx}", 'values': [[f'=IF(B{row_idx}="", "", RANK({a_letter}{row_idx}, {a_letter}$2:{a_letter}$100))']]})

        config.SHEET_LEADERBOARD.batch_update(updates, value_input_option='USER_ENTERED')


def build_initial_row(next_row_index: int, player_id_str: str, headers: list, season_code: str) -> list:
    lifetime_games = f'=IF(B{next_row_index}="", 0, COUNTIF(Game_Logs!$C:$C, B{next_row_index}) + COUNTIF(Game_Logs!$F:$F, B{next_row_index}) + COUNTIF(Game_Logs!$I:$I, B{next_row_index}) + COUNTIF(Game_Logs!$L:$L, B{next_row_index}))'
    lifetime_net = f'=IF(B{next_row_index}="", 0, SUMIF(Game_Logs!$C:$C, B{next_row_index}, Game_Logs!$E:$E) + SUMIF(Game_Logs!$F:$F, B{next_row_index}, Game_Logs!$H:$H) + SUMIF(Game_Logs!$I:$I, B{next_row_index}, Game_Logs!$K:$K) + SUMIF(Game_Logs!$L:$L, B{next_row_index}, Game_Logs!$N:$N))'
    lifetime_adj = f'=IF(C{next_row_index}=0, 0, D{next_row_index} + (C{next_row_index} * Variables!$B$2))'

    row_data = ["", player_id_str, lifetime_games, lifetime_net, lifetime_adj]

    idx = 5
    while idx < len(headers):
        loop_code = headers[idx].split(" ")[0]
        g_letter = get_column_letter(idx + 1)
        n_letter = get_column_letter(idx + 2)

        s_games = f'=IF(B{next_row_index}="", 0, COUNTIFS(Game_Logs!$C:$C, B{next_row_index}, Game_Logs!$O:$O, "{loop_code}") + COUNTIFS(Game_Logs!$F:$F, B{next_row_index}, Game_Logs!$O:$O, "{loop_code}") + COUNTIFS(Game_Logs!$I:$I, B{next_row_index}, Game_Logs!$O:$O, "{loop_code}") + COUNTIFS(Game_Logs!$L:$L, B{next_row_index}, Game_Logs!$O:$O, "{loop_code}"))'
        s_net = f'=IF(B{next_row_index}="", 0, SUMIFS(Game_Logs!$E:$E, Game_Logs!$C:$C, B{next_row_index}, Game_Logs!$O:$O, "{loop_code}") + SUMIFS(Game_Logs!$H:$H, Game_Logs!$F:$F, B{next_row_index}, Game_Logs!$O:$O, "{loop_code}") + SUMIFS(Game_Logs!$K:$K, Game_Logs!$I:$I, B{next_row_index}, Game_Logs!$O:$O, "{loop_code}") + SUMIFS(Game_Logs!$N:$N, Game_Logs!$L:$L, B{next_row_index}, Game_Logs!$O:$O, "{loop_code}"))'
        s_adj = f'=IF({g_letter}{next_row_index}=0, 0, {n_letter}{next_row_index} + ({g_letter}{next_row_index} * Variables!$B$2))'

        row_data.extend([s_games, s_net, s_adj])
        idx += 3

    try:
        s_idx = headers.index(f"{season_code} Adjusted Points")
        rank_col = get_column_letter(s_idx + 1)
        row_data[0] = f'=IF(B{next_row_index}="", "", RANK({rank_col}{next_row_index}, {rank_col}$2:{rank_col}$100))'
    except ValueError:
        row_data[0] = f'=IF(B{next_row_index}="", "", RANK(E{next_row_index}, E$2:E$100))'

    return row_data


def register_new_player_if_needed(player_id_str: str, season_code: str):
    current_rows = config.SHEET_LEADERBOARD.get_all_values()
    existing_ids = [row[1].strip() for row in current_rows[1:] if len(row) > 1]

    if player_id_str not in existing_ids:
        headers = current_rows[0]
        next_row_index = len(current_rows) + 1
        new_player_row = build_initial_row(next_row_index, player_id_str, headers, season_code)
        config.SHEET_LEADERBOARD.append_row(new_player_row, value_input_option='USER_ENTERED')
