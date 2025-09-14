import discord
from discord.ext import commands
from discord import app_commands
import version_check_manager_apps
import version_check_manager_blog
import in_app_logging
import helpers

logger = helpers.load_logging()

class ScrapeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):

        @app_commands.command(name=self.bot.localisation.get('SCRAPE_CMD_NAME'), description=self.bot.localisation.get('SCRAPE_CMD_DESC'))
        async def scrape(interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True)
            try:
                header = self.bot.localisation.get('SCRAPE_LOG_HEADER')
                logger.info(f"{header}{self.bot.localisation.get('LOG_CMD_TRIGGERED')} /{self.bot.localisation.get('SCRAPE_CMD_NAME')}")
                log = f"{header}{self.bot.localisation.get('LOG_CMD_TRIGGERED')} /{self.bot.localisation.get('SCRAPE_CMD_NAME')}"
                admins = await helpers.load_file('Admin file')
                if str(interaction.user.id) in admins or int(interaction.user.id) in await helpers.load_json_key("config", "ClientAdminIDs"):
                    logger.info(f"{header}{self.bot.localisation.get('CLIENTADMIN_IS_ADMIN')}")
                    log += f"\n{header}{self.bot.localisation.get('CLIENTADMIN_IS_ADMIN')}"
                    logger.info(f"{header}{self.bot.localisation.get('SCRAPE_LOG_START')}")
                    log += f"\n{header}{self.bot.localisation.get('SCRAPE_LOG_START')}"
                    msg = await interaction.followup.send(f"{self.bot.localisation.get('SCRAPE_MSG_START_BLOG')}", ephemeral=True)
                    await version_check_manager_blog.version_check_task(self.bot)
                    await interaction.followup.edit_message(content=f"{self.bot.localisation.get('SCRAPE_MSG_START_APPS')}", message_id=msg.id)
                    await version_check_manager_apps.version_check_task(self.bot)
                    await interaction.followup.edit_message(content=f"{self.bot.localisation.get('SCRAPE_MSG_DONE')}", message_id=msg.id)
                    logger.info(f"{header}{self.bot.localisation.get('SCRAPE_LOG_DONE')}")
                    log += f"\n{header}{self.bot.localisation.get('SCRAPE_LOG_DONE')}"
                else:
                    logger.info(f"{header}{self.bot.localisation.get('CLIENTADMIN_NOT_ADMIN')}")
                    log += f"\n{header}{self.bot.localisation.get('CLIENTADMIN_NOT_ADMIN')}"
                    await interaction.followup.send(f"{self.bot.localisation.get('ADMIN_MSG_NO_PERMISSION')}", ephemeral=True)
                await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
            except Exception as e:
                await interaction.followup.send(f"{self.bot.localisation.get('MSG_ERROR_FETCH')} {e}")
                logger.info(f"{self.bot.localisation.get('LOG_ERROR_FETCH')} {e}")
                log += f"{self.bot.localisation.get('LOG_ERROR_FETCH')} {e}"
                await in_app_logging.send_log(self.bot, log, 0, 1, interaction)

        self.bot.tree.add_command(scrape, guilds=[discord.Object(id=int(server)) for server in await helpers.load_json_key("config", "ClientAdminServers")])

async def setup(bot):
    ADMIN_SERVERS = await helpers.load_json_key("config", "ClientAdminServers")
    for server in ADMIN_SERVERS:
        await bot.add_cog(ScrapeCog(bot), guilds=[discord.Object(id=int(server))], override=True)
