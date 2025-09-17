import discord
from discord.ext import commands
from discord import app_commands
import in_app_logging
import helpers
import main

logger = helpers.load_logging()
localisation = dict(helpers.load_localisation())

class StatusCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name=localisation.get('STATUS_CMD_NAME'), description=localisation.get('STATUS_CMD_DESC'))
    @app_commands.describe(status_type=localisation.get('STATUS_CMD_STATUS_TYPE'), status_text=localisation.get('STATUS_CMD_STATUS_TEXT'), url=localisation.get('STATUS_CMD_URL'))
    @app_commands.choices(action=[app_commands.Choice(name=localisation.get('STATUS_CMD_ACTION_OPTION_ADD'), value=1), app_commands.Choice(name=localisation.get('STATUS_CMD_ACTION_OPTION_ACTIVATE'), value=2), app_commands.Choice(name=localisation.get('STATUS_CMD_ACTION_OPTION_REMOVE'), value=3)])
    @app_commands.choices(status_type=[app_commands.Choice(name=localisation.get('STATUS_CMD_STATUS_TYPE_OPTION_PLAYING'), value="playing"), app_commands.Choice(name=localisation.get('STATUS_CMD_STATUS_TYPE_OPTION_WATCHING'), value="watching"), app_commands.Choice(name=localisation.get('STATUS_CMD_STATUS_TYPE_OPTION_STREAMING'), value="streaming"), app_commands.Choice(name=localisation.get('STATUS_CMD_STATUS_TYPE_OPTION_LISTENING'), value="listening"), app_commands.Choice(name=localisation.get('STATUS_CMD_STATUS_TYPE_OPTION_COMPETING'), value="competing")])
    async def status(self, interaction: discord.Interaction, action: int, status_type: str = None, status_text: str = None, url: str = None):
        await interaction.response.defer(ephemeral=True)
        try:
            if interaction.user.id in await helpers.load_json_key("config", "ClientAdminIDs"):
                header = localisation.get('STATUS_LOG_HEADER')
                logger.info(f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('STATUS_CMD_NAME')} status_type: {status_type} status_text: {status_text} url: {url}")
                log = f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('STATUS_CMD_NAME')} status_type: {status_type} status_text: {status_text} url: {url}"
                if action == 1:
                    if main.schedule_dynamic_status_change.is_running():
                        main.schedule_dynamic_status_change.stop()
                    file = await helpers.load_file("status")
                    file["StaticStatusType"] = status_type
                    file["StaticStatusText"] = status_text if status_text else file["StaticStatusText"]
                    file["StaticStatusURL"] = url if url else file["StaticStatusURL"]
                    file["IsStaticStatusActive"] = True
                    await helpers.save_file("status", file)
                    await helpers.change_presence(self.bot, status_type, status_text, url)
                    if status_type == "streaming" and url is None:
                        await interaction.followup.send(f"{localisation.get('STATUS_MSG_WARNING_STREAM_NO_URL')}")
                    await self.send_confirmation(interaction)
                elif action == 2:
                    if main.schedule_dynamic_status_change.is_running():
                        main.schedule_dynamic_status_change.stop()
                    file = await helpers.load_file("status")
                    file["IsStaticStatusActive"] = True
                    await helpers.save_file("status", file)
                    status_type = file["StaticStatusType"]
                    status_text = file["StaticStatusText"]
                    url = file["StaticStatusURL"]
                    await helpers.change_presence(self.bot, status_type, status_text, url)
                    await self.send_confirmation(interaction)
                elif action == 3:
                    file = await helpers.load_file("status")
                    file["IsStaticStatusActive"] = False
                    await helpers.save_file("status", file)
                    if not main.schedule_dynamic_status_change.is_running():
                        main.schedule_dynamic_status_change.start(self.bot)
                    await self.send_confirmation(interaction)
                else:
                    await interaction.followup.send(f"{localisation.get('STATUS_MSG_ERROR_ACTION')}", ephemeral=True)
            else:
                await interaction.followup.send(f"{localisation.get('STATUS_MSG_NOT_OWNER')}", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"{localisation.get('MSG_ERROR_FETCH')} {e}")
            logger.info(f"{localisation.get('LOG_ERROR_FETCH')} {e}")
            log += f"{localisation.get('LOG_ERROR_FETCH')} {e}"
            await in_app_logging.send_log(self.bot, log, 0, 1, interaction)

    async def send_confirmation(self, interaction: discord.Interaction):
        await interaction.followup.send(f"{localisation.get('STATUS_MSG_SUCCESS')}", ephemeral=True)

async def setup(bot):
    ADMIN_SERVERS = await helpers.load_json_key("config", "ClientAdminServers")
    for server in ADMIN_SERVERS:
        await bot.add_cog(StatusCog(bot), guilds=[discord.Object(id=int(server))], override=True)
