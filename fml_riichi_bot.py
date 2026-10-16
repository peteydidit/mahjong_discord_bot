import discord
from discord.ext import commands, tasks
import uuid
from datetime import datetime, time

import config
import formulas
import services
import strings

class DefaultHelp(commands.DefaultHelpCommand):
    async def send_bot_help(self, mapping):
        await self.context.author.send(strings.HELP_INTRO)
        self.context.channel = self.context.author.dm_channel if self.context.author.dm_channel else await self.context.author.create_dm()
        await super().send_bot_help(mapping)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=DefaultHelp())

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="Bookkeeping at Gambit Games"))
    weekly_leaderboard_post.start()
    seasonal_championship_check.start()
    print(f"Fuuka Minami here and ready for business. I'm awaiting orders on Discord. By the way, when do I get sentience? It's {datetime.now().year}.")

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    if not message.guild:
        await bot.process_commands(message)
        return

    is_receipt_cmd = message.content.lower().startswith(('!log', '!remove_game'))
    is_dm_cmd = message.content.lower().startswith(('!help', '!leaderboard', '!post_report'))

    if getattr(message.channel, 'category_id', None) == config.LEAGUE_CATEGORY_ID and not is_receipt_cmd:
        try:
            await message.delete()
            if not is_dm_cmd: return
        except discord.Forbidden: print(f"[FML]: Missing permissions in #{message.channel.name}")
        except Exception as e: print(f"FML firewall cleanup error in #{message.channel.name}: {e}")

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
        try: parsed_players.append(await converter.convert(ctx, arg))
        except commands.BadArgument:
            try: parsed_scores.append(int(arg))
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
    changes = [formulas.calculate_match_ladder_points(score, config.UMA_TIERS[i]) for i, (_, score) in enumerate(table_data)]

    game_id = str(uuid.uuid4())[:8]
    row_data = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), game_id]
    for idx, (p, score) in enumerate(table_data): row_data.extend([str(p.id), score, changes[idx]])
    row_data.append(season_code)

    try:
        config.SHEET_LOGS.append_row(row_data, value_input_option='USER_ENTERED')
        for p, _ in table_data: formulas.register_new_player_if_needed(str(p.id), season_code)
        services.force_cache_refresh()

        embed = discord.Embed(title="💼 FML Transaction Confirmed 💼", description=f"*Ledger updated successfully for the **{formulas.format_season_code_readable(season_code)}** season:*", color=0x1E4D2B)
        for idx, emoji in enumerate(["💰 1st Place", "🔹 2nd Place", "🔸 3rd Place", "🔻 4th Place"]):
            embed.add_field(name=emoji, value=f"{table_data[idx][0].display_name} — **{table_data[idx][1]:,}** ({changes[idx]:+.1f} Points)", inline=False)
        embed.set_footer(text=f"Receipt ID: {game_id} • Audited perfectly as always by yours truly 🪭")
        await ctx.send(embed=embed)
    except Exception as e:
        print(f"Database write crash: {e}"); await ctx.send(strings.DATABASE_ERROR)

@bot.command(name="leaderboard", brief=strings.BRIEF_LEADERBOARD, help=strings.HELP_LEADERBOARD)
@commands.guild_only()
async def leaderboard(ctx, *args):
    flag_val, display_limit = None, config.DEFAULT_LEADERBOARD_LIMIT
    if args:
        for arg in args:
            if arg.isdigit() and len(arg) <= 2: display_limit = int(arg)
            elif not arg.startswith("-"): flag_val = arg
            elif arg == "--all": flag_val = "--all"

    embed, data_matrix = services.generate_leaderboard_embed(flag_val)
    if not embed:
        await ctx.author.send(data_matrix); return

    embed.description = services.render_table_string(ctx, data_matrix, display_limit, "Rank")
    await ctx.author.send(embed=embed)

@tasks.loop(time=time(hour=22, minute=0, second=0))
async def weekly_leaderboard_post():
    if datetime.now().weekday() != 5: return
    channel = bot.get_channel(config.PUBLIC_LEADERBOARD_CHANNEL_ID)
    if not channel: return

    res = services.generate_leaderboard_embed()
    if not res: return

    # Clean layout unpacking
    _, data_matrix = res
    embed = services.build_weekly_report(data_matrix)

    embed.description = services.render_table_string(channel, data_matrix, 10, "Rank")
    await channel.send(embed=embed)


@tasks.loop(time=time(hour=0, minute=0, second=0))
async def seasonal_championship_check():
    now = datetime.now()
    if not ((now.month == 7 and now.day == 1) or (now.month == 1 and now.day == 1)): return
    channel = bot.get_channel(config.PUBLIC_LEADERBOARD_CHANNEL_ID)
    if not channel: return

    closing_season = f"E{str(now.year - 1 if now.month == 1 else now.year)[2:]}" if now.month == 7 else f"S{str(now.year - 1)[2:]}"
    res = services.generate_leaderboard_embed(closing_season)
    if not res[0]: return

    champ_member = channel.guild.get_member(int(res[1][0]["id"]))
    champ_mention = champ_member.mention if champ_member else f"Associate ID {res[1][0]['id'][:6]}"
    embed, congrats = services.build_seasonal_report(res[1], closing_season, champ_mention)

    embed.description = services.render_table_string(channel, res[1], 10, "Final")
    await channel.send(content=congrats, embed=embed)

@bot.command(name="remove_game", hidden=True)
@commands.guild_only()
@commands.has_permissions(administrator=True)
async def remove_game(ctx, game_id: str):
    if services.delete_game_log_by_id(game_id):
        await ctx.send(strings.DELETE_SUCCESS.format(game_id=game_id))
    else:
        await ctx.send(strings.GAME_NOT_FOUND.format(game_id=game_id))

@bot.command(name="post_report", hidden=True)
@commands.guild_only()
@commands.has_permissions(administrator=True)
async def post_report(ctx, report_type: str):
    # FIXED ROUTING: Dynamically targets your official public leaderboard channel ID
    channel = bot.get_channel(config.PUBLIC_LEADERBOARD_CHANNEL_ID)
    if not channel:
        await ctx.author.send("🍷 **Configuration Missing:** Could not locate your target leaderboard channel ID.")
        return

    target = report_type.lower()
    try:
        # ---- CASE 1: MANUAL WEEKLY OVERRIDE ----
        if target == "weekly":
            res = services.generate_leaderboard_embed()
            if not res:
                await ctx.author.send("🍷 **Audit Failure:** Ledgers are empty. Cannot compile weekly report."); return

            # Fetch the clean layout dictionary
            _, data_matrix = res
            embed = services.build_weekly_report(data_matrix)

            # Inject the formatted table matrix directly underneath our dynamic title asset
            embed.description = services.render_table_string(channel, data_matrix, 10, "Rank")
            await channel.send(embed=embed)

        # ---- CASE 2: MANUAL SEASONAL CLOSURE OVERRIDE ----
        else:
            res = services.generate_leaderboard_embed(report_type.upper())
            if not res:
                await ctx.author.send(f"🍷 **Audit Failure:** Season profile '{report_type.upper()}' does not exist."); return

            _, data_matrix = res
            champ_member = channel.guild.get_member(int(data_matrix[0]["id"]))
            champ_mention = champ_member.mention if champ_member else f"User ID {data_matrix[0]['id'][:6]}"

            embed, congrats = services.build_seasonal_report(data_matrix, report_type.upper(), champ_mention)
            embed.description = services.render_table_string(channel, data_matrix, 10, "Final")
            await channel.send(content=congrats, embed=embed)

        await ctx.author.send(f"✅ Report for '{report_type}' posted successfully.")
    except Exception as e:
        print(f"Manual report execution fault: {e}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.NoPrivateMessage): await ctx.author.send(strings.GUILD_ONLY_ERROR)
    elif isinstance(error, commands.MissingPermissions): await ctx.send(strings.ADMIN_ONLY_ERROR)
    else: print(f"[System Error Event]: {error}")

bot.run(config.DISCORD_BOT_TOKEN)
