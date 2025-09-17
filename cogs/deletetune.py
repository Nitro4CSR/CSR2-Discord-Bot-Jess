import discord
from discord.ext import commands
from discord import app_commands
import in_app_logging
import tunes_manager
import helpers

logger = helpers.load_logging()
localisation = dict(helpers.load_localisation())

class DeleteTuneCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name=localisation.get('DELETE_TUNE_CMD_NAME'), description=localisation.get('DELETE_TUNE_CMD_DESC'))
    @discord.app_commands.describe(tune_id=localisation.get('DELETE_TUNE_CMD_TUNE_ID'))
    async def deletetune(self, interaction: discord.Interaction, tune_id: int):
        await interaction.response.defer()
        try:
            header = await helpers.localisation.get('DELETE_TUNE_LOG_HEADER')
            logger.info(f"{header}{await helpers.localisation.get('LOG_CMD_TRIGGERED')} /{await helpers.localisation.get('DELETE_TUNE_CMD_NAME')} tune_id: {tune_id}")
            log = f"{header}{await helpers.localisation.get('LOG_CMD_TRIGGERED')} /{await helpers.localisation.get('DELETE_TUNE_CMD_NAME')} tune_id: {tune_id}"
            user = str(f"{interaction.user.id}")
            owner = await tunes_manager.get_creator_by_tune_id(tune_id)

            if (owner is not None and owner[0] is None):
                await interaction.followup.send(f"{await helpers.localisation.get('DELETE_TUNE_MSG_ERROR_TUNE_ID')}")
            elif ((owner is not None and user == owner[0][0]) or int(user) in await helpers.load_json_key("config", "ClientAdminIDs")):
                await tunes_manager.remove_entry(tune_id)
                result = await tunes_manager.search_tune_id(tune_id)
                if result:
                    await interaction.followup.send(f"{await helpers.localisation.get('DELETE_TUNE_MSG_ERROR_DELETE')}")
                    logger.warning(f"{header}{await helpers.localisation.get('UPDATE_TUNE_LOG_FAIL')}")
                    log += f"\n{header}{await helpers.localisation.get('UPDATE_TUNE_LOG_FAIL')}"
                    status = 0
                else:
                    await interaction.followup.send(F"{await helpers.localisation.get('DELETE_TUNE_MSG_DONE')}")
                    logger.info(f"{header}{await helpers.localisation.get('DELETE_TUNE_LOG_DONE')}")
                    log += f"\n{header}{await helpers.localisation.get('DELETE_TUNE_LOG_DONE')}"
                    status = 2
            else:
                await interaction.followup.send(F"{await helpers.localisation.get('DELETE_TUNE_MSG_ERROR_OWNER')}")
                logger(f"{header}{await helpers.localisation.get('LOG_ERROR_NOT_OWNER')}")
                log += f"\n{header}{await helpers.localisation.get('LOG_ERROR_NOT_OWNER')}"
                status = 2
            await in_app_logging.send_log(self.bot, log, status, 1, interaction)
        except Exception as e:
            await interaction.followup.send(f"{await helpers.localisation.get('MSG_ERROR_FETCH')} {e}")
            logger.info(f"{await helpers.localisation.get('LOG_ERROR_FETCH')} {e}")
            log += f"{await helpers.localisation.get('LOG_ERROR_FETCH')} {e}"
            await in_app_logging.send_log(self.bot, log, 0, 1, interaction)

async def setup(bot):
    await bot.add_cog(DeleteTuneCog(bot))
