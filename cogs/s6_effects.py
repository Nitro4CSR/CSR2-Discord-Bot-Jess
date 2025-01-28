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

class S6ECog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="csr2_s6_effects", description="❗Select one more variable from above❗ Searches for CSR2 Stage 6 effects")
    @app_commands.describe(car="Accepts Ingame names, code names and Unique IDs. The later 2 can be found at the bottom of a searched car", rarity="Select an option from above", tier="Select an option from Above", csr2_version="The CSR2 version the car was released in format: `<OTA_version (optional)> <release_version>`")
    @app_commands.choices(rarity=[app_commands.Choice(name="5 Gold Stars", value="(LENGTH(s6_effects.★) == 125 AND s6_effects.★ LIKE '<:G%')"), app_commands.Choice(name="5 Purple Stars", value="(LENGTH(s6_effects.★) == 125 AND s6_effects.★ LIKE '<:P%')"), app_commands.Choice(name="5 Stars", value="LENGTH(s6_effects.★) == 125"), app_commands.Choice(name="4 Gold Stars", value="LENGTH(s6_effects.★) == 100 AND s6_effects.★ LIKE '<:G%')"), app_commands.Choice(name="4 Purple Stars", value="(LENGTH(s6_effects.★) == 100 AND s6_effects.★ LIKE '<:P%')"), app_commands.Choice(name="4 Stars", value="LENGTH(s6_effects.★) == 100"), app_commands.Choice(name="3 Gold Stars", value="(LENGTH(s6_effects.★) == 75 AND s6_effects.★ LIKE '<:G%')"), app_commands.Choice(name="3 Purple Stars", value="(LENGTH(s6_effects.★) == 75 AND s6_effects.★ LIKE '<:P%')"), app_commands.Choice(name="3 Stars", value="LENGTH(s6_effects.★) == 75"), app_commands.Choice(name="2 Gold Stars", value="(LENGTH(s6_effects.★) == 50 AND s6_effects.★ LIKE '<:G%')"), app_commands.Choice(name="2 Purple Stars", value="(LENGTH(s6_effects.★) == 50 AND s6_effects.★ LIKE '<:P%')"), app_commands.Choice(name="2 Stars", value="LENGTH(s6_effects.★) == 50"), app_commands.Choice(name="1 Gold Stars", value="(LENGTH(s6_effects.★) == 25 AND s6_effects.★ LIKE '<:G%')"), app_commands.Choice(name="1 Purple Stars", value="(LENGTH(s6_effects.★) == 25 AND s6_effects.★ LIKE '<:P%')"), app_commands.Choice(name="1 Stars", value="LENGTH(s6_effects.★) == 25"), app_commands.Choice(name="Non Star", value="0 Stars")])
    @app_commands.choices(tier=[app_commands.Choice(name="Tier 5/T5", value="<:T5:1331668428318183467>"), app_commands.Choice(name="Tier 4/T4", value="<:T4:1331668411394035794>"), app_commands.Choice(name="Tier 3/T3", value="<:T3:1331668398567850126>"), app_commands.Choice(name="Tier 2/T2", value="<:T2:1331668383996838011>"), app_commands.Choice(name="Tier 1/T1", value="<:T1:1331668370902356039>")])
    async def s6e_command(self, interaction: discord.Interaction, car: str = None, rarity: str = None, tier: str = None, csr2_version: str = None):
        logger.info(f"The following command has been used: /csr2_stage6_effects car: {car}, rarity: {rarity}, tier: {tier} csr2_version: {csr2_version}")
        log = f"The following command has been used: /csr2_stage6_effects car: {car}, rarity: {rarity}, tier: {tier} csr2_version: {csr2_version}"
        await interaction.response.defer()

        if any([car, rarity, tier, csr2_version]):
            try:
                log = await self.fetch_and_send_s6e(interaction, car, rarity, tier, csr2_version, log)
            except Exception as e:
                await interaction.followup.send(f"An error occurred: {e}")
                log += f"\nAn error occurred: {e}"
                await in_app_logging.send_log(self.bot, log, interaction)
        else:
            await interaction.followup.send(f"You didn't specify any variables but at least 1 is required! Please rerun the command with a defined variable")
            logger.info(f"No variable was given to  search with")
            log += f"\nNo variable was given to  search with"
            await in_app_logging.send_log(self.bot, log, interaction)

    async def fetch_and_send_s6e(self, interaction: discord.Interaction, car: str, rarity: str, tier: str, csr2_version: str, log: str):

        # Connect to the database
        DATABASE_PATH = helpers.load_external_db()
        LIMIT_FILE = helpers.load_server_limits()
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Query by different criteria
        parameters = []
        query = """\nSELECT s6_effects.UniqueID, s6_effects."DB Name", s6_effects."Ingame Name", s6_effects.Un, s6_effects.★, s6_effects."S5 - PP", s6_effects."S5 - EVO", s6_effects."S5 - NOS", s6_effects."S5 - FD", s6_effects."S5 - TIRES", s6_effects."S5 - DYNO", s6_effects.Engine, s6_effects.Turbo, s6_effects.Intake, s6_effects.NOS, s6_effects.Body, s6_effects.Tires, s6_effects.Trans, s6_effects."is EV?"\nFROM s6_effects"""

        if csr2_version:
            query += """\nJOIN info ON s6_effects.UniqueID = info.UniqueID"""

        if any([car, rarity, tier, csr2_version]):
            query += """\nWHERE"""

        if car:
            # Validate the input value
            primary_key_valid = car.startswith('T') and len(car) > 1 and car[1] in '12345'
            db_name_valid = "_" in car
            if primary_key_valid:
                query += """ s6_effects.UniqueID COLLATE NOCASE LIKE ?"""
            elif db_name_valid:
                query += """ s6_effects.\"DB Name\" COLLATE NOCASE LIKE ?"""
            else:
                query += """ s6_effects.\"Ingame Name\" COLLATE NOCASE LIKE ?"""
            parameters.append(f"%{car}%")

        # Add rarity and tier filter if provided
        if rarity:
            if car:
                query += """ AND"""
            query += f""" {rarity}"""
        if tier:
            if any([car, rarity]):
                query += """ AND"""
            query += """ s6_effects.Un LIKE ?"""
            parameters.append(f"%{tier}%")
        if csr2_version:
            if "OTA" in csr2_version:
                csr2_version = f"""Added into the game in {csr2_version[:4]} Update {csr2_version[5:]}"""
            else:
                csr2_version = f"""Added into the game in Update {csr2_version}"""
            if any([car, rarity, tier]):
                query += """ AND"""
            query += """ info."Vision Info" LIKE ?"""
            parameters.append(f"{csr2_version}%")

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
            logger.info(f"Limit on {server_name} ({server_id}): {limit}")
            log += f"\nLimit on {server_name} ({server_id}): {limit}"

            if limit == 0 or len(rows) <= limit:
                logger.info(f"Sending in Channel")
                log += f"\nSending in Channel"
                log = await self.send_s6e_in_channel(interaction, rows, log, direct_match=True)
            else:
                logger.info(f"Sending in DMs")
                log += f"\nSending in DMs"
                log = await self.send_s6e_in_dm(interaction, rows, log)
        else:
            logger.info(f"No direct matches found, using cutoff to potentially recover")
            log += f"\nNo direct matches found, using cutoff to potentially recover"
            parameters = []
            similar_entries_query = ("""\nSELECT records."Ingame Name Clarification", records.UniqueID, records.★\nFROM records""")

            if csr2_version:
                similar_entries_query += """\nJOIN info ON records.UniqueID = info.UniqueID"""

            if any([rarity, tier, csr2_version]):
                similar_entries_query += """\nWHERE"""""

            if rarity:
                similar_entries_query += f""" {rarity}"""
            if tier:
                if rarity:
                    similar_entries_query += """ AND"""
                similar_entries_query += """ records.Un LIKE ?"""
                parameters.append(f"%{tier}%")
            if csr2_version:
                if rarity or tier:
                    similar_entries_query += """ AND"""
                similar_entries_query += """ info."Vision Info" LIKE ?"""
                parameters.append(f"{csr2_version}")

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
                            await self.fetch_and_send_s6e_by_unique_id(interaction, selected_unique_id, log)
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
        return log

    async def fetch_and_send_s6e_by_unique_id(self, interaction: discord.Interaction, unique_id: str, log: str):
        # Connect to the database
        DATABASE_PATH = helpers.load_external_db()
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        query = """\nSELECT UniqueID, "DB Name", "Ingame Name", Un, ★, "S5 - PP", "S5 - EVO", "S5 - NOS", "S5 - FD", "S5 - TIRES", "S5 - DYNO", Engine, Turbo, Intake, NOS, Body, Tires, Trans, "Is EV?"\nFROM s6_effects\nWHERE UniqueID = ?"""

        logger.info(f"The following query has been used: {query}\nThe following parameters were used: {(unique_id,)}")
        log += f"\nThe following query has been used: {query}\nThe following parameters were used: {(unique_id,)}"
        
        try:
            logger.info(f"Querying with UniqueID from Recovery.")
            log += f"\nQuerying with UniqueID from Recovery."
            cursor.execute(query, (unique_id,))
            rows = cursor.fetchall()
        except sqlite3.OperationalError as e:
            await interaction.response.send_message(f"Database error occurred: {e}", ephemeral=True)
            await in_app_logging.send_log(self.bot, log, interaction)
            conn.close()
            return
        
        if rows:
            logger.info(f"Query success")
            log += f"\nQuery success"
            await self.send_s6e_in_channel(interaction, rows, log, direct_match=False)
        else:
            logger.info(f"Query found no S6E entry... Sending contribute notice")
            log += f"\nQuery found no S6E entry... Sending contribute notice"
            try:
                await interaction.response.send_message("Selected car not found in Stage 6 Effects database. [Contribute Now](https://docs.google.com/spreadsheets/d/1pBamDQTOcWyJoUowrXM05Tj567UVAti1VA8zWsSlrhM/edit)")
            except Exception as e:
                print(f"Follow-up interaction expired: {e}")
                await in_app_logging.send_log(self.bot, log, interaction)

        conn.close()
        return log

    async def send_s6e_in_channel(self, interaction: discord.Interaction, rows: list, log: str, direct_match: bool):
        if direct_match:
            await interaction.followup.send("Fetching Stage 6 effects, please wait...", ephemeral=True)
        else:
            await interaction.response.send_message("The interaction has expired. Please try again.", ephemeral=True)

        messages, log = self.construct_results(rows, log)

        if messages:
            for batch in messages:
                try:
                    await interaction.followup.send(embeds=batch)
                    await asyncio.sleep(0.5)
                except Exception as e:
                    print(f"Follow-up interaction expired: {e}")
                    log += f"\nFollow-up interaction expired: {e}"
                    await in_app_logging.send_log(self.bot, log, interaction)
                    return
            logger.info(f"Results sent in Channel.")
            log += f"\nResults sent in Channel."
            await in_app_logging.send_log(self.bot, log, interaction)
        return log
                
    async def send_s6e_in_dm(self, interaction: discord.Interaction, rows: list, log: str):
        try:
            await interaction.followup.send(f"Sending results via DMs because the amount of results exceeds the maximum allowed results on this server.")
            user = interaction.user

            try:
                await user.send("Fetching Stage 6 effects, please wait...")

                messages, log = self.construct_results(rows, log)

                if messages:
                    for batch in messages:
                        try:
                            await user.send(embeds=batch)
                            await asyncio.sleep(0.5)
                        except discord.Forbidden:
                            logger.info("DMs are closed or closed for non-friended accounts. No records will be sent. Please open your DMs and try again.")
                            log += "DMs are closed or closed for non-friended accounts. No records will be sent. Please open your DMs and try again."
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
        return log

    def construct_results(self, rows: list, log: str):
        logger.info(f"Constructing Embeds")
        log += f"\nConstructing Embeds"
        messages = []
        batch = []
        for row in rows:
            if row[18] == 'false':
                categories = ["Engine      ", "Turbo       ", "Intake      ", "NOS         ", "Body        ", "Tires       ", "Transmission"]
            else:
                categories = ["Motor       ", "Battery     ", "Inverter    ", "Overboost   ", "Body        ", "Tires       ", "Transmission"]

            values = row[11:18]
            offsets = [round(float(values[i]) - float(row[10]), 3) for i in range(7)]
            combined = sorted(zip(values, categories, offsets))
            sorted_values, sorted_categories, sorted_offsets = zip(*combined)

            # Create the chart string
            chart_lines = [f"{category}   {offset:+.3f}   {value:.3f}" for category, offset, value in zip(sorted_categories, sorted_offsets, sorted_values)]
            chart = "\n".join(chart_lines)

            embed = discord.Embed(
                title=row[2],  # Ingame Name Clarification
                description=f"",
                color=discord.Color(0xff00ff)
            )
            embed.add_field(name=f"# {row[3]}   {row[4]}", value=f"**S5-PP: {row[5]}\nS5-EVO: {row[6]}\n\n**", inline=False)
            embed.add_field(name=f"S5-Nos: {row[7]}", value=f"", inline=True)
            embed.add_field(name=f"S5-FD: {float(row[8]):.2f}", value="", inline=True)
            embed.add_field(name=f"S5-TP: {row[9]}", value="", inline=True)
            embed.add_field(name=f"S5-Dyno: {float(row[10]):.3f}", value=f"")
            embed.add_field(name=f"Best Stage 6: {sorted_categories[0]} ({float(sorted_offsets[0]):+.3f}) ({float(sorted_values[0]):.3f})", value=f"`\nPart           Offset   Time\n{chart}`", inline=False)
            embed.set_footer(text=f"{row[0]} - {row[1]}")
            embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')

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
    await bot.add_cog(S6ECog(bot))
