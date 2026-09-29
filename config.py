import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from dotenv import load_dotenv

# 1. Automatically locate and open the local untracked .env file
load_dotenv()

# 2. Extract our runtime secrets out of the local OS environment wrapper
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GOOGLE_CREDS_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# 3. Setup Google Sheets API using the dynamically loaded file path
SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
CREDS = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDS_FILE, SCOPE)
CLIENT = gspread.authorize(CREDS)

SPREADSHEET_KEY = "1pRn-olS_f6H5nEKQW6J0hpkEYCH1SPXPC1ia0H9b0pc"
SHEET_LOGS = CLIENT.open_by_key(SPREADSHEET_KEY).worksheet("Game_Logs")
SHEET_LEADERBOARD = CLIENT.open_by_key(SPREADSHEET_KEY).worksheet("Leaderboard")

STARTING_TOTAL = 100000
UMA_TIERS = [15.0, 5.0, -5.0, -15.0]

# Leaderboard Display Settings
DEFAULT_LEADERBOARD_LIMIT = 32

# Automated Target Channels ID Tracking
PUBLIC_LEADERBOARD_CHANNEL_ID = 123456789012345678
LEAGUE_LOG_CHANNEL_ID = 123456789012345678

def get_current_season_code() -> str:
    now = datetime.now()
    year_short = str(now.year)[2:]
    round_prefix = "E" if now.month <= 6 else "S"
    return f"{round_prefix}{year_short}"
