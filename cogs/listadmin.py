import discord
from discord.ext import commands
from discord import app_commands
import in_app_logging
import helpers

logger = helpers.load_logging()
localisation = dict(helpers.load_localisation())

class ListadminCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name=localisation.get('LISTADMIN_CMD_NAME'), description=localisation.get('LISTADMIN_CMD_DESC'))
    @app_commands.describe(type=localisation.get('ADMIN_CMD_TYPE'))
    @app_commands.choices(type=[app_commands.Choice(name=localisation.get('ADMIN_CMD_TYPE_OPTION_CUSTOM_LISTS'), value="global_list_admins"), app_commands.Choice(name=localisation.get('ADMIN_CMD_TYPE_OPTION_BOT'), value="Admin file")])
    async def listadmins(self, interaction: discord.Interaction, type: str = None):
        await interaction.response.defer(ephemeral=True)
        try:
            header = localisation.get('LISTADMIN_LOG_HEADER')
            logger.info(f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('LISTADMIN_CMD_NAME')}")
            log = f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('LISTADMIN_CMD_NAME')}"
            if not type:
                type = "Admin file"
            admins = await helpers.load_file(type)
            if str(interaction.user.id) in admins or int(interaction.user.id) in await helpers.load_json_key("config", "ClientAdminIDs"):
                admin_list = ", ".join([f"<@{admin_id}>" for admin_id in admins])
                await interaction.followup.send(f"{localisation.get('LISTADMIN_MSG_ADMINS')} {admin_list}", ephemeral=True)
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
        await bot.add_cog(ListadminCog(bot), guilds=[discord.Object(id=int(server))], override=True)
