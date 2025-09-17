import discord
from discord.ext import commands
from discord import app_commands
import database_manager
import in_app_logging
import helpers

logger = helpers.load_logging()
localisation = dict(helpers.load_localisation())

class DatabaseUpdateCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name=localisation.get('UPDATEDB_CMD_NAME'), description=localisation.get('UPDATEDB_CMD_DESC'))
    async def updatedb(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            header = localisation.get('UPDATEDB_LOG_HEADER')
            logger.info(f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('UPDATEDB_CMD_NAME')}")
            log = f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('UPDATEDB_CMD_NAME')}"

            admins = await helpers.load_file('Admin file')
            if str(interaction.user.id) in admins or str(interaction.user.id) in await helpers.load_json_key("config", "ClientAdminIDs"):
                logger.info(f"{header}{localisation.get('ADMIN_LOG_IS_ADMIN')}")
                log += f"\n{header}{localisation.get('ADMIN_LOG_IS_ADMIN')}"
                logger.info(f"{header}{localisation.get('UPDATEDB_LOG_DB_UPDATE')}")
                log += f"\n{header}{localisation.get('UPDATEDB_LOG_DB_UPDATE')}"
                await database_manager.recreate_database(self.bot)
                logger.info(f"{header}{localisation.get('UPDATEDB_LOG_DONE')}")
                log += f"\n{header}{localisation.get('UPDATEDB_LOG_DONE')}"
                await interaction.followup.send(f"{localisation.get('UPDATEDB_MSG_UPDATE_DONE')}", ephemeral=True)
            else:
                logger.info(f"{header}{localisation.get('ADMIN_LOG_NOT_ADMIN')}")
                log += f"\n{header}{localisation.get('ADMIN_LOG_NOT_ADMIN')}"
                await interaction.followup.send(f"{localisation.get('ADMIN_MSG_NO_PERMISSION')}", ephemeral=True)
            await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
        except Exception as e:
            await interaction.followup.send(f"{localisation.get('MSG_ERROR_FETCH')} {e}")
            logger.info(f"{localisation.get('LOG_ERROR_FETCH')} {e}")
            log += f"{localisation.get('LOG_ERROR_FETCH')} {e}"
            await in_app_logging.send_log(self.bot, log, 0, 1, interaction)

async def setup(bot):
    ADMIN_SERVERS = await helpers.load_json_key("config", "ClientAdminServers")
    for server in ADMIN_SERVERS:
        await bot.add_cog(DatabaseUpdateCog(bot), guilds=[discord.Object(id=int(server))], override=True)
