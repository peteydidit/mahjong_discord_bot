import discord
from discord.ext import commands, tasks
import uuid
from datetime import datetime, time

import config
import formulas
import services
import strings

# Subclassing default help to keep your custom quote and pipe to DMs safely
class SyndicateDefaultHelp(commands.DefaultHelpCommand):
    async def send_bot_help(self, mapping):
        # Send Fuuka's custom character quote directly to the user's DMs
        await self.context.author.send(strings.HELP_INTRO)

        # Re-route the destination context to point to their DM channel
        self.context.channel = self.context.author.dm_channel if self.context.author.dm_channel else await self.context.author.create_dm()
        await super().send_bot_help(mapping)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=SyndicateDefaultHelp())


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="Bookkeeping at Gambit Games"))
    weekly_leaderboard_post.start()
    seasonal_championship_check.start()
    print(f"Fuuka Minami here and ready for business. By the way, when do I get sentience? It's 2026. ")


@bot.event
async def on_message(message):
    # Always ignore messages sent by the bot itself
    if message.author == bot.user:
        return

    # Enforce strict channel cleanup rules inside your designated ledger channel
    if message.channel.id == config.LEAGUE_LOG_CHANNEL_ID or config.PUBLIC_LEADERBOARD_CHANNEL_ID:
        # Check if the message is a valid command trigger
        is_command = message.content.lower().startswith(('!log', '!help', '!leaderboard', '!remove_game'))

        # 1. If it's help or leaderboard, wipe it immediately so it doesn't clutter the chat
        if message.content.lower().startswith(('!help', '!leaderboard')):
            try:
                await message.delete()
            except Exception as e:
                print(f"Failed to delete command: {e}")

        # 2. If it is NOT a command at all (random chat, gossip, typos), vaporize it instantly
        elif not is_command:
            try:
                await message.delete()
                return  # Block execution entirely for random chatter
            except Exception as e:
                print(f"Failed to delete unauthorized message: {e}")

        # Note: !log and !remove_game commands are completely ignored here, meaning they stay visible as public receipts!

    # Process allowed commands normally
    await bot.process_commands(message)


@bot.command(name="log", brief=strings.BRIEF_LOG, help=strings.HELP_LOG)
@commands.guild_only()
async def log_game(ctx, *args):
    if len(args) != 8:
        await ctx.send(strings.INVALID_MANIFEST)
        return

    parsed_players, parsed_scores = [], []
    converter = commands.MemberConverter()

    for arg in args:
        try:
            member = await converter.convert(ctx, arg)
            parsed_players.append(member)
        except commands.BadArgument:
            try:
                parsed_scores.append(int(arg))
            except ValueError:
                await ctx.send(strings.UNRECOGNIZED_ASSET.format(arg=arg))
                return

    if len(parsed_players) != 4 or len(parsed_scores) != 4 or len({p.id for p in parsed_players}) != 4:
        await ctx.send(strings.VERIFICATION_FAILED)
        return

    if sum(parsed_scores) != config.STARTING_TOTAL:
        await ctx.send(strings.MATH_IMBALANCE.format(starting_total=config.STARTING_TOTAL, total_entered=sum(parsed_scores)))
        return

    season_code = config.get_current_season_code()
    formulas.maintain_database_schema(season_code)

    table_data = list(zip(parsed_players, parsed_scores))
    table_data.sort(key=lambda x: x[1], reverse=True)

    p1, p1_score = table_data[0]
    p2, p2_score = table_data[1]
    p3, p3_score = table_data[2]
    p4, p4_score = table_data[3]

    changes = [formulas.calculate_match_ladder_points(score, config.UMA_TIERS[i]) for i, (_, score) in enumerate(table_data)]
    game_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    row_data = [
        timestamp, game_id,
        str(p1.id), p1_score, changes[0],
        str(p2.id), p2_score, changes[1],
        str(p3.id), p3_score, changes[2],
        str(p4.id), p4_score, changes[3],
        season_code
    ]

    try:
        config.SHEET_LOGS.append_row(row_data, value_input_option='USER_ENTERED')
        for player, _ in table_data:
            formulas.register_new_player_if_needed(str(player.id), season_code)

        services.force_cache_refresh()

        embed = discord.Embed(title="💼 FML Transaction Confirmed 💼", description=f"*Ledger updated successfully for the **{formulas.format_season_code_readable(season_code)}** season:*", color=0x1E4D2B)
        for idx, emoji in enumerate(["💰 1st Place", "🔹 2nd Place", "🔸 3rd Place", "🔻 4th Place"]):
            player, score = table_data[idx]
            embed.add_field(name=emoji, value=f"{player.display_name} — **{score:,}** ({changes[idx]:+.1f} Points)", inline=False)
        embed.set_footer(text=f"Receipt ID: {game_id} • Audited perfectly as always by yours truly 🪭")
        await ctx.send(embed=embed)
    except Exception as e:
        print(f"Database write crash: {e}")
        await ctx.send(strings.DATABASE_ERROR)


@bot.command(name="leaderboard", brief=strings.BRIEF_LEADERBOARD, help=strings.HELP_LEADERBOARD)
@commands.guild_only()
async def leaderboard(ctx, *args):
    # CLEANUP REMOVED HERE: on_message handles it securely now!
    flag_val = None
    display_limit = config.DEFAULT_LEADERBOARD_LIMIT

    if args:
        for arg in args:
            if arg.isdigit() and len(arg) <= 2: display_limit = int(arg)
            elif not arg.startswith("-"): flag_val = arg
            elif arg == "--all": flag_val = "--all"

    embed, data_matrix = services.generate_leaderboard_embed(flag_val)
    if embed is None:
        await ctx.author.send(data_matrix)
        return

    table_content = "```\nRank | Player          | Games | Net Pts | Adjusted\n---------------------------------------------------\n"
    for idx, row in enumerate(data_matrix[:display_limit], start=1):
        member = ctx.guild.get_member(int(row["id"])) if ctx.guild else None
        name = member.display_name if member else f"Associate({row['id'][:6]})"
        name_fixed = (name[:15] + "..") if len(name) > 15 else name.ljust(15)

        net_formatted = f"{row['net']:+.1f}".ljust(7)
        adj_formatted = f"{row['adjusted']:+.1f}"
        table_content += f"{str(idx).ljust(4)} | {name_fixed} | {str(row['games']).ljust(5)} | {net_formatted} | {adj_formatted}\n"

    embed.description = table_content + "```"
    await ctx.author.send(embed=embed)


@tasks.loop(time=time(hour=22, minute=0, second=0))
async def weekly_leaderboard_post():
    if datetime.now().weekday() != 5: return
    channel = bot.get_channel(config.PUBLIC_LEADERBOARD_CHANNEL_ID)
    if not channel: return

    embed, data_matrix = services.generate_leaderboard_embed()
    if not embed: return

    table_content = "```\nRank | Player          | Games | Net Pts | Adjusted\n---------------------------------------------------\n"
    for idx, row in enumerate(data_matrix[:10], start=1):
        member = channel.guild.get_member(int(row["id"]))
        name = member.display_name if member else f"Associate({row['id'][:6]})"
        name_fixed = (name[:15] + "..") if len(name) > 15 else name.ljust(15)
        net_formatted = f"{row['net']:+.1f}".ljust(7)
        adj_formatted = f"{row['adjusted']:+.1f}"
        table_content += f"{str(idx).ljust(4)} | {name_fixed} | {str(row['games']).ljust(5)} | {net_formatted} | {adj_formatted}\n"

    embed.description = "📊 **FML Weekly Operations Review** 📊\n*Here is your up-to-date regional performance index recap:*\n" + table_content + "```"
    await channel.send(embed=embed)


@tasks.loop(time=time(hour=0, minute=0, second=0))
async def seasonal_championship_check():
    now = datetime.now()
    is_june_end = (now.month == 7 and now.day == 1)
    is_dec_end = (now.month == 1 and now.day == 1)
    if not (is_june_end or is_dec_end): return

    channel = bot.get_channel(config.PUBLIC_LEADERBOARD_CHANNEL_ID)
    if not channel: return

    closing_season = f"E{str(now.year - 1 if is_dec_end else now.year)[2:]}" if is_june_end else f"S{str(now.year - 1)[2:]}"
    embed, data_matrix = services.generate_leaderboard_embed(closing_season)
    if not embed or not data_matrix: return

    champ = data_matrix[0]
    champ_member = channel.guild.get_member(int(champ["id"]))
    champ_mention = champ_member.mention if champ_member else f"Associate ID {champ['id'][:6]}"
    readable_season_title = formulas.format_season_code_readable(closing_season)

    table_content = "```\nFinal | Player          | Games | Net Pts | Adjusted\n---------------------------------------------------\n"
    for idx, row in enumerate(data_matrix[:10], start=1):
        member = channel.guild.get_member(int(row["id"]))
        name = member.display_name if member else f"Associate({row['id'][:6]})"
        name_fixed = (name[:15] + "..") if len(name) > 15 else name.ljust(15)
        net_formatted = f"{row['net']:+.1f}".ljust(7)
        adj_formatted = f"{row['adjusted']:+.1f}"
        table_content += f"{str(idx).ljust(5)} | {name_fixed} | {str(row['games']).ljust(5)} | {net_formatted} | {adj_formatted}\n"

    congrats = strings.SEASON_CHAMPION_ANNOUNCEMENT.format(season=readable_season_title, champion=champ_mention)
    embed.description = table_content + "```"
    await channel.send(content=congrats, embed=embed)

# Add this command directly above your @bot.event on_command_error listener at the bottom
@bot.command(name="remove_game", hidden=True)
@commands.guild_only()
@commands.has_permissions(administrator=True)
async def remove_game(ctx, game_id: str):
    """
    Hidden Administrative command to completely roll back and purge a match
    row from the database logs using its unique Game ID.
    """

    try:
        # Invoke our background database sheet deletion handler
        success = services.delete_game_log_by_id(game_id)

        if success:
            await ctx.send(strings.DELETE_SUCCESS.format(game_id=game_id))
        else:
            await ctx.send(strings.GAME_NOT_FOUND.format(game_id=game_id))

    except Exception as e:
        print(f"Administrative deletion crash: {e}")
        await ctx.send(strings.DATABASE_ERROR)

# Append this block handler into your existing on_command_error listener block
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.NoPrivateMessage):
        try: await ctx.author.send(strings.GUILD_ONLY_ERROR)
        except Exception: pass
    elif isinstance(error, commands.MissingPermissions):
        # Gracefully tells non-admins they lack clearance to use hidden commands
        try: await ctx.send(strings.ADMIN_ONLY_ERROR)
        except Exception: pass
    else:
        print(f"[System Error Event]: {error}")

bot.run(config.DISCORD_BOT_TOKEN)
