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
    @app_commands.choices(command=[app_commands.Choice(name=localisation.get('MODCOMMANDS_CMD_NAME'), value='modcommands'), app_commands.Choice(name=localisation.get('LIMITRESULTS_CMD_NAME'), value='limitresults'), app_commands.Choice(name=localisation.get('ANNOUNCE_UPDATES_ADD_CMD_NAME'), value='announce_updates_add'), app_commands.Choice(name=localisation.get('ANNOUNCE_UPDATES_DELETE_CMD_NAME'), value='announce_updates_delete'), app_commands.Choice(name=localisation.get('CUSTOMLIST_CREATE_CMD_NAME'), value='customlist_create'), app_commands.Choice(name=localisation.get('CUSTOMLIST_UPLOAD_CMD_NAME'), value='customlist_upload'), app_commands.Choice(name=localisation.get('CUSTOMLIST_TEMPLATE_CMD_NAME'), value='customlist_template'), app_commands.Choice(name=localisation.get('CUSTOMLIST_EDIT_CMD_NAME'), value='customlist_edit'), app_commands.Choice(name=localisation.get('CUSTOMLIST_DELETE_CMD_NAME'), value='customlist_delete')])
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
                """default""": f"""</{localisation.get('LIMITRESULTS_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("LIMITRESULTS_CMD_NAME")}_CMD'.upper())}>\n</{localisation.get('ANNOUNCE_UPDATES_ADD_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("ANNOUNCE_UPDATES_ADD_CMD_NAME")}_CMD'.upper())}>\n</{localisation.get('ANNOUNCE_UPDATES_DELETE_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("ANNOUNCE_UPDATES_DELETE_CMD_NAME")}_CMD'.upper())}>\n</{localisation.get('CUSTOMLIST_CREATE_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("CUSTOMLIST_CREATE_CMD_NAME")}_CMD'.upper())}>\n</{localisation.get('CUSTOMLIST_UPLOAD_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("CUSTOMLIST_UPLOAD_CMD_NAME")}_CMD'.upper())}>\n</{localisation.get('CUSTOMLIST_TEMPLATE_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("CUSTOMLIST_TEMPLATE_CMD_NAME")}_CMD'.upper())}>\n</{localisation.get('CUSTOMLIST_EDIT_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("CUSTOMLIST_EDIT_CMD_NAME")}_CMD'.upper())}>\n</{localisation.get('CUSTOMLIST_DELETE_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("CUSTOMLIST_DELETE_CMD_NAME")}_CMD'.upper())}>\n""",
                """modcommands""": f"""## </{localisation.get('MODCOMMANDS_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("MODCOMMANDS_CMD_NAME")}_CMD'.upper())}>\n{localisation.get("LIMITRESULTS_CMD_DESC")}\n{localisation.get('COMMANDS_MSG_EMBED_DESC_ADDITIONAL_OPERATORS')}\n- command: {localisation.get('ANY_CMD_COMMAND')} {localisation.get('COMMANDS_MSG_OPTIONAL')}\n\n  - {localisation.get('COMMANDS_MSG_EMBED_DESC_OPTIONS')}\n    - {localisation.get('MODCOMMANDS_CMD_NAME')}\n    - {localisation.get('LIMITRESULTS_CMD_NAME')}\n    - {localisation.get('ANNOUNCE_UPDATES_ADD_CMD_NAME')}\n    - {localisation.get('ANNOUNCE_UPDATES_DELETE_CMD_NAME')}\n    - {localisation.get('CUSTOMLIST_CREATE_CMD_NAME')}\n    - {localisation.get('CUSTOMLIST_UPLOAD_CMD_NAME')}\n    - {localisation.get('CUSTOMLIST_TEMPLATE_CMD_NAME')}\n    - {localisation.get('CUSTOMLIST_EDIT_CMD_NAME')}\n    - {localisation.get('CUSTOMLIST_DELETE_CMD_NAME')}\n""",
                """limitresults""": f"""## </{localisation.get('LIMITRESULTS_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("LIMITRESULTS_CMD_NAME")}_CMD'.upper())}>\n{localisation.get("LIMITRESULTS_CMD_DESC")}\n{localisation.get('COMMANDS_MSG_EMBED_DESC_ADDITIONAL_OPERATORS')}\n- limit: {localisation.get('LIMITRESULTS_CMD_LIMIT')}\n- scope: {localisation.get('GETLIMIT_CMD_SCOPE')} {localisation.get('COMMANDS_MSG_OPTIONAL')}\n  - {localisation.get('COMMANDS_MSG_EMBED_DESC_OPTIONS')}\n    - {localisation.get('LIMIT_CMD_SCOPE_OPTION_SERVER')}\n    - {localisation.get('LIMIT_CMD_SCOPE_OPTION_PERSONAL')}\n""",
                """announceupdates_add""": f"""## </{localisation.get('ANNOUNCE_UPDATES_ADD_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("ANNOUNCE_UPDATES_ADD_CMD_NAME")}_CMD'.upper())}>\n{localisation.get("NOTIFY_UPDATES_ADD_CMD_DESC")}\n{localisation.get('COMMANDS_MSG_EMBED_DESC_ADDITIONAL_OPERATORS')}\n- channel: {localisation.get('ANNOUNCE_UPDATES_CMD_CHANNEL')}\n- scope: {localisation.get('ANY_CMD_SCOPE')} {localisation.get('COMMANDS_MSG_OPTIONAL')}\n  - {localisation.get('COMMANDS_MSG_EMBED_DESC_OPTIONS')}\n    - {localisation.get('ANY_CMD_SCOPE_OPTION_ALL')}\n    - {localisation.get('ANY_CMD_SCOPE_OPTION_CSR2')}\n    - {localisation.get('ANY_CMD_SCOPE_OPTION_CSR3')}\n    - {localisation.get('ANY_CMD_SCOPE_OPTION_BLOG')}\n""",
                """announceupdates_delete""": f"""## </{localisation.get('ANNOUNCE_UPDATES_DELETE_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("ANNOUNCE_UPDATES_DELETE_CMD_NAME")}_CMD'.upper())}>\n{localisation.get("NOTIFY_UPDATES_DELETE_CMD_DESC")}\n{localisation.get('COMMANDS_MSG_EMBED_DESC_ADDITIONAL_OPERATORS')}\n- channel: {localisation.get('ANNOUNCE_UPDATES_CMD_CHANNEL')}\n- scope: {localisation.get('ANY_CMD_SCOPE')} {localisation.get('COMMANDS_MSG_OPTIONAL')}\n  - {localisation.get('COMMANDS_MSG_EMBED_DESC_OPTIONS')}\n    - {localisation.get('ANY_CMD_SCOPE_OPTION_ALL')}\n    - {localisation.get('ANY_CMD_SCOPE_OPTION_CSR2')}\n    - {localisation.get('ANY_CMD_SCOPE_OPTION_CSR3')}\n    - {localisation.get('ANY_CMD_SCOPE_OPTION_BLOG')}\n""",
                """customlist_create""": f"""## </{localisation.get('CUSTOMLIST_CREATE_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("CUSTOMLIST_CREATE_CMD_NAME")}_CMD'.upper())}>\n{localisation.get('CUSTOMLIST_CREATE_CMD_DESC')}\n{localisation.get('COMMANDS_MSG_EMBED_DESC_ADDITIONAL_OPERATORS')}\n- global_list: {localisation.get('CUSTOMLIST_ANY_CMD_GLOBAL_LIST')} {localisation.get('COMMANDS_MSG_OPTIONAL')}\n  - {localisation.get('COMMANDS_MSG_EMBED_DESC_OPTIONS')}\n    - {localisation.get('CUSTOMLIST_ANY_CMD_GLOBAL_LIST_OPTION_TRUE')}\n    - {localisation.get('CUSTOMLIST_ANY_CMD_GLOBAL_LIST_OPTION_FALSE')}\n""",
                """customlist_upload""": f"""## </{localisation.get('CUSTOMLIST_UPLOAD_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("CUSTOMLIST_UPLOAD_CMD_NAME")}_CMD'.upper())}>\n{localisation.get('CUSTOMLIST_UPLOAD_CMD_DESC')}\n{localisation.get('COMMANDS_MSG_EMBED_DESC_ADDITIONAL_OPERATORS')}\n- list_file: {localisation.get('CUSTOMLIST_UPLOAD_CMD_LIST_FILE')}\n- global_list: {localisation.get('CUSTOMLIST_ANY_CMD_GLOBAL_LIST')} {localisation.get('COMMANDS_MSG_OPTIONAL')}\n  - {localisation.get('COMMANDS_MSG_EMBED_DESC_OPTIONS')}\n    - {localisation.get('CUSTOMLIST_ANY_CMD_GLOBAL_LIST_OPTION_TRUE')}\n    - {localisation.get('CUSTOMLIST_ANY_CMD_GLOBAL_LIST_OPTION_FALSE')}\n""",
                """customlist_template""": f"""## </{localisation.get('CUSTOMLIST_TEMPLATE_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("CUSTOMLIST_TEMPLATE_CMD_NAME")}_CMD'.upper())}>\n{localisation.get('CUSTOMLIST_TEMPLATE_CMD_DESC')}\n""",
                """customlist_edit""": f"""## </{localisation.get('CUSTOMLIST_EDIT_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("CUSTOMLIST_EDIT_CMD_NAME")}_CMD'.upper())}>\n{localisation.get('CUSTOMLIST_EDIT_CMD_DESC')}\n{localisation.get('COMMANDS_MSG_EMBED_DESC_ADDITIONAL_OPERATORS')}\n- list_id: {localisation.get('CUSTOMLIST_ANY_CMD_LIST_ID')}\n- global_list: {localisation.get('CUSTOMLIST_ANY_CMD_GLOBAL_LIST')} {localisation.get('COMMANDS_MSG_OPTIONAL')}\n  - {localisation.get('COMMANDS_MSG_EMBED_DESC_OPTIONS')}\n    - {localisation.get('CUSTOMLIST_ANY_CMD_GLOBAL_LIST_OPTION_TRUE')}\n    - {localisation.get('CUSTOMLIST_ANY_CMD_GLOBAL_LIST_OPTION_FALSE')}\n- list_name: {localisation.get('CUSTOMLIST_ANY_CMD_LIST_NAME')} {localisation.get('COMMANDS_MSG_OPTIONAL')}\n- group: {localisation.get('CUSTOMLIST_ANY_CMD_GROUP')} {localisation.get('COMMANDS_MSG_OPTIONAL')}\n  - {localisation.get('COMMANDS_MSG_EMBED_DESC_OPTIONS')}\n    - {localisation.get('CUSTOMLIST_EDIT_CMD_ANY_OPTION_ADD')}\n    - {localisation.get('CUSTOMLIST_EDIT_CMD_ANY_OPTION_DELETE')}\n    - {localisation.get('CUSTOMLIST_EDIT_CMD_ANY_OPTION_RENAME')}\n- group_name: {localisation.get('CUSTOMLIST_ANY_CMD_GROUP_NAME')} {localisation.get('COMMANDS_MSG_OPTIONAL')}\n- car: {localisation.get('CUSTOMLIST_ANY_CMD_CAR')} {localisation.get('COMMANDS_MSG_OPTIONAL')}\n  - {localisation.get('COMMANDS_MSG_EMBED_DESC_OPTIONS')}\n    - {localisation.get('CUSTOMLIST_EDIT_CMD_ANY_OPTION_ADD')}\n    - {localisation.get('CUSTOMLIST_EDIT_CMD_ANY_OPTION_DELETE')}\n- car_name: {localisation.get('CUSTOMLIST_ANY_CMD_CAR_NAME')} {localisation.get('COMMANDS_MSG_OPTIONAL')}\n- car_group: {localisation.get('CUSTOMLIST_ANY_CMD_CAR_GROUP')} {localisation.get('COMMANDS_MSG_OPTIONAL')}\n""",
                """customlist_delete""": f"""## </{localisation.get('CUSTOMLIST_DELETE_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("CUSTOMLIST_DELETE_CMD_NAME")}_CMD'.upper())}>\n{localisation.get('CUSTOMLIST_DELETE_CMD_DESC')}\n{localisation.get('COMMANDS_MSG_EMBED_DESC_ADDITIONAL_OPERATORS')}\n- list_id: {localisation.get('CUSTOMLIST_ANY_CMD_LIST_ID')}\n"""
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
