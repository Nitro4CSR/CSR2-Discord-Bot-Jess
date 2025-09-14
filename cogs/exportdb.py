import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
import in_app_logging
import helpers

logger = helpers.load_logging()

class ExportDBCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):

        @app_commands.command(name=self.bot.localisation.get('EXPORTDB_CMD_NAME'), description=self.bot.localisation.get('EXPORTDB_CMD_DESC'))
        async def exportdb(interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True)
            try:
                header = await helpers.self.bot.localisation.get('EXPORTDB_LOG_HEADER')
                logger.info(f"{header}{await helpers.self.bot.localisation.get('LOG_CMD_TRIGGERED')} /{await helpers.self.bot.localisation.get('EXPORTDB_CMD_NAME')}")
                log = f"{header}{await helpers.self.bot.localisation.get('LOG_CMD_TRIGGERED')} /{await helpers.self.bot.localisation.get('EXPORTDB_CMD_NAME')}"
                admins = await helpers.load_file('Admin file')
                if str(interaction.user.id) not in admins and int(interaction.user.id) not in await helpers.load_json_key("config", "ClientAdminIDs"):
                    await interaction.followup.send(f"{await helpers.self.bot.localisation.get('ADMIN_MSG_NO_PERMISSION')}", ephemeral=True)
                    await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
                    return
                while not os.path.exists(await helpers.load_file_path('EDB')):
                    asyncio.sleep(0.2)
                while not os.path.exists(await helpers.load_file_path('tunes')):
                    asyncio.sleep(0.2)
                await interaction.user.send(files=[discord.File(await helpers.load_file_path('EDB'), filename="CSR2_Data_SQLite3.db"), discord.File(await helpers.load_file_path('EDB'), filename="Community_Data_SQLite3.db")])
                await interaction.followup.send(f"{await helpers.self.bot.localisation.get('EXPORTDB_MSG_SENT_DMS')}", ephemeral=True)
            except discord.Forbidden:
                await interaction.followup.send(f"{await helpers.self.bot.localisation.get('MSG_WARNING_DMS_CLOSED')}", ephemeral=True)
                await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
            except Exception as e:
                await interaction.followup.send(f"{await helpers.self.bot.localisation.get('MSG_ERROR_FETCH')} {e}")
                logger.info(f"{await helpers.self.bot.localisation.get('LOG_ERROR_FETCH')} {e}")
                log += f"{await helpers.self.bot.localisation.get('LOG_ERROR_FETCH')} {e}"
                await in_app_logging.send_log(self.bot, log, 0, 1, interaction)

        self.bot.tree.add_command(exportdb, guilds=[discord.Object(id=int(server)) for server in await helpers.load_json_key("config", "ClientAdminServers")])

async def setup(bot):
    ADMIN_SERVERS = await helpers.load_json_key("config", "ClientAdminServers")
    for server in ADMIN_SERVERS:
        await bot.add_cog(ExportDBCog(bot), guilds=[discord.Object(id=int(server))], override=True)
