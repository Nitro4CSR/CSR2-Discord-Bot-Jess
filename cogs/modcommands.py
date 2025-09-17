import discord
from discord.ext import commands
from discord import app_commands
import in_app_logging
import helpers

logger = helpers.load_logging()
localisation = dict(helpers.load_localisation())

class ModcommandsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name=localisation.get('MODCOMMANDS_CMD_NAME'), description=localisation.get('MODCOMMANDS_CMD_DESC'))
    @app_commands.describe(command=localisation.get('ANY_CMD_COMMAND'))
    @app_commands.choices(command=[app_commands.Choice(name='csr2_limitresults', value='limitresults'), app_commands.Choice(name='csr2_announce_updates_add', value='announce_updates_add'), app_commands.Choice(name='csr2_announce_updates_delete', value='announce_updates_delete')])
    async def modcommands(self, interaction: discord.Interaction, command: str = None):
        await interaction.response.defer()
        try:
            header = localisation.get('MODCOMMANDS_LOG_HEADER')
            logger.info(f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('MODCOMMANDS_CMD_NAME')} commad: {command}")
            log = f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('MODCOMMANDS_CMD_NAME')} commad: {command}"

            if not interaction.guild or not interaction.user.guild_permissions.administrator and str(interaction.user.id) not in await helpers.load_json_key("config", "ClientAdminIDs"):
                await interaction.followup.send(f"{localisation.get('MODCOMMANDS_MSG_WARNING_NO_PERMISSION_SERVER')}", ephemeral=True)
                await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
                return
            command = "default" if command is None else command
            title_text = f"{localisation.get('COMMANDS_MSG_EMBED_TITLE_AVAILABLE_COMMANDS')}" if command == "default" else f"{localisation.get('COMMANDS_MSG_EMBED_TITLE_COMMAND_USAGE')}"
            descriptions = {
                """default""": f"""</{localisation.get('LIMITRESULTS_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("LIMITRESULTS_CMD_NAME")}_CMD'.upper())}>\n</{localisation.get('ANNOUNCE_UPDATES_ADD_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("ANNOUNCE_UPDATES_ADD_CMD_NAME")}_CMD'.upper())}>\n</{localisation.get('ANNOUNCE_UPDATES_DELETE_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("ANNOUNCE_UPDATES_DELETE_CMD_NAME")}_CMD'.upper())}>\n""",
                """limitresults""": f"""## </{localisation.get('LIMITRESULTS_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("LIMITRESULTS_CMD_NAME")}_CMD'.upper())}>\n{localisation.get("LIMITRESULTS_CMD_DESC")}\n{localisation.get('COMMANDS_MSG_EMBED_DESC_ADDITIONAL_OPERATORS')}\n- limit: {localisation.get('LIMITRESULTS_CMD_LIMIT')}\n- scope: {localisation.get('GETLIMIT_CMD_SCOPE')} {localisation.get('COMMANDS_MSG_OPTIONAL')}\n  - {localisation.get('COMMANDS_MSG_EMBED_DESC_OPTIONS')}\n    - {localisation.get('LIMIT_CMD_SCOPE_OPTION_SERVER')}\n    - {localisation.get('LIMIT_CMD_SCOPE_OPTION_PERSONAL')}\n""",
                """announceupdates_add""": f"""## </{localisation.get('ANNOUNCE_UPDATES_ADD_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("ANNOUNCE_UPDATES_ADD_CMD_NAME")}_CMD'.upper())}>\n{localisation.get("NOTIFY_UPDATES_ADD_CMD_DESC")}\n{localisation.get('COMMANDS_MSG_EMBED_DESC_ADDITIONAL_OPERATORS')}\n- channel: {localisation.get('ANNOUNCE_UPDATES_CMD_CHANNEL')}\n- scope: {localisation.get('ANY_CMD_SCOPE')} {localisation.get('COMMANDS_MSG_OPTIONAL')}\n  - {localisation.get('COMMANDS_MSG_EMBED_DESC_OPTIONS')}\n    - {localisation.get('ANY_CMD_SCOPE_OPTION_ALL')}\n    - {localisation.get('ANY_CMD_SCOPE_OPTION_CSR2')}\n    - {localisation.get('ANY_CMD_SCOPE_OPTION_CSR3')}\n    - {localisation.get('ANY_CMD_SCOPE_OPTION_BLOG')}\n""",
                """announceupdates_delete""": f"""## </{localisation.get('ANNOUNCE_UPDATES_DELETE_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("ANNOUNCE_UPDATES_DELETE_CMD_NAME")}_CMD'.upper())}>\n{localisation.get("NOTIFY_UPDATES_DELETE_CMD_DESC")}\n{localisation.get('COMMANDS_MSG_EMBED_DESC_ADDITIONAL_OPERATORS')}\n- channel: {localisation.get('ANNOUNCE_UPDATES_CMD_CHANNEL')}\n- scope: {localisation.get('ANY_CMD_SCOPE')} {localisation.get('COMMANDS_MSG_OPTIONAL')}\n  - {localisation.get('COMMANDS_MSG_EMBED_DESC_OPTIONS')}\n    - {localisation.get('ANY_CMD_SCOPE_OPTION_ALL')}\n    - {localisation.get('ANY_CMD_SCOPE_OPTION_CSR2')}\n    - {localisation.get('ANY_CMD_SCOPE_OPTION_CSR3')}\n    - {localisation.get('ANY_CMD_SCOPE_OPTION_BLOG')}\n""",
            }
            description_text = descriptions[command]
            embed = discord.Embed(
                title=title_text,
                description=description_text,
                color=discord.Color(0xff00ff)
            )
            embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')

            await interaction.followup.send(embed=embed)
            await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
        except Exception as e:
            await interaction.followup.send(f"{localisation.get('MSG_ERROR_FETCH')} {e}")
            logger.info(f"{localisation.get('LOG_ERROR_FETCH')} {e}")
            log += f"{localisation.get('LOG_ERROR_FETCH')} {e}"
            await in_app_logging.send_log(self.bot, log, 0, 1, interaction)

async def setup(bot):
    await bot.add_cog(ModcommandsCog(bot))
