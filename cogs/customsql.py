import asyncio
import discord
from discord.ext import commands
from discord import app_commands
import os
import in_app_logging
import helpers

logger = helpers.load_logging()

class CustomSQLCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):

        @app_commands.command(name=self.bot.localisation.get('CUSTOMSQL_CMD_NAME'), description=self.bot.localisation.get('CUSTOMSQL_CMD_DESC'))
        @app_commands.describe(database=self.bot.localisation.get('CUSTOMSQL_CMD_DATABASE'), select=self.bot.localisation.get('CUSTOMSQL_CMD_SELECT'), update=self.bot.localisation.get('CUSTOMSQL_CMD_UPDATE'), create_table=self.bot.localisation.get('CUSTOMSQL_CMD_CREATE_TABLE'), insert_into=self.bot.localisation.get('CUSTOMSQL_CMD_INSERT_INTO'), from_=self.bot.localisation.get('CUSTOMSQL_CMD_FROM'), set_=self.bot.localisation.get('CUSTOMSQL_CMD_SET'), where=self.bot.localisation.get('CUSTOMSQL_CMD_WHERE'))
        @app_commands.choices(database=[app_commands.Choice(name="WRs", value="WRs"), app_commands.Choice(name="tunes", value="tunes")])
        @app_commands.choices(from_=[app_commands.Choice(name="records", value="records"), app_commands.Choice(name="s6_effects", value="s6_effects"), app_commands.Choice(name="info", value="info"), app_commands.Choice(name="updates", value="updates"), app_commands.Choice(name="community_tunes", value="community_tunes")])
        async def customsql(interaction: discord.Interaction, database: app_commands.Choice[str], select: str = None, update: str = None, create_table: str = None, insert_into: str = None, from_: app_commands.Choice[str] = None, set_: str = None, where: str = None):
            await interaction.response.defer(ephemeral=True)
            try:
                header = self.bot.localisation.get('CUSTOMSQL_LOG_HEADER')
                logger.info(f"{header}{self.bot.localisation.get('LOG_CMD_TRIGGERED')} /{self.bot.localisation.get('CLIENTINFO_CMD_NAME')} database: {database} select: {select} update: {update} create_table: {create_table} insert_into: {insert_into} from_: {from_} set_: {set_} where: {where}")
                log = f"{header}{self.bot.localisation.get('LOG_CMD_TRIGGERED')} /{self.bot.localisation.get('CLIENTINFO_CMD_NAME')} database: {database} select: {select} update: {update} create_table: {create_table} insert_into: {insert_into} from_: {from_} set_: {set_} where: {where}"
    
                if any([update, create_table, insert_into, set_]):
                    logger.info(f"{header}{self.bot.localisation.get('CUSTOMSQL_LOG_PRIVELEGED_QUERY')}")
                    log += f"\n{header}{self.bot.localisation.get('CUSTOMSQL_LOG_PRIVELEGED_QUERY')}"
                    admins = await helpers.load_file('Admin file')
                    if str(interaction.user.id) not in admins or int(interaction.user.id) not in await helpers.load_json_key("config", "ClientAdminIDs"):
                        logger.info(f"{header}{self.bot.localisation.get('ADMIN_LOG_NOT_ADMIN')}")
                        log += f"\n{header}{self.bot.localisation.get('ADMIN_LOG_NOT_ADMIN')}"
                        await interaction.response.send_message(f"{self.bot.localisation.get('ADMIN_MSG_NO_PERMISSION')}", ephemeral=True)
                        await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
                        return
                    logger.info(f"{header}{self.bot.localisation.get('ADMIN_LOG_IS_ADMIN')}")
                    log += f"\n{header}{self.bot.localisation.get('ADMIN_LOG_IS_ADMIN')}"
                    
                sql_parts = []
                if select == "*":
                    table_columns = {
                        "records": """"UniqueID", "DB Name", "Ingame Name Clarification", "Un", "★", "WR-PP", "WR-EVO", "WR-NITRO", "WR-FD", "WR-TIRE", "WR-DYNO", "WR-BEST ET", "WR Addon", "SHIFT Links", "WR-DRIVER" """,
                        "s6_effects": """"UniqueID", "DB Name", "Ingame Name", "Un", "★", "S5 - PP", "S5 - EVO", "S5 - NOS", "S5 - FD", "S5 - TIRES", "S5 - DYNO", "Engine", "Turbo", "Intake", "NOS", "Body", "Tires", "Trans", "is EV?" """,
                        "info": """"UniqueID", "DB Name", "Ingame Name Clarification", "Un", "★", "IMG", "Vision Info", "is EV?", "thread" """,
                        "updates": """"ID", "Date", "Output Vision" """,
                        "community_tunes": """"TuneID", "DB Name", "Ingame Name Clarification", "Un", "★", "PP" INTEGER, "EVO" INTEGER, "Engine/Motor" Integer, "En_st.1", "En_st.2", "En_st.3", "En_st.4", "En_st.5", "En_st.6", "Turbo/Battery" Integer, "Tu_st.1", "Tu_st.2", "Tu_st.3", "Tu_st.4", "Tu_st.5", "Tu_st.6", "Intake/Inverter" Integer, "In_st.1", "In_st.2", "In_st.3", "In_st.4", "In_st.5", "In_st.6", "Nitrous/Overboost" Integer, "Ni_st.1", "Ni_st.2", "Ni_st.3", "Ni_st.4", "Ni_st.5", "Ni_st.6", "Body" Integer, "Bo_st.1", "Bo_st.2", "Bo_st.3", "Bo_st.4", "Bo_st.5", "Bo_st.6", "Tires" Integer, "Ti_st.1", "Ti_st.2", "Ti_st.3", "Ti_st.4", "Ti_st.5", "Ti_st.6", "Transmission" Integer, "Tr_st.1", "Tr_st.2", "Tr_st.3", "Tr_st.4", "Tr_st.5", "Tr_st.6", "NITRO", "FD", "TIRE", "DYNO", "Purpose", "Usage Guide", "Creator", "Creator ID" """
                    }
                    select = table_columns[from_.value]
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
    
                
                while not os.path.exists(await helpers.load_file_path(database.value)):
                    await asyncio.sleep(0.5)
                results = await helpers.execute_sql_statement(database.value, sql_statement)
                if results:
                    logger.info(f"{header}{len(results)} {self.bot.localisation.get('LOG_RESULTS_FOUND')}")
                    log += f"\n{header}{len(results)} {self.bot.localisation.get('LOG_RESULTS_FOUND')}"
                    route = await helpers.get_send_route(len(results), interaction.user.id, interaction.guild.id if interaction.guild else None)
                    if route == 2:
                        await interaction.followup.send(f"{self.bot.localisation.get('MSG_WARNING_OVER_LIMITS')}" if interaction.guild else f"{self.bot.localisation.get('MSG_WARNING_OVER_LIMIT')}")
                    else:
                        messages, log = await self.create_embeds(results, select.split(","), log)
                    log = await self.send_channel(interaction, messages, log) if route == 0 else await self.send_dms(interaction, messages, log)
                else:
                    await interaction.response.send_message(f"{self.bot.localisation.get('CUSTOMSQL_MSG_DONE_EXECUTION_NO_RESULTS')}", ephemeral=True)
                await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
            except Exception as e:
                await interaction.followup.send(f"{self.bot.localisation.get('MSG_ERROR_FETCH')} {e}")
                logger.info(f"{self.bot.localisation.get('LOG_ERROR_FETCH')} {e}")
                log += f"{self.bot.localisation.get('LOG_ERROR_FETCH')} {e}"
                await in_app_logging.send_log(self.bot, log, 0, 1, interaction)

        self.bot.tree.add_command(customsql)
            
    async def create_embeds(self, results: list, selections: list, log: str):
        header = self.bot.localisation.get('CUSTOMSQL_LOG_HEADER')
        logger.info(f"{header}{self.bot.localisation.get('LOG_BUILD_EMBEDS')}")
        log += f"\n{header}{self.bot.localisation.get('LOG_BUILD_EMBEDS')}"
        messages = []
        batch = []
        idx = 1
        for result in results:
            desc_lines = [f"- **{selection}**: {value}" for selection, value in zip(selections, result)]
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
                title=f"{self.bot.localisation.get('CUSTOMSQL_MSG_EMBED_TITLE')}",
                description=desc1,
                color=discord.Color(0xff00ff)
            )
            try:
                embed.add_field(name="", value=f"{desc2}")
                try:
                    embed.add_field(name="", value=f"{desc3}")
                except:
                    logger.info(f"{header}{self.bot.localisation.get('CUSTOMSQL_LOG_SPLIT_EMBED_NOT_NEEDED_2')}")
                    log += f"\n{header}{self.bot.localisation.get('CUSTOMSQL_LOG_SPLIT_EMBED_NOT_NEEDED_2')}"
            except:
                logger.info(f"{header}{self.bot.localisation.get('CUSTOMSQL_LOG_SPLIT_EMBED_NOT_NEEDED_1')}")
                log += f"\n{header}{self.bot.localisation.get('CUSTOMSQL_LOG_SPLIT_EMBED_NOT_NEEDED_1')}"
            embed.set_footer(text=f"{self.bot.localisation.get('CUSTOMSQL_MSG_EMBED_DESC_FOOTER')} {idx} / {len(results)}")
            embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')
            batch.append(embed)
            idx = idx + 1
            if len(batch) == 10:
                messages.append(batch)
                batch = []
        if batch:
            messages.append(batch)
            batch = []
    
        logger.info(f"{header}{self.bot.localisation.get('LOG_EMBEDS_BUILD')}")
        log += f"\n{header}{self.bot.localisation.get('LOG_EMBEDS_BUILD')}"
        return messages, log
    
    async def send_channel(self, interaction: discord.Interaction, messages: list, log: str):
        header = self.bot.localisation.get('CUSTOMSQL_LOG_HEADER')
        await interaction.followup.send(f"{self.bot.localisation.get('MSG_NOTICE_FETCH')}")
        for message in messages:
            await interaction.followup.send(embeds=message)
            await asyncio.sleep(0.5)
        logger.info(f"{header}{self.bot.localisation.get('LOG_DONE_CHANNEL')}")
        log += f"\n{header}{self.bot.localisation.get('LOG_DONE_CHANNEL')}"
        return log
    
    async def send_dms(self, interaction: discord.Interaction, messages: list, log: str):
        header = self.bot.localisation.get('CUSTOMSQL_LOG_HEADER')
        if interaction.guild:
            await interaction.followup.send(f"{self.bot.localisation.get('MSG_NOTICE_OVER_SERVER_LIMIT')}")
        try:
            await interaction.user.send(f"{self.bot.localisation.get('MSG_NOTICE_FETCH')}") if interaction.guild else await interaction.followup.send(f"{self.bot.localisation.get('MSG_NOTICE_FETCH')}")
        except discord.Forbidden:
            await interaction.followup.send(f"{self.bot.localisation.get('MSG_WARNING_DMS_CLOSED')}", ephemeral=True)
            logger.info(f"{header}{self.bot.localisation.get('LOG_ERROR_CLOSED')}")
            log += f"\n{header}{self.bot.localisation.get('LOG_ERROR_CLOSED')}"
            return log
        for message in messages:
            await interaction.user.send(embeds=message)
            await asyncio.sleep(0.5)
        logger.info(f"{header}{self.bot.localisation.get('LOG_DONE_DM')}")
        log += f"\n{header}{self.bot.localisation.get('LOG_DONE_DM')}"
        if interaction.guild:
            await interaction.followup.send(f"{self.bot.localisation.get('MSG_NOTICE_SENT_DMS')}", ephemeral=True)
        return log

async def setup(bot):
    await bot.add_cog(CustomSQLCog(bot))
