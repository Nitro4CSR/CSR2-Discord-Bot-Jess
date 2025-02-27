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

class VisionCommandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="csr2_vision", description="❗Select one more variable from above❗ Searches for CSR2 World Records and setups")
    @app_commands.describe(car="Accepts Ingame names, code names and Unique IDs. The later 2 can be found at the bottom of a searched car", rarity="Select an option from Above", tier="Select an option from Above", csr2_version="The CSR2 version the car was released in format: `<OTA_version (optional)> <release_version>`")
    @app_commands.choices(rarity=[app_commands.Choice(name="5 Gold Stars", value="G5"), app_commands.Choice(name="5 Purple Stars", value="P5"), app_commands.Choice(name="5 Stars", value="5"), app_commands.Choice(name="4 Gold Stars", value="G4"), app_commands.Choice(name="4 Purple Stars", value="P4"), app_commands.Choice(name="4 Stars", value="4"), app_commands.Choice(name="3 Gold Stars", value="G3"), app_commands.Choice(name="3 Purple Stars", value="P3"), app_commands.Choice(name="3 Stars", value="3"), app_commands.Choice(name="2 Gold Stars", value="G2"), app_commands.Choice(name="2 Purple Stars", value="P2"), app_commands.Choice(name="2 Stars", value="2"), app_commands.Choice(name="1 Gold Stars", value="G1"), app_commands.Choice(name="1 Purple Stars", value="P1"), app_commands.Choice(name="1 Stars", value="1"), app_commands.Choice(name="Gold Star", value="G"), app_commands.Choice(name="Purple Star", value="P"), app_commands.Choice(name="Non Star", value="0")])
    @app_commands.choices(tier=[app_commands.Choice(name="Tier 5 (T5|K5|L5)", value="T5"), app_commands.Choice(name="Tier 4 (T4|K4|L4)", value="T4"), app_commands.Choice(name="Tier 3 (T3|K3|L3)", value="T3"), app_commands.Choice(name="Tier 2 (T2|K2|L2)", value="T2"), app_commands.Choice(name="Tier 1 (T1|K1|L1)", value="T1")])
    async def vison_command(self, interaction: discord.Interaction, car: str = None, rarity: str = None, tier: str = None, csr2_version: str = None):
        logger.info(f"The following command has been used: /csr2_vision car: {car} rarity: {rarity} tier: {tier} csr2_version: {csr2_version}")
        log = f"The following command has been used: /csr2_vision car: {car} rarity: {rarity} tier: {tier} csr2_version: {csr2_version}"
        await interaction.response.defer()

        if any([car, rarity, tier, csr2_version]):
            try:
                await self.fetch_and_send_records(interaction, car, rarity, tier, csr2_version, log)
            except Exception as e:
                await interaction.followup.send(f"An error occurred: {e}")
                log += f"\nAn error occurred: {e}"
                await in_app_logging.send_log(self.bot, log, interaction)
        else:
            await interaction.followup.send(f"You didn't specify any variables but at least 1 is required! Please rerun the command with a defined variable")
            logger.info(f"No variable was given to  search with")
            log += f"\nNo variable was given to  search with"
            await in_app_logging.send_log(self.bot, log, interaction)

    async def fetch_and_send_records(self, interaction: discord.Interaction, car: str, rarity: str, tier: str, csr2_version: str, log: str):

        # Connect to the database
        DATABASE_PATH = helpers.load_external_db()
        LIMIT_FILE = helpers.load_server_limits()
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Query by different criteria
        parameters = []
        query = """\nSELECT records.UniqueID, records."DB Name", records."Ingame Name Clarification", records.Un, records.★, records."WR-PP", records."WR-EVO", records."WR-NITRO", records."WR-FD", records."WR-TIRE", records."WR-DYNO", records."WR-BEST ET", records."WR Addon", records."SHIFT Links", records."WR-DRIVER", info.IMG, info."Vision Info", info."is EV?", info.thread, s6_effects."S5 - PP", s6_effects."S5 - EVO", s6_effects."S5 - Nos", s6_effects."S5 - FD", s6_effects."S5 - TIRES", s6_effects."S5 - DYNO", s6_effects.Engine, s6_effects.Turbo, s6_effects.Intake, s6_effects.NOS, s6_effects.Body, s6_effects.Tires, s6_effects.Trans\nFROM records\nLEFT JOIN info ON records.UniqueID = info.UniqueID\nLEFT JOIN s6_effects ON records.UniqueID = s6_effects.UniqueID"""

        if any([car, rarity, tier, csr2_version]):
            query += """\nWHERE"""

        if car:
            # Validate the input value
            primary_key_valid = car.startswith('T') and len(car) > 1 and car[1] in '12345'
            db_name_valid = "_" in car
            if primary_key_valid:
                query += """ records.UniqueID COLLATE NOCASE LIKE ?"""
            elif db_name_valid:
                query += """ records."DB Name" COLLATE NOCASE LIKE ?"""
            else:
                query += """ records."Ingame Name Clarification" COLLATE NOCASE LIKE ?"""
            parameters.append(f"%{car}%")

        # Add rarity and tier filter if provided
        if rarity:
            if car:
                query += """ AND"""
            query += """ records.★ LIKE ?"""
            parameters.append(f"%{rarity}%")
        if tier:
            if any([car, rarity]):
                query += """ AND"""
            query += """ records.Un LIKE ?"""
            parameters.append(f"%{tier}%")
        if csr2_version:
            if "OTA" in csr2_version:
                csr2_version = f"""Added into the game in {csr2_version[:4]} Update {csr2_version[5:]}%"""
            else:
                csr2_version = f"""Added into the game in Update {csr2_version}%"""
            if any([car, rarity, tier]):
                query += """ AND"""
            query += """ info.\"Vision Info\" LIKE ?"""
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
            logger.info(f"Limit on {server_name} ({server_id}): {limit}")
            log += f"\nLimit on {server_name} ({server_id}): {limit}"

            if limit == 0 or len(rows) <= (limit / 3):
                logger.info(f"Sending in Channel")
                log += f"\nSending in Channel"
                await self.send_records_in_channel(interaction, rows, log, direct_match=True)
            else:
                logger.info(f"Sending in DMs")
                log += f"\nSending in DMs"
                await self.send_records_in_dm(interaction, rows, log)
        else:
            logger.info(f"No direct matches found, using cutoff to potentially recover.")
            log += f"\nNo direct matches found, using cutoff to potentially recover."
            parameters = []
            similar_entries_query = ("""\nSELECT records."Ingame Name Clarification", records.UniqueID, records.★\nFROM records""")

            if csr2_version:
                similar_entries_query += """\nJOIN info ON records.UniqueID = info.UniqueID"""

            if any([rarity, tier, csr2_version]):
                similar_entries_query += """\nWHERE"""

            if rarity:
                similar_entries_query += """ records.★ LIKE ?"""
                parameters.append(f"%{rarity}%")
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
                            await self.fetch_and_send_records_by_unique_id(interaction, selected_unique_id, log)
                        except discord.errors.NotFound:
                            await interaction.response.send_message("The interaction has expired. Please try again.", ephemeral=True)

                    button.callback = button_callback
                    view.add_item(button)

                embed = discord.Embed(
                    title="Did you mean one of these?",
                    description="\n".join(f"{i+1}. {entry} ({all_unique_ids[entry][1]})" for i, entry in enumerate(similar_entries)),
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

    async def fetch_and_send_records_by_unique_id(self, interaction: discord.Interaction, unique_id: str, log: str):
        # Connect to the database
        DATABASE_PATH = helpers.load_external_db()
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        query = """\nSELECT "UniqueID", "DB Name", "Ingame Name Clarification", Un, ★, "WR-PP", "WR-EVO", "WR-NITRO", "WR-FD", "WR-TIRE", "WR-DYNO", "WR-BEST ET", "WR Addon", "SHIFT Links", "WR-DRIVER"\nFROM records\nWHERE UniqueID = ?"""

        logger.info(f"The following query has been used: {query}\nThe following parameters were used: {(unique_id,)}")
        log += f"\nThe following query has been used: {query}\nThe following parameters were used: {(unique_id,)}"

        try:
            logger.info(f"Querying with UniqueID from Recovery.")
            log += f"\nQuerying with UniqueID from Recovery."
            cursor.execute(query, (unique_id,))
            rows = cursor.fetchall()
        except sqlite3.OperationalError as e:
            await interaction.followup.send(f"Database error occurred: {e}")
            await in_app_logging.send_log(self.bot, log, interaction)
            conn.close()
            return

        if rows:
            logger.info(f"Query success")
            log += f"\nQuery success"
            await self.send_records_in_channel(interaction, rows, log, direct_match=False)
        else:
            logger.info(f"Query found no WR entry... Sending contribute notice")
            log += f"\nQuery found no WR entry... Sending contribute notice"
            try:
                await interaction.followup.send("Selected car not found in WR database.")
            except discord.NotFound:
                print("Follow-up interaction expired.")
                await in_app_logging.send_log(self.bot, log, interaction)

        conn.close()

    async def send_records_in_channel(self, interaction: discord.Interaction, rows: list, log: str, direct_match: bool):
        if direct_match:
            await interaction.followup.send("Fetching Vision data, please wait...", ephemeral=True)
        else:
            await interaction.response.send_message("Fetching Vision data, please wait...", ephemeral=True)

        messages, log = await self.construct_results(rows, log)

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

    async def send_records_in_dm(self, interaction: discord.Interaction, rows: list, log: str):
        try:
            await interaction.followup.send("Sending results via DMs because the amount of results exceeds the maximum allowed results on this server.", ephemeral=True)
            user = interaction.user

            try:
                await user.send("Fetching Vision data, please wait...")

                messages, log = await self.construct_results(rows, log)

                if messages:
                    for batch in messages:
                        try:
                            await user.send(embeds=batch)
                            await asyncio.sleep(0.5)
                        except discord.Forbidden:
                            logger.info(f"DMs are closed or closed for non friended accounts. No records will be send. Please open your DMs and try again.")
                            log += f"\nDMs are closed or closed for non friended accounts. No records will be send. Please open your DMs and try again."
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

    async def construct_results(self, rows: list, log: str):
        logger.info(f"Constructing Embeds")
        log += f"\nConstructing Embeds"
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

            if row[22] == None:
                row[22] = 0


            if row[17] == 'false':
                categories = ["Engine      ", "Turbo       ", "Intake      ", "NOS         ", "Body        ", "Tires       ", "Transmission"]
                row[17] = 'Combustion Engine Car'
            else:
                categories = ["Motor       ", "Battery     ", "Inverter    ", "Overboost   ", "Body        ", "Tires       ", "Transmission"]
                row[17] = 'Electric Car'

            if not any(x is None for x in row[24:31]):
                values = row[24:31]
                offsets = [round(float(values[i]) - float(row[24]), 3) for i in range(7)]
                combined = sorted(zip(values, categories, offsets))
                sorted_values, sorted_categories, sorted_offsets = zip(*combined)
                # Create the chart string
                chart_lines = [f"{category}   {offset:+.3f}   {value:.3f}" for category, offset, value in zip(sorted_categories, sorted_offsets, sorted_values)]
                chart = "\n".join(chart_lines)
                value = f"S5-PP: {row[19]}\nS5-EVO: {row[20]}\n\nS5-Nos: {row[21]}\nS5-FD: {float(row[22]):.2f}\nS5-TP: {row[23]}\nS5-Dyno: {float(row[24]):.3f}\n\n**Best Stage 6:** {sorted_categories[0]} ({float(sorted_offsets[0]):+.3f}) ({float(sorted_values[0]):.3f})\n`\nPart           Offset   Time\n{chart}`"
            else:
                value = f"No Stage 6 Effects for this car yet. Help us and [Contribute Now](https://docs.google.com/spreadsheets/d/1pBamDQTOcWyJoUowrXM05Tj567UVAti1VA8zWsSlrhM/edit)"

            embed = discord.Embed(
                title=row[2],  # Ingame Name Clarification
                description=f"# {row[3]}   {row[4]}",
                color=discord.Color(0xff00ff)
            )
            embed.add_field(name=f"Car Info", value=f"{row[17]}\n{row[16]}\n\n[View all Specs](https://discord.com/channels/683998568305917970/1122543660282695780/threads/{row[18]})")
            embed.add_field(name=f"World Record Tune", value=f"PP: {row[5]}\nEVO: {row[6]}\n\nNos: {row[7]}\nFD: {float(row[8]):.2f}\nTP: {row[9]}\nDyno: {float(row[10]):.3f}\n\nWR: {float(row[11]):.3f}\nDriver: {escaped_text}{row[14]}\n\nUpgrades: {row[12]}\n[Shift Pattern]({row[13]})", inline=False)
            embed.add_field(name=f"Stage 6 Effects", value=value)
            embed.set_footer(text=f"{row[0]} - {row[1]}")
            embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')
            embed.set_image(url=f"https://raw.githubusercontent.com/Nitro4CSR/{row[15]}")
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
    await bot.add_cog(VisionCommandCog(bot))
