import discord
from discord.ext import commands
from discord import app_commands
import in_app_logging
import helpers

logger = helpers.load_logging()
localisation = dict(helpers.load_localisation())

class RemoveadminCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name=localisation.get('REMOVEADMIN_CMD_NAME'), description=localisation.get('REMOVEADMIN_CMD_DESC'))
    @app_commands.describe(user=localisation.get('REMOVEADMIN_CMD_USER'))
    async def removeadmin(self, interaction: discord.Interaction, user: discord.User):
        await interaction.response.defer(ephemeral=True)
        try:
            header = localisation.get('REMOVEADMIN_LOG_HEADER')
            logger.info(f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('REMOVEADMIN_CMD_NAME')} user: {user}")
            log = f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('REMOVEADMIN_CMD_NAME')} user: {user}"

            admins = await helpers.load_file('Admin file')
            if str(interaction.user.id) in admins or int(interaction.user.id) in await helpers.load_json_key("config", "ClientAdminIDs"):
                if str(user.id) in admins:
                    admins.remove(str(user.id))
                    await helpers.save_file("admins", admins)
                    await interaction.followup.send(f"{user.mention} {localisation.get('REMOVEADMIN_MSG_USER_REMOVED')}", ephemeral=True)
                else:
                    await interaction.followup.send(f"{user.mention} {localisation.get('REMOVEADMIN_MSG_USER_NOT_IN_LIST')}", ephemeral=True)
                logger.info(f"{header}{localisation.get('ADMIN_LOG_IS_ADMIN')}")
                log += f"\n{header}{localisation.get('ADMIN_LOG_IS_ADMIN')}"
            else:
                await interaction.followup.send(f"{localisation.get('ADMIN_MSG_NO_PERMISSION')}", ephemeral=True)
                logger.info(f"{header}{localisation.get('ADMIN_LOG_NOT_ADMIN')}")
                log += f"\n{header}{localisation.get('ADMIN_LOG_NOT_ADMIN')}"
            await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
        except Exception as e:
            await interaction.followup.send(f"{localisation.get('MSG_ERROR_FETCH')} {e}", ephemeral=True)
            logger.info(f"{localisation.get('LOG_ERROR_FETCH')} {e}")
            log += f"{localisation.get('LOG_ERROR_FETCH')} {e}"
            await in_app_logging.send_log(self.bot, log, 0, 1, interaction)

async def setup(bot):
    ADMIN_SERVERS = await helpers.load_json_key("config", "ClientAdminServers")
    for server in ADMIN_SERVERS:
        await bot.add_cog(RemoveadminCog(bot), guilds=[discord.Object(id=int(server))], override=True)
