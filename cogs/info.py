import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
from difflib import get_close_matches
import asyncio
import json
import logging
import in_app_logging
import helpers

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class InfoCommandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="csr2_info", description="❗Select one more variable from above❗ Searches for CSR2 info about cars")
    @app_commands.describe(car="Accepts Ingame names, code names and Unique IDs. The later 2 can be found at the bottom of a searched car", rarity="Select an option from Above", tier="Select an option from Above", csr2_version="The CSR2 version the car was released in format: `<OTA_version (optional)> <release_version>`")
    @app_commands.choices(rarity=[app_commands.Choice(name="5 Gold Stars", value="(LENGTH(★) == 125 AND ★ LIKE '<:G%')"), app_commands.Choice(name="5 Purple Stars", value="(LENGTH(★) == 125 AND ★ LIKE '<:P%')"), app_commands.Choice(name="5 Stars", value="LENGTH(★) == 125"), app_commands.Choice(name="4 Gold Stars", value="LENGTH(★) == 100 AND ★ LIKE '<:G%')"), app_commands.Choice(name="4 Purple Stars", value="(LENGTH(★) == 100 AND ★ LIKE '<:P%')"), app_commands.Choice(name="4 Stars", value="LENGTH(★) == 100"), app_commands.Choice(name="3 Gold Stars", value="(LENGTH(★) == 75 AND ★ LIKE '<:G%')"), app_commands.Choice(name="3 Purple Stars", value="(LENGTH(★) == 75 AND ★ LIKE '<:P%')"), app_commands.Choice(name="3 Stars", value="LENGTH(★) == 75"), app_commands.Choice(name="2 Gold Stars", value="(LENGTH(★) == 50 AND ★ LIKE '<:G%')"), app_commands.Choice(name="2 Purple Stars", value="(LENGTH(★) == 50 AND ★ LIKE '<:P%')"), app_commands.Choice(name="2 Stars", value="LENGTH(★) == 50"), app_commands.Choice(name="1 Gold Stars", value="(LENGTH(★) == 25 AND ★ LIKE '<:G%')"), app_commands.Choice(name="1 Purple Stars", value="(LENGTH(★) == 25 AND ★ LIKE '<:P%')"), app_commands.Choice(name="1 Stars", value="LENGTH(★) == 25"), app_commands.Choice(name="Non Star", value="0 Stars")])
    @app_commands.choices(tier=[app_commands.Choice(name="Tier 5/T5", value="<:T5:1331668428318183467>"), app_commands.Choice(name="Tier 4/T4", value="<:T4:1331668411394035794>"), app_commands.Choice(name="Tier 3/T3", value="<:T3:1331668398567850126>"), app_commands.Choice(name="Tier 2/T2", value="<:T2:1331668383996838011>"), app_commands.Choice(name="Tier 1/T1", value="<:T1:1331668370902356039>")])
    async def wr_command(self, interaction: discord.Interaction, car: str = None, rarity: str = None, tier: str = None, csr2_version: str = None):
        logger.info(f"The following command has been used: /csr2_info car: {car} rarity: {rarity} tier: {tier} csr2_version: {csr2_version}")
        log = f"The following command has been used: /csr2_info car: {car} rarity: {rarity} tier: {tier} csr2_version: {csr2_version}"
        await asyncio.sleep(1)
        await interaction.response.defer(ephemeral=True)

        if any([car, rarity, tier, csr2_version]):
            try:
                await self.fetch_and_send_info(interaction, car, rarity, tier, csr2_version, log)
            except Exception as e:
                await interaction.followup.send(f"An error occurred: {e}")
                log += f"\nAn error occurred: {e}"
                await in_app_logging.send_log(self.bot, log, interaction)
        else:
            await interaction.followup.send(f"You didn't specify any variables but at least 1 is required! Please rerun the command with a defined variable.")
            logger.info(f"No variable was given to  search with")
            log += f"\nNo variable was given to  search with"
            await in_app_logging.send_log(self.bot, log, interaction)

    async def fetch_and_send_info(self, interaction: discord.Interaction, car: str, rarity: str, tier: str, csr2_version: str, log: str):

        # Connect to the database
        DATABASE_PATH = helpers.load_external_db()
        LIMIT_FILE = helpers.load_server_limits()
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Query by different criteria
        parameters = []
        query = """\nSELECT "UniqueID", "DB Name", "Ingame Name", Un, ★, IMG, "Vision Info", "is EV?", "thread"\nFROM info"""

        if any([car, rarity, tier, csr2_version]):
            query += "\nWHERE"

        if car:
            # Validate the input value
            primary_key_valid = car.startswith('T') and len(car) > 1 and car[1] in '12345'
            db_name_valid = "_" in car
            if primary_key_valid:
                query += """ UniqueID COLLATE NOCASE LIKE ?"""
            elif db_name_valid:
                query += """ "DB Name" COLLATE NOCASE LIKE ?"""
            else:
                query += """ "Ingame Name" COLLATE NOCASE LIKE ?"""
            parameters.append(f"%{car}%")

        # Add rarity and tier filter if provided
        if rarity:
            if car:
                query += """ AND"""
            query += f""" {rarity}"""
        if tier:
            if any([car, rarity]):
                query += """ AND"""
            query += """ Un LIKE ?"""
            parameters.append(f"%{tier}%")
        if csr2_version:
            if "OTA" in csr2_version:
                csr2_version = f"""Added into the game in {csr2_version[:4]} Update {csr2_version[5:]}%"""
            else:
                csr2_version = f"""Added into the game in Update {csr2_version}%"""
            if any([car, rarity, tier]):
                query += """ AND"""
            query += """ "Vision Info" LIKE ?"""
            parameters.append(f"{csr2_version}")

        logger.info(f"The following query has been used: {query}\nThe following parameters were used: {parameters}")
        log += f"\nThe following query has been used: {query}\nThe following parameters were used: {parameters}"

        try:
            cursor.execute(query, parameters)
            rows = cursor.fetchall()
        except sqlite3.OperationalError as e:
            await interaction.followup.send(f"Database error occurred: {e}")
            await in_app_logging.send_log(self.bot, log, interaction)
            conn.close()
            return

        if rows:
            logger.info(f"{len(rows)} results found")
            log += f"\n{len(rows)} results found"
            # Get the server ID and check limits
            server_id = str(interaction.guild.id) if interaction.guild else None
            server_name = str(interaction.guild.name) if interaction.guild else None
            with open(LIMIT_FILE, 'r') as file:
                limits = json.load(file)
            limit = limits.get(server_id, {"PostLimit": 0})["PostLimit"]  # Default to 0 if server_id is not found
            logger.info(f"Limit on {interaction.guild.name} ({server_id}): {limit}")
            log += f"\nLimit on {interaction.guild.name} ({server_id}): {limit}"

            if limit == 0 or len(rows) <= limit:
                log = await self.send_info_in_channel(interaction, rows, log)
            else:
                log = await self.send_info_in_dm(interaction, rows, log)
        else:
            logger.info(f"No direct matches found, using cutoff to potentially recover.")
            log += f"\nNo direct matches found, using cutoff to potentially recover."
            parameters = []
            similar_entries_query = ("""\nSELECT "Ingame Name", UniqueID, ★\nFROM info""")

            if any([car, rarity, tier, csr2_version]):
                similar_entries_query += """\nWHERE"""
            if car:
                similar_entries_query += """ "Ingame Name" COLLATE NOCASE LIKE ?"""
                parameters.append(f"%{car}%")
            if rarity:
                if car:
                    similar_entries_query += " AND"
                similar_entries_query += f""" {rarity}"""
            if tier:
                if car or rarity:
                    similar_entries_query += " AND"
                similar_entries_query += """ Un LIKE ?"""
                parameters.append(f"%{tier}%")
            if csr2_version:
                if car or rarity or tier:
                    similar_entries_query += " AND"
                similar_entries_query += """ "Vision Info" LIKE ?"""
                parameters.append(f"%{csr2_version}%")

            logger.info(f"The following query has been used: {similar_entries_query}\nThe following parameters were used: {parameters}")
            log += f"\nThe following query has been used: {similar_entries_query}\nThe following parameters were used: {parameters}"

            cursor.execute(similar_entries_query, parameters)
            all_entries = cursor.fetchall()
            all_unique_ids = {row[0]: (row[1], row[2]) for row in all_entries}

            if car:
                cutoff = 0.3
            else:
                car = f"% %"
                cutoff = 1.0
            similar_entries = get_close_matches(car.strip('%'), list(all_unique_ids.keys()), n=10, cutoff=cutoff)

            if similar_entries:
                logger.info(f"Recovery success with {len(similar_entries)} results.")
                log += f"\nRecovery success with {len(similar_entries)} results."
                
                # Create a button view
                view = discord.ui.View(timeout=300)  # Set timeout for the view
                for i, entry in enumerate(similar_entries):
                    button = discord.ui.Button(label=str(i + 1), style=discord.ButtonStyle.primary)

                    async def button_callback(interaction: discord.Interaction, entry=entry):
                        try:
                            selected_unique_id = all_unique_ids[entry][0]
                            log = await self.fetch_and_send_info_by_unique_id(interaction, selected_unique_id, log)
                        except discord.errors.NotFound:
                            await interaction.response.send_message("The interaction has expired. Please try again.", ephemeral=True)

                    button.callback = button_callback
                    view.add_item(button)

                embed = discord.Embed(
                    title="Did you mean one of these?",
                    description="\n".join(f"{i+1}. {entry} ({all_unique_ids[entry][1]})" for i, entry in enumerate(similar_entries)),  # Display rarity in brackets
                    color=discord.Color(0xff00ff)
                )
                embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')

                await interaction.followup.send(embed=embed, view=view)

            else:
                logger.info(f"Recovery failed. No results found.")
                log += f"\nRecovery failed. No results found."
                try:
                    await interaction.followup.send("No similar named cars found.")
                except discord.NotFound:
                    logger.error("Follow-up interaction expired.")
                await in_app_logging.send_log(self.bot, log, interaction)

        conn.close()

    async def fetch_and_send_info_by_unique_id(self, interaction: discord.Interaction, unique_id: str, log: str):
        # Connect to the database
        DATABASE_PATH = helpers.load_external_db()
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        query = """\nSELECT UniqueID, "DB Name", "Ingame Name", Un, ★, IMG, "Vision Info", "is EV?", thread\nFROM info\nWHERE UniqueID = ?"""

        logger.info(f"The following query has been used: {query}\nThe following parameters were used: {(unique_id,)}")
        log += f"\nThe following query has been used: {query}\nThe following parameters were used: {(unique_id,)}"

        try:
            logger.info(f"Querrying with UniqueID from Recovery.")
            log += f"\nQuerrying with UniqueID from Recovery."
            cursor.execute(query, (unique_id,))
            rows = cursor.fetchall()
        except sqlite3.OperationalError as e:
            await interaction.followup.send(f"Database error occurred: {e}")
            await in_app_logging.send_log(self.bot, log, interaction)
            conn.close()
            return

        if rows:
            logger.info(f"Querry success")
            log += f"\nQuerry success"
            log = await self.send_info_in_channel(interaction, rows, log)
        else:
            try:
                await interaction.followup.send("No info found with the selected UniqueID.")
            except discord.NotFound:
                logger.error("Follow-up interaction expired.")
            await in_app_logging.send_log(self.bot, log, interaction)

        conn.close()

    async def send_info_in_channel(self, interaction: discord.Interaction, rows: list, log: str):
        await interaction.followup.send("Fetching info, please wait...")

        messages, log = self.construct_results(rows, log)

        if messages:
            for batch in messages:
                try:
                    await interaction.followup.send(embeds=batch)
                    await asyncio.sleep(0.5)
                except discord.NotFound:
                    logger.error("Follow-up interaction expired.")
                    log += "\nFollow-up interaction expired."
                    await in_app_logging.send_log(self.bot, log, interaction)
                    return
            logger.info(f"Results sent in Channel.")
            log += f"\nResults sent in Channel."
            await in_app_logging.send_log(self.bot, log, interaction)

    async def send_info_in_dm(self, interaction: discord.Interaction, rows: list, log: str):
        try:
            await interaction.followup.send(f"Sending results via DMs because amount of results exceed the maximum allowed results on this server")
            user = interaction.user
            try:
                await user.send("Fetching info, please wait...")

                messages, log = self.construct_results(rows, log)

                if messages:
                    for batch in messages:
                        try:
                            await user.send(embeds=batch)
                            await asyncio.sleep(0.5)
                        except discord.Forbidden:
                            logger.info("DMs are closed or closed for non-friended accounts. No records will be sent. Please open your DMs and try again.")
                            log += f"\nDMs are closed or closed for non-friended accounts. No records will be sent. Please open your DMs and try again."
                            await in_app_logging.send_log(self.bot, log, interaction)
                            return
                    logger.info(f"Results sent in DMs.")
                    log += f"\nResults sent in DMs."
                    await in_app_logging.send_log(self.bot, log, interaction)

                await asyncio.sleep(0.5)
                try:
                    await interaction.followup.send(f"The results were sent to you via DM.", ephemeral=True)
                    await in_app_logging.send_log(self.bot, log, interaction)
                except discord.HTTPException as e:
                    if e.status == 429:
                        logger.warning(f"Rate Limited caught (HTTP 429)")
                        log += f"\nRate Limited caught (HTTP 429)"
                        retry_after = int(e.response.headers.get('Retry-After', 5))
                        await asyncio.sleep(retry_after)
                        await interaction.followup.send(f"The results were sent to you via DM.", ephemeral=True)
                        await in_app_logging.send_log(self.bot, log, interaction)
            except discord.Forbidden:
                await interaction.followup.send("Unable to send DMs. Please ensure your DMs are open and try again.", ephemeral=True)
                await in_app_logging.send_log(self.bot, log, interaction)
        except discord.errors.NotFound:
            await interaction.response.send_message("The interaction has expired. Please try again.", ephemeral=True)
            await in_app_logging.send_log(self.bot, log, interaction)

    def construct_results(self, rows: list, log: str):
        logger.info(f"Constructing Embeds")
        log += f"\nConstructing Embeds"
        messages = []
        batch = []
        for row in rows:
            # Convert tuple to list for modification
            row_list = list(row)
            if row_list[7] == "false":
                row_list[7] = 'Combustion Engine Car'
            else:
                row_list[7] = 'Electric Car'

            embed = discord.Embed(
                title=row_list[2],  # Ingame Name
                description="",
                color=discord.Color(0xff00ff)
            )
            embed.add_field(name=f"{row[3]}   {row_list[4]}", value=f"**{row_list[7]}**")
            embed.add_field(name="Info", value=f"{row_list[6]}\n\n**[View all Specs](https://discord.com/channels/683998568305917970/1122543660282695780/threads/{row_list[8]})**", inline=False)
            embed.set_footer(text=f"{row_list[0]} - {row_list[1]}")
            embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')

            try:
                embed.set_image(url=row_list[5])
            except Exception as e:
                logger.error(f"Error setting image URL {row_list[5]}: {e}")
                log += f"\nError setting image URL {row_list[5]}: {e}"

            batch.append(embed)

            # Send batch when it reaches 10 embeds
            if len(batch) == 10:
                messages.append(batch)
                batch = []

        # Add remaining embeds if there are any
        if batch:
            messages.append(batch)

        logger.info(f"Embeds constructed")
        log += f"\nEmbeds constructed"
        return messages, log

async def setup(bot):
    await bot.add_cog(InfoCommandCog(bot))
