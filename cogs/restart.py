import discord
from discord.ext import commands
from discord import app_commands
import in_app_logging
import helpers

logger = helpers.load_logging()

class RestartCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):

        @app_commands.command(name=self.bot.localisation.get('RESTART_CMD_NAME'), description=self.bot.localisation.get('RESTART_CMD_DESC'))
        async def restart(interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True)
            try:
                header = self.bot.localisation.get('RESTART_LOG_HEADER')
                logger.info(f"{header}{self.bot.localisation.get('LOG_CMD_TRIGGERED')} /{self.bot.localisation.get('RESTART_CMD_NAME')}")
                log = f"{header}{self.bot.localisation.get('LOG_CMD_TRIGGERED')} /{self.bot.localisation.get('RESTART_CMD_NAME')}"
                await interaction.followup.send(f"{self.bot.localisation.get('RESTART_MSG_RESTARTING')}", ephemeral=True)
                await helpers.restart()
                await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
            except Exception as e:
                await interaction.followup.send(f"{self.bot.localisation.get('MSG_ERROR_FETCH')} {e}")
                logger.info(f"{self.bot.localisation.get('LOG_ERROR_FETCH')} {e}")
                log += f"{self.bot.localisation.get('LOG_ERROR_FETCH')} {e}"
                await in_app_logging.send_log(self.bot, log, 0, 1, interaction)

        self.bot.tree.add_command(restart, guilds=[discord.Object(id=int(server)) for server in await helpers.load_json_key("config", "ClientAdminServers")])

async def setup(bot):
    ADMIN_SERVERS = await helpers.load_json_key("config", "ClientAdminServers")
    for server in ADMIN_SERVERS:
        await bot.add_cog(RestartCog(bot), guilds=[discord.Object(id=int(server))], override=True)
