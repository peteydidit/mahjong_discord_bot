# 🪭 Florida Mahjong League — Operations Manual 🐦‍🔥

Welcome to the official repository for the **Florida Mahjong League Bot.** Our league is blessed to have the talents of our stand-in ledger-keeper, **Fuuka Minami (南枫花)**, the CEO of the Mahjong Invitational League of Florida. This Discord bot dynamically bridges a local open-ladder tournament system with Google Sheets, acting as an automated league rankings tracker and game logger.

The system is fully decoupled into optimized python modules, utilizing in-memory caching and background cron-scheduling tasks to deliver sub-second ledger updates with pure executive style.

---

## 💎 Character & Tone Profile
Fuuka Minami handles your tournament enterprise like a high-stakes asset portfolio. 
* **The Emojis:** Folding Fan (🪭), Phoenix (🐦‍🔥), and Wine/Luxury (🍷, 💼, 💰, 🌴).
* **The Attitude:** Sophisticated, commanding, and business-minded. Poorly formatted inputs or bad table math are treated as sloppy financial audits rather than code exceptions. Fuuka keeps your associates aligned using custom corporate dialogue blocks:


---

## 🪭 Core Features & Architecture 🐦‍🔥

### 💼 1. The Silent DM Guidance Console (`!help`)
* **The Protocol:** Minimizes public chatter. When an associate calls for training, Fuuka instantly purges the text trigger from the server channel and routes the full operational manual quietly into their private DMs.
* **The Executive Flair:** She greets them with her signature cold charisma:  
  > *"🪭 Need some training hm? I suppose... but mind you I have a very busy schedule. Here's what I can help with... 🐦‍🔥"*

### 💰 2. Frictionless Ledger Logging (`!log`)
* **The Protocol:** Order-independent parameters. Table captains can input match scores in any random sequence (e.g., `!log @Charlie 21000 @Alice 35000 @David 18000 @Bob 26000`).
* **The Core Auditing:** The engine unpacks the arguments, verifies the biological signatures (no duplicate players), and ensures the table equity balances perfectly to exactly **100,000 points**. It then programmatically sorts positions from 1st to 4th place.
* **The Spreadsheet Output:** Appends a clean 15-column receipt into the `Game_Logs` sheet tracking the *Timestamp, Game ID, Raw Scores, calculated tournament Uma points (+15 / +5 / -5 / -15), and exact Ladder Point yields* concurrently.

### 🌴 3. Blazing-Fast Standings (`!leaderboard`)
* **The Protocol:** Wipes the command prompt from the channel and routes ranks cleanly via DM.
* **The Caching Engine:** To completely bypass Google API connection lag, the command utilizes **In-Memory Caching**. Instead of a 10-second server download delay, she pulls rows out of local system RAM in **0.01 seconds** flat.
* **Flexible Queries:** Players can pass custom limit values or year parameters to review historical eras on demand (e.g., `!leaderboard 10`, `!leaderboard E26 5`, `!leaderboard --all`).

### 🔄 4. Automated Roster Provisioning
* **The Protocol:** Manual database entry is for low-level underlings. The moment a brand-new associate finishes their first match log, Fuuka automatically provisions a fresh tracking row for them inside the `Leaderboard` spreadsheet tab, deploying all required calculation cell equations instantly.

### 📅 5. Saturday Operations Review (Automated Task)
* **The Protocol:** Every Saturday night at exactly **10:00 PM EST**, Fuuka wakes up on a background loop thread, audits the live ladder matrix, trims the display down to an elite Top 10, and posts a public performance review recap card directly into your server's announcements channel.

### 👑 6. The 6-Month Championship Coronation (Automated Task)
* **The Protocol:** At midnight on **July 1st** and **January 1st**, the seasonal round comes to a hard close. Fuuka freezes the ledger, identifies the highest-earning associate, and posts a public victory announcement pinning their name to the historical archives as the official **East Round 🌸** or **South Round 🍂** Syndicate Champion.

### 🗑️ 7. Hidden Executive Purging (`!remove_game`)
* **The Protocol:** An administrative fallback utility. If a table captain logs bad numbers, a senior executive can execute `!remove_game [Game_ID]`. Fuuka vaporizes the command text to keep it hidden, deletes the target row from the sheet, resets her memory cache, and triggers an automated sheets recalculation.

### 🔒 8. Secured Channel Protection
* **The Protocol:** To maintain an immaculate transaction ledger feed, Fuuka polices your logging channel with a zero-tolerance filter. Any casual text chat, gossip, or invalid commands typed inside the channel are **instantly deleted from existence**, leaving nothing but verified receipts behind.

---

## 🗂️ Project Directory Layout

```text
mahjong_discord_bot/
│
├── florida-mahjong-league-XXXXXX.json  # Google Service Account Private Key
├── config.py                            # Authorization scopes, constants, and channel IDs
├── formulas.py                          # Oka/Uma math models and Excel string generation
├── services.py                          # In-memory data caches and sheet delete operations
├── strings.py                           # Character dialogue assets and help manuals
└── fml_riichi_bot.py                    # Main runner: Discord events and cron tasks
```

---

## ⚙️ Operational Installation

1. Clone this repository into your local development environment.
2. Install the required system dependencies via your terminal:
   ```bash
   pip install discord.py gspread oauth2client
   ```
3. Drop your Google Cloud Service Account JSON key into the root folder and name it `florida-mahjong-league-c0ef49d4c193.json`.
4. Turn on **Developer Mode** in Discord, right-click your channels, and copy the IDs into `config.py` for `PUBLIC_LEADERBOARD_CHANNEL_ID` and `LEAGUE_LOG_CHANNEL_ID`.
5. Enable **Server Members Intent** inside the Discord Developer Portal under the *Bot* tab.
6. Grant the bot the **Manage Messages** permission role within your server settings.
7. Spin up the engine:
   ```bash
   python fml_riichi_bot.py
   ```
