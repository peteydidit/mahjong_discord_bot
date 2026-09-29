# Short definitions displayed on global !help
HELP_INTRO = (
    "Need some training hm? 🪭 *Spins fan* 🪭 I suppose... but mind you I have a very busy schedule. "
    "Here's what I can help with... 🐦‍🔥"
)
BRIEF_LOG = "Log a completed table transaction."
BRIEF_LEADERBOARD = "Evaluate business performance metrics."

# Deep documentation manuals displayed on !help [command]
HELP_LOG = (
    "Submits a final 4-player game report directly into the FML ledger.\n\n"
    "**Usage Protocol:**\n"
    "!log @PlayerA scoreA @PlayerB scoreB @PlayerC scoreC @PlayerD scoreD\n\n"
    "**Core Rule Restrictions:**\n"
    "• All 4 associates must be real, unique, blue-clickable mentions.\n"
    "• Order doesn't matter.\n"
    "• Total points across all 4 numbers must balance to exactly 100,000.\n\n"
    "**Example Report:**\n"
    "`!log @Ichihime 35000 @Mika 26000 @Akagi 21000 @Fuuka Minami 18000`"
)

HELP_LEADERBOARD = (
    "Fetches and displays the top ladder standings profiles. "
    "By default, this pulls data straight from the current active 6-month round.\n\n"
    "**Flexible Flags & Optional Parameters:**\n"
    "• `!leaderboard` -> Shows current round's KPIs for all associates.\n"
    "• `!leaderboard [number]` -> Narrows the visual feed to the top [X] entries (e.g., !leaderboard 10).\n"
    "• `!leaderboard --all` -> Scans lifetime FML investments since day one.\n"
    "• `!leaderboard [season_code]` -> Reviews historical performance records (e.g., !leaderboard E26)."
)

# Character Dialogue Triggers
MATH_IMBALANCE = "🪭 *Sighs and spins fan* 🪭 **What kind of accounting is this?**\nThe total equity in our FML games must equal exactly **{starting_total:,}** points. Your current math leaves us at **{total_entered:,}**. We don't need the IRS on us again 🐦‍🔥"
DUPLICATE_PLAYERS = "🪭 **An associate cannot sit in two chairs at once.**\nProvide four distinct, separate names for this drop."
INVALID_MANIFEST = "🪭 *Taps closed fan on the mahogany desk...* **Your manifest format is incorrect.**\nYou must supply exactly 4 player tags and 4 scores. Order no longer matters, but the count does.\nExample: `!log @Charlie 21000 @Alice 35000 @David 18000 @Bob 26000`"
UNRECOGNIZED_ASSET = "🪭 **Unrecognized asset entry: '{arg}'**."
VERIFICATION_FAILED = "🪭 **Data verification validation checks dropped.**"
DATABASE_ERROR = "🪭 **The local encryption lines are jammed.** The data didn't hit the sheet securely. Deal with it, secretary."
LEADERBOARD_EMPTY = "📭 *Looking over a blank page...* **Nobody has put up any numbers yet.** Go make a transaction using `!log`."
SEASON_NOT_FOUND = "🪭 **Season profile '{season_code}' does not exist in my records. Some things don't last forever 🐦‍🔥**"
AUDIT_FAILURE = "❌ **Audit Interrupted:** I couldn't pull the performance ratings matrix from the server. Check your system script."
GUILD_ONLY_ERROR = "🪭 *Blushes behind fan* 🪭 **Hitting up my DMs with that are you? We don't discuss server operations over unsecured channels.**\nPlease execute your commands inside the official FML territory channels, not in my private messages."
ADMIN_ONLY_ERROR = "🪭 *Narrows eyes...* **You don't have the clearance to authorize this deletion.**\nOnly senior syndicate executives can alter historical transaction rows."
GAME_NOT_FOUND = "🪭 **Transaction key '{game_id}' could not be located in our ledger.**\nDouble-check the reference ID string and try again."
DELETE_SUCCESS = "🗑️ **Transaction Successfully Refunded** 🗑️\n*Game row `{game_id}` has been completely purged from the FML ledger profiles.*"

SEASON_CHAMPION_ANNOUNCEMENT = (
    "🍷 🪭 **THE MARKET CLOSES. OPERATIONS AUDIT COMPLETE.** 🪭 🍷\n\n"
    "The {season} has officially terminated. "
    "One associate has completely dominated the FML racket and collected the highest dividends.\n\n"
    "👑 **Congratulations to our Seasonal Champion: {champion}** 👑\n\n"
    "Your efficiency has been noted, and your bonuses have been secured on the payroll ledger. "
    "To the rest of you... the books reset tomorrow. Let's see who survives the next round. 🐦‍🔥"
)
