import discord
from discord.ext import commands
from discord import app_commands
import in_app_logging
import helpers

logger = helpers.load_logging()
localisation = dict(helpers.load_localisation())

class NotifyUpdatesCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name=localisation.get('NOTIFY_UPDATES_ADD_CMD_NAME'), description=localisation.get('NOTIFY_UPDATES_ADD_CMD_DESC'))
    @app_commands.choices(scope=helpers.load_command_options_scope(localisation))
    @app_commands.describe(scope=localisation.get('ANY_CMD_SCOPE'))
    async def notifyupdates_add(self, interaction: discord.Interaction, scope: str = None):
        await interaction.response.defer(ephemeral=True)
        try:
            header = localisation.get('NOTIFY_UPDATES_ADD_LOG_HEADER')
            logger.info(f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('NOTIFY_UPDATES_ADD_CMD_NAME')} scope: {scope}")
            log = f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('NOTIFY_UPDATES_ADD_CMD_NAME')} scope: {scope}"
            scope = await self.str_to_list(scope)
            embed = discord.Embed(title=f"{localisation.get('ANNOUNCE_UPDATES_ADD_MSG_EMBED_TITLE')}", description=f"{localisation.get('ANNOUNCE_UPDATES_ADD_MSG_EMBED_DESC')} {scope}", color=discord.Color(0xff00ff))
            embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')
            try:
                message = await interaction.user.send(embed=embed, silent=True)
                for scope in scope:
                    await self.process_request(interaction.user.id, scope, 1, log)
                    status = 2
                await interaction.followup.send(f"{interaction.user.mention} {localisation.get('ANNOUNCE_UPDATES_ADD_LOG_DONE')}", ephemeral=True)
                logger.info(f"{header}{localisation.get('NOTIFY_UPDATES_ADD_LOG_DONE')} {interaction.user.display_name}")
                log += f"\n{header}{localisation.get('NOTIFY_UPDATES_ADD_LOG_DONE')} {interaction.user.display_name}"
                await message.delete()
            except:
                await interaction.followup.send(f"{localisation.get('NOTIFY_UPDATES_ADD_LOG_FAIL')} {interaction.user.mention}", ephemeral=True)
                logger.error(f"{header}{localisation.get('NOTIFY_UPDATES_ADD_LOG_FAIL')} {interaction.user.display_name}")
                log += f"\n{header}{localisation.get('NOTIFY_UPDATES_ADD_LOG_FAIL')} {interaction.user.display_name}"
            await in_app_logging.send_log(self.bot, log, status, 1, interaction)
        except Exception as e:
            await interaction.followup.send(f"{localisation.get('MSG_ERROR_FETCH')} {e}", ephemeral=True)
            logger.info(f"{localisation.get('LOG_ERROR_FETCH')} {e}")
            log += f"{localisation.get('LOG_ERROR_FETCH')} {e}"
            await in_app_logging.send_log(self.bot, log, 0, 1, interaction)

    @app_commands.command(name="csr2_notify_updates_delete", description="Allow Jess to notify you about updates in DMs")
    @app_commands.choices(scope=helpers.load_command_options_scope(localisation))
    @app_commands.describe(scope=localisation.get('ANY_CMD_SCOPE'))
    async def notifyupdates_delete(self, interaction: discord.Interaction, scope: str = None):
        await interaction.response.defer(ephemeral=True)
        try:
            header = localisation.get('NOTIFY_UPDATES_DELETE_LOG_HEADER')
            logger.info(f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('NOTIFY_UPDATES_DELETE_CMD_NAME')} scope: {scope}")
            log = f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('NOTIFY_UPDATES_DELETE_CMD_NAME')} scope: {scope}"
            scope = await self.str_to_list(scope)
            try:
                for scope in scope:
                    await self.process_request(interaction.user.id, scope, 0, log)
                    status = 2
                await interaction.followup.send(f"{interaction.user.mention} {localisation.get('ANNOUNCE_UPDATES_REMOVE_LOG_DONE')}", ephemeral=True)
                logger.info(f"{header}{localisation.get('NOTIFY_UPDATES_DELETE_LOG_DONE')} {interaction.user.display_name}")
                log += f"\n{header}{localisation.get('NOTIFY_UPDATES_DELETE_LOG_DONE')} {interaction.user.display_name}"
            except:
                await interaction.followup.send(f"{localisation.get('NOTIFY_UPDATES_DELETE_LOG_FAIL')} {interaction.user.mention}", ephemeral=True)
                logger.error(f"{header}{localisation.get('NOTIFY_UPDATES_DELETE_LOG_FAIL')} {interaction.user.display_name}")
                log += f"\n{header}{localisation.get('NOTIFY_UPDATES_DELETE_LOG_FAIL')} {interaction.user.display_name}"
                status = 0
            await in_app_logging.send_log(self.bot, log, status, 1, interaction)
        except Exception as e:
            await interaction.followup.send(f"{localisation.get('MSG_ERROR_FETCH')} {e}", ephemeral=True)
            logger.info(f"{localisation.get('LOG_ERROR_FETCH')} {e}")
            log += f"{localisation.get('LOG_ERROR_FETCH')} {e}"
            await in_app_logging.send_log(self.bot, log, 0, 1, interaction)

    async def str_to_list(self, scope):
        scope_list = []
        if not scope or scope == "CSR2" or scope == "All":
            scope_list.append("CSR2")
        if not scope or scope == "CSR3" or scope == "All":
            scope_list.append("CSR3")
        if not scope or scope == "Blog" or scope == "All":
            scope_list.append("Blog")
        return scope_list

    async def process_request(self, id: str, scope: str, request: int, log: str):
        list = await helpers.load_file(f"{scope} announcement user file")
        if (str(id) in list and request == 0) or (str(id) not in list and request == 1):
            list.remove(str(id)) if request == 0 else list.append(str(id))
            await helpers.save_file(f"{scope}_announcement_users", list)

async def setup(bot):
    await bot.add_cog(NotifyUpdatesCog(bot))
