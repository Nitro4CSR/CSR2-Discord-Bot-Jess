import discord
from discord.ext import commands
from discord import app_commands
import aiosqlite
from difflib import get_close_matches
import aiofiles
import asyncio
import json
import os
import in_app_logging
import helpers

logger = helpers.load_logging()

class WRCommandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="csr2_wr", description="❗Select one more variable from above❗ Searches for CSR2 World Records and setups")
    @app_commands.describe(car="Accepts Ingame names, code names and Unique IDs. The later 2 can be found at the bottom of a searched car", rarity="Select an option from Above", tier="Select an option from Above", csr2_version="The CSR2 version the car was released in format: `<OTA_version (optional)> <release_version>`")
    @app_commands.choices(rarity=helpers.load_command_options_rarity())
    @app_commands.choices(tier=helpers.load_command_options_tier())
    async def wr_command(self, interaction: discord.Interaction, car: str = None, rarity: str = None, tier: str = None, csr2_version: str = None):
        logger.info(f"WR - The following command has been used: /csr2_wr car: {car} rarity: {rarity} tier: {tier} csr2_version: {csr2_version}")
        log = f"WR - The following command has been used: /csr2_wr car: {car} rarity: {rarity} tier: {tier} csr2_version: {csr2_version}"
        await interaction.response.defer()

        if any([car, rarity, tier, csr2_version]):
            try:
                await fetch_and_send_records(self.bot, interaction, car, rarity, tier, csr2_version, log)
            except Exception as e:
                await interaction.followup.send(f"An error occurred: {e}")
                logger.error(f"WR - An error occurred: {e}")
                log += f"\nWR - An error occurred: {e}"
                await in_app_logging.send_log(self.bot, log, 0, 1, interaction)
        else:
            await interaction.followup.send(f"You didn't specify any variables but at least 1 is required! Please rerun the command with a defined variable", ephemeral=True)
            logger.info(f"WR - No variable was given to  search with")
            log += f"\nWR - No variable was given to  search with"
            await in_app_logging.send_log(self.bot, log, 2, 1, interaction)

async def fetch_and_send_records(bot: commands.Bot, interaction: discord.Interaction, car: str, rarity: str, tier: str, csr2_version: str, log: str):

    DATABASE_PATH = await helpers.load_file_path('EDB')
    SERVER_LIMIT_FILE = await helpers.load_file_path('server_limits')
    USER_LIMIT_FILE = await helpers.load_file_path('user_limits')
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        async with conn.cursor() as cursor:

            parameters = []
            query = """\nSELECT records.UniqueID, records."DB Name", records."Ingame Name Clarification", records.Un, records.★, records."WR-PP", records."WR-EVO", records."WR-NITRO", records."WR-FD", records."WR-TIRE", records."WR-DYNO", records."WR-BEST ET", records."WR Addon", records."SHIFT Links", records."WR-DRIVER"\nFROM records"""
        
            if csr2_version:
                query += """\nJOIN info ON records.UniqueID = info.UniqueID"""
        
            if any([car, rarity, tier, csr2_version]):
                query += """\nWHERE"""
        
            if car:
                primary_key_valid = car.startswith('T') and len(car) > 1 and car[1] in '12345'
                db_name_valid = "_" in car
                if primary_key_valid:
                    query += """ records.UniqueID COLLATE NOCASE LIKE ?"""
                elif db_name_valid:
                    query += """ records."DB Name" COLLATE NOCASE LIKE ?"""
                else:
                    query += """ records."Ingame Name Clarification" COLLATE NOCASE LIKE ?"""
                parameters.append(f"%{car}%")
        
            if rarity:
                if car:
                    query += """ AND"""
                query += """ records.★ LIKE ?"""
                parameters.append(rarity)
            if tier:
                if any([car, rarity]):
                    query += """ AND"""
                query += """ records.Un == ?"""
                parameters.append(tier)
            if csr2_version:
                if "OTA" in csr2_version:
                    csr2_version = f"""Added into the game in {csr2_version[:4]} Update {csr2_version[5:]}%"""
                else:
                    csr2_version = f"""Added into the game in Update {csr2_version}%"""
                if any([car, rarity, tier]):
                    query += """ AND"""
                query += """ info.\"Vision Info\" LIKE ?"""
                parameters.append(f"{csr2_version}")
        
            logger.info(f"WR - The following query has been used: {query}\nThe following parameters were used: {parameters}")
            log += f"\nWR - The following query has been used: {query}\nThe following parameters were used: {parameters}"
        
            try:
                await cursor.execute(query, parameters)
                rows = await cursor.fetchall()
            except aiosqlite.OperationalError as e:
                await interaction.followup.send(f"Database error occurred: {e}", ephemeral=True)
                await in_app_logging.send_log(bot, log, 0, 1, interaction)
                await conn.close()
                return
        
            if rows:
                logger.info(f"WR - {len(rows)} results found")
                log += f"\nWR - {len(rows)} results found"
                if interaction.guild:
                    async with aiofiles.open(SERVER_LIMIT_FILE, 'r') as file:
                        server_limits = json.loads(await file.read())
                    server_limit = server_limits.get(str(interaction.guild.id), {"PostLimit": 0})["PostLimit"]
                    logger.info(f"WR - Limit on {interaction.guild.name} ({interaction.guild.id}): {server_limit}")
                    log += f"\nWR - Limit on {interaction.guild.name} ({interaction.guild.id}): {server_limit}"
                    if server_limit == 0 or len(rows) <= server_limit:
                        logger.info(f"WR - Sending in Channel")
                        log += f"\nWR - Sending in Channel"
                        log = await send_records_in_channel(bot, interaction, rows, log, True)
                        await in_app_logging.send_log(bot, log, 2, 1, interaction)
                        return
                async with aiofiles.open(USER_LIMIT_FILE, 'r') as file:
                    user_limits = json.loads(await file.read())
                user_limit = user_limits.get(str(interaction.user.id), {"PostLimit": 10})["PostLimit"]
                logger.info(f"WR - Limit for {interaction.user.name} ({interaction.user.id}): {user_limit}")
                log += f"\nWR - Limit on {interaction.user.name} ({interaction.user.id}): {user_limit}"
                if user_limit == 0 or len(rows) <= user_limit:
                    logger.info(f"WR - Sending in DMs")
                    log += f"\nWR - Sending in DMs"
                    log = await send_records_in_dm(bot, interaction, rows, log)
                else:
                    await interaction.followup.send(f"Both server limit and your personal limit are below the amount of results.\n" if interaction.guild else f"Your personal limit is below the amount of results.\n")
                    class ForceSendView(discord.ui.View):
                        def __init__(self, timeout=180):
                            super().__init__(timeout=timeout)
                
                        @discord.ui.button(label="Make an exception", style=discord.ButtonStyle.primary)
                        async def force_send_button(self, interaction_button: discord.Interaction, button: discord.ui.Button):
                            logger.info("WR - User made an exception")
                            nonlocal log
                            log += "\nWR - User made an exception"
                            await interaction_button.response.defer(ephemeral=True)
                            await send_records_in_dm(bot, interaction_button, rows, log)
                
                    message_text = (
                        f"Search results: **{len(rows)}**\n"
                        f"Your personal Limit: **{user_limit}**\n"
                        f"-# Increase your personal limit by running </csr2_limitresults:{os.getenv('CSR2_LIMITRESULTS_COMMAND')}>, entering a number and selecting `Personal` as the scope or refine your query."
                    )
                    await interaction.followup.send(message_text, ephemeral=True, view=ForceSendView())
                    logger.info("WR - User and server limit exceeded, button offered")
                    log += f"\nWR - User and server limit exceeded, button offered"
                await in_app_logging.send_log(bot, log, 2, 1, interaction)
            else:
                logger.info(f"WR - No direct matches found, using cutoff to potentially recover.")
                log += f"\nWR - No direct matches found, using cutoff to potentially recover."
                parameters = []
                similar_entries_query = ("""\nSELECT records."Ingame Name Clarification", records.UniqueID, records.Un, records.★\nFROM records""")
        
                if csr2_version:
                    similar_entries_query += """\nJOIN info ON records.UniqueID = info.UniqueID"""
        
                if any([rarity, tier, csr2_version]):
                    similar_entries_query += """\nWHERE"""
        
                if rarity:
                    similar_entries_query += """ records.★ LIKE ?"""
                    parameters.append(rarity)
                if tier:
                    if rarity:
                        similar_entries_query += """ AND"""
                    similar_entries_query += """ records.Un == ?"""
                    parameters.append(tier)
                if csr2_version:
                    if rarity or tier:
                        similar_entries_query += """ AND"""
                    similar_entries_query += """ info."Vision Info" LIKE ?"""
                    parameters.append(f"{csr2_version}")
        
                logger.info(f"WR - The following query has been used: {similar_entries_query}\nThe following parameters were used: {parameters}")
                log += f"\nWR - The following query has been used: {similar_entries_query}\nThe following parameters were used: {parameters}"
        
                await cursor.execute(similar_entries_query, parameters)
                all_entries = await cursor.fetchall()
                all_unique_ids = {row[0]: (row[1], row[2], row[3]) for row in all_entries}
        
                if car:
                    cutoff = 0.3
                else:
                    car = f"% %"
                    cutoff = 1.0

                similar_entries = get_close_matches(car.strip('%'), list(all_unique_ids.keys()), n=10, cutoff=cutoff)
        
                if similar_entries:
                    logger.info(f"WR - Recovery success with {len(similar_entries)} results.")
                    log += f"\nWR - Recovery success with {len(similar_entries)} results."

                    if len(similar_entries) > 1:
                        view = discord.ui.View(timeout=300)
                        for i, entry in enumerate(similar_entries):
                            button = discord.ui.Button(label=str(i + 1), style=discord.ButtonStyle.primary)

                            async def button_callback(interaction: discord.Interaction, entry=entry):
                                try:
                                    selected_unique_id = all_unique_ids[entry][0]
                                    await fetch_and_send_records_by_unique_id(bot, interaction, selected_unique_id, False, log)
                                except discord.errors.NotFound:
                                    await interaction.response.send_message("The interaction has expired. Please try again.", ephemeral=True)

                            button.callback = button_callback
                            view.add_item(button)

                        description_list = [
                            f"{i+1}. {entry} {await helpers.emojify_tier(all_unique_ids[entry][1])} {await helpers.emojify_rarity(all_unique_ids[entry][2])}" 
                            for i, entry in enumerate(similar_entries)
                        ]

                        embed = discord.Embed(
                            title="Did you mean one of these?",
                            description="\n".join(description_list),
                            color=discord.Color(0xff00ff)
                        )
                        embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')

                        await interaction.followup.send(embed=embed, view=view)
                    else:
                        try:
                            await fetch_and_send_records_by_unique_id(bot, interaction, all_unique_ids[similar_entries[0]][0], True, log)
                        except discord.errors.NotFound:
                            await interaction.response.send_message("The interaction has expired. Please try again.", ephemeral=True)
                else:
                    logger.info(f"WR - Recovery failed. No results found.")
                    log += f"\nWR - Recovery failed. No results found."
                    try:
                        await interaction.followup.send("No similar named cars found.")
                    except discord.NotFound:
                        logger.error("WR - Follow-up interaction expired.")
                        log += "WR - Follow-up interaction expired."
                    await in_app_logging.send_log(bot, log, 2, 1, interaction)
        
    await conn.close()

    return log

async def fetch_and_send_records_by_unique_id(bot: commands.Bot, interaction: discord.Interaction, unique_id: str, direct_match: bool, log: str):
    DATABASE_PATH = await helpers.load_file_path('EDB')
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        async with conn.cursor() as cursor:

            query = """\nSELECT "UniqueID", "DB Name", "Ingame Name Clarification", Un, ★, "WR-PP", "WR-EVO", "WR-NITRO", "WR-FD", "WR-TIRE", "WR-DYNO", "WR-BEST ET", "WR Addon", "SHIFT Links", "WR-DRIVER"\nFROM records\nWHERE UniqueID = ?"""
        
            logger.info(f"WR - The following query has been used: {query}\nThe following parameters were used: {(unique_id,)}")
            log += f"\nWR - The following query has been used: {query}\nThe following parameters were used: {(unique_id,)}"
        
            try:
                logger.info(f"WR - Querying with UniqueID from Recovery.")
                log += f"\nWR - Querying with UniqueID from Recovery."
                await cursor.execute(query, (unique_id,))
                rows = await cursor.fetchall()
            except aiosqlite.OperationalError as e:
                await interaction.followup.send(f"Database error occurred: {e}")
                logger.error(f"WR - Database error occurred: {e}")
                log += f"\nWR - Database error occurred: {e}"
                await in_app_logging.send_log(bot, log, 0, 1, interaction)
                await conn.close()
                return
        
            if rows:
                logger.info(f"WR - Query success")
                log += f"\nWR - Query success"
                await send_records_in_channel(bot, interaction, rows, log, direct_match)
            else:
                logger.info(f"WR - Query found no WR entry... Sending contribute notice")
                log += f"\nWR - Query found no WR entry... Sending contribute notice"
                try:
                    await interaction.followup.send("Selected car not found in WR database.")
                except discord.NotFound:
                    logger.error(f"WR - Follow-up interaction expired: {e}")
                    log += f"\nWR - Follow-up interaction expired: {e}"
                    await in_app_logging.send_log(bot, log, 0, 1, interaction)
        
    await conn.close()

    return log

async def send_records_in_channel(bot: commands.Bot, interaction: discord.Interaction, rows: list, log: str, direct_match: bool):
    if direct_match:
        await interaction.followup.send("Fetching records, please wait...")
    else:
        await interaction.response.send_message("Fetching records, please wait...")

    messages, log = await construct_results(rows, log)

    if messages:
        for i, batch in enumerate(messages):
            try:
                await interaction.followup.send(embeds=batch, silent=True if i != 0 else None)
                await asyncio.sleep(0.5)
            except discord.NotFound:
                logger.error("WR - Follow-up interaction expired.")
                log += "\nWR - Follow-up interaction expired."
                await in_app_logging.send_log(bot, log, 0, 1, interaction)
                return
        logger.info(f"WR - Results sent in Channel.")
        log += f"\nWR - Results sent in Channel."
        await in_app_logging.send_log(bot, log, 2, 1, interaction)

    return log

async def send_records_in_dm(bot: commands.Bot, interaction: discord.Interaction, rows: list, log: str):
    try:
        if interaction.guild:
            await interaction.followup.send(f"Sending results via DMs because the amount of results exceed the maximum allowed results on this server.")
        user = interaction.user

        try:
            await user.send("Fetching records, please wait...") if interaction.guild else await interaction.followup.send("Fetching records, please wait...")

            messages, log = await construct_results(rows, log)

            if messages:
                for i, batch in enumerate(messages):
                    try:
                        await user.send(embeds=batch, silent=True if i != 0 else None)
                        await asyncio.sleep(0.5)
                    except discord.Forbidden:
                        logger.info(f"WR - DMs are closed or closed for non friended accounts. No records will be send. Please open your DMs and try again.")
                        log += f"\nWR - DMs are closed or closed for non friended accounts. No records will be send. Please open your DMs and try again."
                        await in_app_logging.send_log(bot, log, 2, 1, interaction)
                        return
                logger.info(f"WR - Results sent in DMs.")
                log += f"\nWR - Results sent in DMs."

            await asyncio.sleep(0.5)
            try:
                if interaction.guild:
                    await interaction.followup.send(f"The results were sent to you via DM.", ephemeral=True)
                await in_app_logging.send_log(bot, log, 2, 1, interaction)
            except discord.HTTPException as e:
                if e.status == 429:
                    logger.warning(f"WR - Rate Limited caught (HTTP 429)")
                    log += f"\nWR - Rate Limited caught (HTTP 429)"
                    retry_after = int(e.response.headers.get('Retry-After', 5))
                    await asyncio.sleep(retry_after)
                    await interaction.followup.send(f"The results were sent to you via DM.", ephemeral=True)
                    await in_app_logging.send_log(bot, log, 1, 1, interaction)
        except discord.Forbidden:
            await interaction.followup.send("Unable to send DMs. Please ensure your DMs are open and try again.", ephemeral=True)
            await in_app_logging.send_log(bot, log, 2, 1, interaction)
    except discord.errors.NotFound:
        await interaction.response.send_message("The interaction has expired. Please try again.", ephemeral=True)
        await in_app_logging.send_log(bot, log, 0, 1, interaction)

    return log

async def construct_results(rows: list, log: str):
    logger.info(f"WR - Constructing Embeds")
    log += f"\nWR - Constructing Embeds"
    messages = []
    batch = []
    for row in rows:
        row = list(row)
        row[3] = await helpers.emojify_tier(row[3])
        row[4] = await helpers.emojify_rarity(row[4])
        markdown_characters = ['*', '_', '~', '#']
        escaped_text = ''
        if row[14][0] in markdown_characters:
            escaped_text = '\\'
        if isinstance(row[8], float) or row[8].replace('.', '', 1).isdigit():
            row[8] = f"{float(row[8]):.2f}"

        embed = discord.Embed(
            title=row[2],
            description=f"# {row[3]}   {row[4]}",
            color=discord.Color(0xff00ff)
        )
        embed.add_field(name=f"PP: {row[5]}\nEVO: {row[6]}\n", value=f"\n", inline=False)
        embed.add_field(name=f"Nos: {row[7]}\nFD: {row[8]}\nTP: {row[9]}\nDyno: {float(row[10]):.3f}", value=f"\n", inline=False)
        embed.add_field(name=f"WR: {float(row[11]):.3f}", value=f"**Driver: {escaped_text}{row[14]}\n**", inline=False)
        embed.add_field(name=f"Upgrades: {row[12]}", value=f"**[Shift Pattern]({row[13]})**", inline=False)
        embed.set_footer(text=f"{row[0]} - {row[1]}")
        embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')

        batch.append(embed)

        if len(batch) == 10:
            messages.append(batch)
            batch = []

    if batch:
        messages.append(batch)

    logger.info(f"WR - Embeds constructed")
    log += f"\nWR - Embeds constructed"

    return messages, log

async def setup(bot):
    await bot.add_cog(WRCommandCog(bot))
