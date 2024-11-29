import asyncio
import discord
from discord.ext import commands
from discord import app_commands
import os
import sqlite3
from cogs import admin
import logging
import json
import in_app_logging
import helpers

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

LIMIT_FILE = helpers.load_server_limits()

class CustomSQLCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="csr2_customsql", description="Custom SQL command for CSR2.")
    @app_commands.describe(database="Choose the database to connect to.", select="The SELECT part of the SQL statement.", update="The UPDATE part of the SQL statement.", create_table="The CREATE TABLE part of the SQL statement.", insert_into="The INSERT INTO part of the SQL statement.", from_="The FROM part of the SQL statement.", set_="The SET part of the SQL statement.", where="The WHERE part of the SQL statement.")
    @app_commands.choices(database=[app_commands.Choice(name="WRs", value="EDB"), app_commands.Choice(name="tunes", value="tunes")])
    @app_commands.choices(from_=[app_commands.Choice(name="records", value="records"), app_commands.Choice(name="s6_effects", value="s6_effects"), app_commands.Choice(name="info", value="info"), app_commands.Choice(name="updates", value="updates"), app_commands.Choice(name="community_tunes", value="community_tunes")])
    async def customsql(self, interaction: discord.Interaction, database: app_commands.Choice[str], select: str = None, update: str = None, create_table: str = None, insert_into: str = None, from_: app_commands.Choice[str] = None, set_: str = None, where: str = None):
        logger.info(f"The following command has been used: /csr2_customsql database: {database} select: {select} update: {update} create_table: {create_table} insert_into: {insert_into} from_: {from_} set_: {set_} where: {where}")
        log = f"The following command has been used: /csr2_customsql database: {database} select: {select} update: {update} create_table: {create_table} insert_into: {insert_into} from_: {from_} set_: {set_} where: {where}"

        await interaction.response.defer(ephemeral=True)
        # await asyncio.sleep(1)
        # Mapping database options to paths
        database_paths = {
            "WRs": os.path.join('resources', 'WRs.db'),
            "tunes": os.path.join('resources', 'tunes.db')
        }

        # Get the database path from the selected choice
        db_path = database_paths[database.value]

        # Check for admin privileges if necessary
        if any([update, create_table, insert_into, set_]):
            logger.info(f"update, create_table, insert_into or set_ was used. Checking user permissions...")
            log += f"\nupdate, create_table, insert_into or set_ was used. Checking user permissions..."
            admin_list = await admin.load_admins()
            if interaction.user.id not in admin_list:
                logger.info(f"User is not bot admin. Exiting...")
                log += f"\nUser is not bot admin. Exiting..."
                await in_app_logging.send_log(self.bot, log, interaction)
                await interaction.response.send_message("You do not have the necessary permissions to execute this command.", ephemeral=True)
                await in_app_logging.send_log(self.bot, log, interaction)
                return
        logger.info(f"User is bot admin. Proceeding to run command...")
        log += f"\nUser is bot admin. Proceeding to run command..."

        if select == "*":
            table_columns = {
                "records": """"UniqueID", "DB Name", "Ingame Name Clarification", "Un", "★", "WR-PP", "WR-EVO", "WR-NITRO", "WR-FD", "WR-TIRE", "WR-DYNO", "WR-BEST ET", "WR Addon", "SHIFT Links", "WR-DRIVER" """,
                "s6_effects": """"UniqueID", "DB Name", "Ingame Name", "Un", "★", "S5 - PP", "S5 - EVO", "S5 - NOS", "S5 - FD", "S5 - TIRES", "S5 - DYNO", "Engine", "Turbo", "Intake", "NOS", "Body", "Tires", "Trans", "is EV?" """,
                "info": """"UniqueID", "DB Name", "Ingame Name Clarification", "Un", "★", "IMG", "Vision Info", "is EV?", "thread" """,
                "updates": """"ID", "Date", "Output Vision" """,
                "community_tunes": """"TuneID", "DB Name", "Ingame Name Clarification", "Un", "★", "PP" INTEGER, "EVO" INTEGER, "Engine/Motor" Integer, "En_st.1", "En_st.2", "En_st.3", "En_st.4", "En_st.5", "En_st.6", "Turbo/Battery" Integer, "Tu_st.1", "Tu_st.2", "Tu_st.3", "Tu_st.4", "Tu_st.5", "Tu_st.6", "Intake/Inverter" Integer, "In_st.1", "In_st.2", "In_st.3", "In_st.4", "In_st.5", "In_st.6", "Nitrous/Overboost" Integer, "Ni_st.1", "Ni_st.2", "Ni_st.3", "Ni_st.4", "Ni_st.5", "Ni_st.6", "Body" Integer, "Bo_st.1", "Bo_st.2", "Bo_st.3", "Bo_st.4", "Bo_st.5", "Bo_st.6", "Tires" Integer, "Ti_st.1", "Ti_st.2", "Ti_st.3", "Ti_st.4", "Ti_st.5", "Ti_st.6", "Transmission" Integer, "Tr_st.1", "Tr_st.2", "Tr_st.3", "Tr_st.4", "Tr_st.5", "Tr_st.6", "NITRO", "FD", "TIRE", "DYNO", "Purpose", "Usage Guide", "Creator", "Creator ID" """
            }
            select = table_columns[from_.value]

        # Constructing the SQL statement
        sql_parts = []
        if select:
            sql_parts.append(f"SELECT {select}")
        if update:
            sql_parts.append(f"UPDATE {update}")
        if create_table:
            sql_parts.append(f"CREATE TABLE {create_table}")
        if insert_into:
            sql_parts.append(f"INSERT INTO {insert_into}")
        if from_:
            sql_parts.append(f"FROM {from_.value}")
        if set_:
            sql_parts.append(f"SET {set_}")
        if where:
            sql_parts.append(f"WHERE {where}")

        sql_statement = " ".join(sql_parts)

        # Execute the SQL statement
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            if select:
                logger.info(f"running query for collecting results...")
                log += f"\nrunning query for collecting results..."
                cursor.execute(sql_statement)
                results = cursor.fetchall()
                selections = select.split(',')
                if results:
                    logger.info(f"{len(results)} results found")
                    log += f"\n{len(results)} results found"
                    server_id = str(interaction.guild.id) if interaction.guild else None
                    with open(LIMIT_FILE, 'r') as file:
                        limits = json.load(file)
                    limit = limits.get(server_id, {"PostLimit": 0})["PostLimit"]  # Default to 0 if server_id is not found
                    logger.info(f"Limit on {interaction.guild.name} ({server_id}): {limit}")
                    log += f"\nLimit on {interaction.guild.name} ({server_id}): {limit}"

                    if limit == 0 or len(results) <= limit:
                        logger.info(f"Sending in Channel")
                        log += f"\nSending in Channel"
                        log = await self.send_query_in_channel(interaction, results, selections, log)
                    else:
                        logger.info(f"Sending in DMs")
                        log += f"\nSending in DMs"
                        log = await self.send_query_in_dm(interaction, results, selections, log)
                await interaction.followup.send("Query executed successfully")
            else:
                cursor.execute(sql_statement)
                conn.commit()
                await interaction.response.send_message("SQL statement executed successfully.", ephemeral=True)

        except sqlite3.Error as e:
            await interaction.followup.send(f"An error occurred: {e}", ephemeral=True)
            log += f"\nAn error occurred: {e}"
        finally:
            await in_app_logging.send_log(self.bot, log, interaction)
            conn.close()

    @app_commands.command(name="csr2_dbstructure", description="Displays the Database structure so you can use /csr2_customsql appropriately")
    async def csr2_dbstructure(self, interaction: discord.Interaction):
        logger.info(f"The following command has been used: /csr2_dbstructure")
        log = f"The following command has been used: /csr2_dbstructure"

        embed = discord.Embed(
            title="Database Structure",
            description="## tunes.db\n# community_tunes\n- `TuneID`: INTEGER (PRIMARY KEY)\n- `DB Name`: TEXT\n- `Ingame Name Clarification`: TEXT\n- `Un`: TEXT\n- `★`: TEXT\n- `PP`: TEXT\n- `EVO`: TEXT\n- `Engine/Motor`: INTEGER\n- `En_st.1`: INTEGER`\n- `En_st.2`: INTEGER`\n- `En_st.3`: INTEGER`\n- `En_st.4`: INTEGER`\n- `En_st.5`: INTEGER`\n- `En_st.6`: INTEGER`\n- `Turbo/Battery`: INTEGER\n- `Tu_st.1`: INTEGER\n-  `Tu_st.2`: INTEGER\n-  `Tu_st.3`: INTEGER\n-  `Tu_st.4`: INTEGER\n-  `Tu_st.5`: INTEGER\n-  `Tu_st.6`: INTEGER\n- `Intake/Inverter`: INTEGER\n- `In_st.1`: INTEGER\n-  `In_st.2`: INTEGER\n-  `In_st.3`: INTEGER\n-  `In_st.4`: INTEGER\n-  `In_st.5`: INTEGER\n-  `In_st.6`\n- `Nitrous/Overboost`: INTEGER\n- `Ni_st.1`: INTEGER\n-  `Ni_st.2`: INTEGER\n-  `Ni_st.3`: INTEGER\n-  `Ni_st.4`: INTEGER\n-  `Ni_st.5`: INTEGER\n-  `Ni_st.6`\n- `Body`: INTEGER\n- `Bo_st.1`: INTEGER\n-  `Bo_st.2`: INTEGER\n-  `Bo_st.3`: INTEGER\n-  `Bo_st.4`: INTEGER\n-  `Bo_st.5`: INTEGER\n-  `Bo_st.6`\n- `Tires`: INTEGER\n- `Ti_st.1`: INTEGER\n-  `Ti_st.2`: INTEGER\n-  `Ti_st.3`: INTEGER\n-  `Ti_st.4`: INTEGER\n-  `Ti_st.5`: INTEGER\n-  `Ti_st.6`\n- `Transmission`: INTEGER\n- `Tr_st.1`: INTEGER\n-  `Tr_st.2`: INTEGER\n-  `Tr_st.3`: INTEGER\n-  `Tr_st.4`: INTEGER\n-  `Tr_st.5`: INTEGER\n-  `Tr_st.6`\n- `NITRO`: TEXT\n- `FD`: REAL\n- `TIRE`: TEXT\n- `DYNO`: REAL\n- `Purpose`: TEXT\n- `Usage Guide`: TEXT\n- `Creator`: TEXT\n- `Creator ID`: TEXT\n# sqlite_sequence\n- `name`: TEXT\n- `seq`: INTEGER\n---\n## WRs.db\n# records\n- `UniqueID`: TEXT (PRIMARY KEY)\n- `DB Name`: TEXT\n- `Ingame Name Clarification`: TEXT\n- `Un`: TEXT\n- `★`: TEXT\n- `WR-PP`: TEXT\n- `WR-EVO`: TEXT\n- `WR-NITRO`: TEXT\n- `WR-FD`: REAL\n- `WR-TIRE`: TEXT\n- `WR-DYNO`: REAL\n- `WR-BEST ET`: REAL\n- `WR Addon`: TEXT\n- `SHIFT Links`: TEXT\n- `WR-DRIVER`: TEXT\n# s6_effects\n- `UniqueID`: TEXT (PRIMARY KEY)\n- `DB Name`: TEXT\n- `Ingame Name`: TEXT\n- `Un`: TEXT\n- `★`: TEXT\n- `S5 - PP`: TEXT\n- `S5 - EVO`: TEXT\n- `S5 - NOS`: TEXT\n- `S5 - FD`: REAL\n- `S5 - TIRES`: TEXT\n- `S5 - DYNO`: REAL\n- `Engine`: REAL\n- `Turbo`: REAL\n- `Intake`: REAL\n- `NOS`: REAL\n- `Body`: REAL\n- `Tires`: REAL\n- `Trans`: REAL\n- `is EV?`: TEXT\n# info\n- `UniqueID`: TEXT (PRIMARY KEY)\n- `DB Name`: TEXT\n- `Ingame Name Clarification`: TEXT\n- `Un`: TEXT\n- `★`: TEXT\n- `IMG`: TEXT\n- `Vision Info`: TEXT\n- `is EV?`: TEXT\n- `thread`: TEXT\n# updates\n- `ID`: TEXT (PRIMARY KEY)\n- `Date`: TEXT\n- `Output Vision`: TEXT",
            color=discord.Color(0xff00ff)
        )
        embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')

        await interaction.response.send_message(embed=embed)
        await in_app_logging.send_log(self.bot, log, interaction)
        
    async def send_query_in_channel(self, interaction: discord.Interaction, results: list, selections: list, log: str):
        messages, log = self.construct_results(results, selections, log)

        if messages:
            for batch in messages:
                try:
                    await interaction.followup.send(embeds=batch)
                    await asyncio.sleep(0.5)
                except:
                    logger.error("Follow-up interaction expired.")
                    log += f"\nFollow-up interaction expired."
                    await in_app_logging.send_log(self.bot, log, interaction)
                    return
            logger.info(f"Results sent in Channel.")
            log += f"\nResults sent in Channel."
            return log
    
    async def send_query_in_dm(self, interaction: discord.Interaction, results: list, selections: list, log: str):
        try:
            await interaction.followup.send("Sending results via DMs because the amount of results exceeds the maximum allowed results on this server.", ephemeral=True)
            user = interaction.user

            try:
                await user.send("Fetching records, please wait...")

                messages, log = self.construct_results(results, selections, log)

                if messages:
                    for batch in messages:
                        try:
                            await user.send(embeds=batch)
                            await asyncio.sleep(0.5)
                        except:
                            logger.info("DMs are closed or closed for non friended accounts. No records will be send. Please open your DMs and try again.")
                            log += f"\nDMs are closed or closed for non friended accounts. No records will be send. Please open your DMs and try again."
                            return
                    logger.info(f"Results sent in DMs.")
                    log += f"\nResults sent in DMs."

                await asyncio.sleep(0.5)
                try:
                    await interaction.followup.send(f"The results were sent to you via DM.", ephemeral=True)
                except discord.HTTPException as e:
                    if e.status == 429:
                        logger.warning(f"Rate Limited caught (HTTP 429)")
                        retry_after = int(e.response.headers.get('Retry-After', 5))
                        await asyncio.sleep(retry_after)
                        await interaction.followup.send(f"The results were sent to you via DM.", ephemeral=True)
            except discord.Forbidden:
                await interaction.followup.send("Unable to send DMs. Please ensure your DMs are open and try again.", ephemeral=True)
        except discord.errors.NotFound:
            await interaction.response.send_message("The interaction has expired. Please try again.", ephemeral=True)
            return log

    def construct_results(self, results: list, selections: list, log: str):
        logger.info(f"Constructing Embeds")
        log += f"\nConstructing Embeds"
        messages = []
        batch = []
        idx = 1
        for result in results:
            values = result
            desc_lines = [f"- **{selection}**: {value}" for selection, value in zip(selections, values)]
            desc = "\n".join(desc_lines)
            if len(desc) > 4096:
                next_new_line = desc.find("\n", 4000)
                if next_new_line:
                    desc1 = desc[:next_new_line + 1]
                    desc2 = desc[next_new_line + 1:]
                else:
                    next_new_line = desc.find("\n", 3800)
                    desc1 = desc[:next_new_line + 1]
                    desc2 = desc[next_new_line + 1:]
                    if len(desc2) > 1024:
                        next_new_line = desc2.find("\n", 900)
                        if next_new_line:
                            desc2 = desc2[:next_new_line + 1]
                            desc3 = desc2[next_new_line + 1:]
                        else:
                            next_new_line = desc2.find("\n", 800)
                            desc2 = desc2[:next_new_line + 1]
                            desc3 = desc2[next_new_line + 1:]
            else:
                desc1 = desc

            embed = discord.Embed(
                title=f"Your Query Results",
                description=desc1,
                color=discord.Color(0xff00ff)
            )
            try:
                embed.add_field(name="", value=f"{desc2}")
                try:
                    embed.add_field(name="", value=f"{desc3}")
                except:
                    logger.info(f"Description 2 not longer than 1024 characters. skipping add_field...")
                    log += f"\nDescription 2 not longer than 1024 characters. skipping add_field..."
            except:
                logger.info(f"Description not longer than 4096 characters. skipping add_field...")
                log += f"\nDescription not longer than 4096 characters. skipping add_field..."
            embed.set_footer(text=f"row: {idx}")
            embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')

            batch.append(embed)

            # Send batch when it reaches 10 embeds
            if len(batch) == 10:
                messages.append(batch)
                batch = []

        # Add remaining embeds if there are any
        if batch:
            messages.append(batch)
            idx = idx + 1

        logger.info(f"Embeds constructed")
        log += f"\nEmbeds constructed"
        return messages, log

# Setup function to add this cog to the bot
async def setup(bot):
    await bot.add_cog(CustomSQLCog(bot))
