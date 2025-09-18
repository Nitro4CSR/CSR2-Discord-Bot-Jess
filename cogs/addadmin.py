import discord
from discord.ext import commands
from discord import app_commands
import os
import in_app_logging
import helpers

logger = helpers.load_logging()
localisation = dict(helpers.load_localisation())

class AddAdminCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name=localisation.get('ADDADMIN_CMD_NAME'), description=localisation.get('ADDADMIN_CMD_DESC'))
    @app_commands.describe(user=localisation.get('ADDADMIN_CMD_USER'), type=localisation.get('ADMIN_CMD_TYPE'))
    @app_commands.choices(type=[app_commands.Choice(name=localisation.get('ADMIN_CMD_TYPE_OPTION_CUSTOM_LISTS'), value="global_list_admins"), app_commands.Choice(name=localisation.get('ADMIN_CMD_TYPE_OPTION_BOT'), value="Admin file")])
    async def addadmin(self, interaction: discord.Interaction, user: discord.User, type: str = None):
        await interaction.response.defer(ephemeral=True)
        try:
            header = localisation.get('ADDADMIN_LOG_HEADER')
            logger.info(f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('LISTADMIN_CMD_NAME')} user: {user} type: {type}")
            log = f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('LISTADMIN_CMD_NAME')} user: {user} type: {type}"
            if not type:
                type = "Admin file"
            admins = list(await helpers.load_file(type)) if os.path.exists(await helpers.load_file_path('global_list_admins')) else []
            if str(interaction.user.id) in admins or int(interaction.user.id) in await helpers.load_json_key("config", "ClientAdminIDs"):
                if str(user.id) not in admins:
                    admins.append(str(user.id))
                await helpers.save_file(type, admins)
                await interaction.followup.send(f"{user.mention} {localisation.get('ADDADMIN_MSG_USER_ADDED')}", ephemeral=True)
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
        await bot.add_cog(AddAdminCog(bot), guilds=[discord.Object(id=int(server))], override=True)
