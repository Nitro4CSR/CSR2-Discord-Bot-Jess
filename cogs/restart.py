import discord
from discord.ext import commands
from discord import app_commands
import in_app_logging
import helpers

logger = helpers.load_logging()
localisation = dict(helpers.load_localisation())

class RestartCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name=localisation.get('RESTART_CMD_NAME'), description=localisation.get('RESTART_CMD_DESC'))
    async def restart(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            header = localisation.get('RESTART_LOG_HEADER')
            logger.info(f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('RESTART_CMD_NAME')}")
            log = f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('RESTART_CMD_NAME')}"
            await interaction.followup.send(f"{localisation.get('RESTART_MSG_RESTARTING')}", ephemeral=True)
            await helpers.restart()
            await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
        except Exception as e:
            await interaction.followup.send(f"{localisation.get('MSG_ERROR_FETCH')} {e}")
            logger.info(f"{localisation.get('LOG_ERROR_FETCH')} {e}")
            log += f"{localisation.get('LOG_ERROR_FETCH')} {e}"
            await in_app_logging.send_log(self.bot, log, 0, 1, interaction)

async def setup(bot):
    ADMIN_SERVERS = await helpers.load_json_key("config", "ClientAdminServers")
    for server in ADMIN_SERVERS:
        await bot.add_cog(RestartCog(bot), guilds=[discord.Object(id=int(server))], override=True)
