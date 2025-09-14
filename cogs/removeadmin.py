import discord
from discord.ext import commands
from discord import app_commands
import in_app_logging
import helpers

logger = helpers.load_logging()

class RemoveadminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):

        @app_commands.command(name=self.bot.localisation.get('REMOVEADMIN_CMD_NAME'), description=self.bot.localisation.get('REMOVEADMIN_CMD_DESC'))
        @app_commands.describe(user=self.bot.localisation.get('REMOVEADMIN_CMD_USER'))
        async def removeadmin(interaction: discord.Interaction, user: discord.User):
            await interaction.response.defer(ephemeral=True)
            try:
                header = self.bot.localisation.get('REMOVEADMIN_LOG_HEADER')
                logger.info(f"{header}{self.bot.localisation.get('LOG_CMD_TRIGGERED')} /{self.bot.localisation.get('REMOVEADMIN_CMD_NAME')} user: {user}")
                log = f"{header}{self.bot.localisation.get('LOG_CMD_TRIGGERED')} /{self.bot.localisation.get('REMOVEADMIN_CMD_NAME')} user: {user}"
    
                admins = await helpers.load_file('Admin file')
                if str(interaction.user.id) in admins or int(interaction.user.id) in await helpers.load_json_key("config", "ClientAdminIDs"):
                    if str(user.id) in admins:
                        admins.remove(str(user.id))
                        await helpers.save_file("admins", admins)
                        await interaction.followup.send(f"{user.mention} {self.bot.localisation.get('REMOVEADMIN_MSG_USER_REMOVED')}", ephemeral=True)
                    else:
                        await interaction.followup.send(f"{user.mention} {self.bot.localisation.get('REMOVEADMIN_MSG_USER_NOT_IN_LIST')}", ephemeral=True)
                    logger.info(f"{header}{self.bot.localisation.get('ADMIN_LOG_IS_ADMIN')}")
                    log += f"\n{header}{self.bot.localisation.get('ADMIN_LOG_IS_ADMIN')}"
                else:
                    await interaction.followup.send(f"{self.bot.localisation.get('ADMIN_MSG_NO_PERMISSION')}", ephemeral=True)
                    logger.info(f"{header}{self.bot.localisation.get('ADMIN_LOG_NOT_ADMIN')}")
                    log += f"\n{header}{self.bot.localisation.get('ADMIN_LOG_NOT_ADMIN')}"
                await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
            except Exception as e:
                await interaction.followup.send(f"{self.bot.localisation.get('MSG_ERROR_FETCH')} {e}", ephemeral=True)
                logger.info(f"{self.bot.localisation.get('LOG_ERROR_FETCH')} {e}")
                log += f"{self.bot.localisation.get('LOG_ERROR_FETCH')} {e}"
                await in_app_logging.send_log(self.bot, log, 0, 1, interaction)

        self.bot.tree.add_command(removeadmin, guilds=[discord.Object(id=int(server)) for server in await helpers.load_json_key("config", "ClientAdminServers")])

async def setup(bot):
    ADMIN_SERVERS = await helpers.load_json_key("config", "ClientAdminServers")
    for server in ADMIN_SERVERS:
        await bot.add_cog(RemoveadminCog(bot), guilds=[discord.Object(id=int(server))], override=True)
