import discord
from discord.ext import commands
from discord import app_commands
import in_app_logging
import helpers

logger = helpers.load_logging()
localisation = dict(helpers.load_localisation())

class AdminCommandsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name=localisation.get('ADMINCOMMANDS_CMD_NAME'), description=localisation.get('ADMINCOMMANDS_CMD_DESC'))
    @app_commands.describe(command=localisation.get('ANY_CMD_COMMAND'))
    @app_commands.choices(command=[app_commands.Choice(name=localisation.get('ADMINCOMMANDS_CMD_NAME'), value="admincommands"), app_commands.Choice(name=localisation.get('ADDADMIN_CMD_NAME'), value="addadmin"), app_commands.Choice(name=localisation.get('REMOVEADMIN_CMD_NAME'), value="removeadmin"), app_commands.Choice(name=localisation.get('LISTADMIN_CMD_NAME'), value="listadmin"), app_commands.Choice(name=localisation.get('UPDATECODE_CMD_NAME'), value="updatecode"), app_commands.Choice(name=localisation.get('RESTART_CMD_NAME'), value="restart"), app_commands.Choice(name=localisation.get('BROADCAST_CMD_NAME'), value="broadcast"), app_commands.Choice(name=localisation.get('STATUS_CMD_NAME'), value="status"), app_commands.Choice(name=localisation.get('CONNECTED_CMD_NAME'), value="connected"), app_commands.Choice(name=localisation.get('EXPORTDB_CMD_NAME'), value="exportdb"), app_commands.Choice(name=localisation.get('UPDATEDB_CMD_NAME'), value="updatedb"), app_commands.Choice(name=localisation.get('SCRAPE_CMD_NAME'), value="scrape")])
    async def admincommands(self, interaction: discord.Interaction, command: str = None):
        await interaction.response.defer(ephemeral=True)
        try:
            header = localisation.get('ADMINCOMMANDS_LOG_HEADER')
            logger.info(f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('ADMINCOMMANDS_CMD_NAME')} commad: {command}")
            log = f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('ADMINCOMMANDS_CMD_NAME')} commad: {command}"

            admins = await helpers.load_file('Admin file')
            if str(interaction.user.id) in admins or int(interaction.user.id) in await helpers.load_json_key("config", "ClientAdminIDs"):

                if command is None:
                    command = "default"

                if command == "default":
                    title_text = f"{localisation.get('COMMANDS_MSG_EMBED_TITLE_AVAILABLE_COMMANDS')}"
                else:
                    title_text = f"{localisation.get('COMMANDS_MSG_EMBED_TITLE_COMMAND_USAGE')}"

                descriptions = {
                    """default""": f"""</{localisation.get('ADMINCOMMANDS_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("ADMINCOMMANDS_CMD_NAME")}_CMD'.upper())}>\n</{localisation.get('ADDADMIN_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("ADDADMIN_CMD_NAME")}_CMD'.upper())}>\n</{localisation.get('REMOVEADMIN_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("REMOVEADMIN_CMD_NAME")}_CMD'.upper())}>\n</{localisation.get('LISTADMIN_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("LISTADMIN_CMD_NAME")}_CMD'.upper())}>\n</{localisation.get('UPDATECODE_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("UPDATECODE_CMD_NAME")}_CMD'.upper())}>\n</{localisation.get('RESTART_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("RESTART_CMD_NAME")}_CMD'.upper())}>\n</{localisation.get('BROADCAST_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("BROADCAST_CMD_NAME")}_CMD'.upper())}>\n</{localisation.get('STATUS_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("STATUS_CMD_NAME")}_CMD'.upper())}>\n</{localisation.get('CONNECTED_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("CONNECTED_CMD_NAME")}_CMD'.upper())}>\n</{localisation.get('EXPORTDB_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("EXPORTDB_CMD_NAME")}_CMD'.upper())}>\n</{localisation.get('UPDATEDB_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("UPDATEDB_CMD_NAME")}_CMD'.upper())}>\n</{localisation.get('SCRAPE_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("SCRAPE_CMD_NAME")}_CMD'.upper())}>\n""",
                    """admincommands""": f"""## </{localisation.get('ADMINCOMMANDS_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("ADMINCOMMANDS_CMD_NAME")}_CMD'.upper())}>\n{localisation.get('ADMINCOMMANDS_CMD_DESC')}\n{localisation.get('COMMANDS_MSG_EMBED_DESC_ADDITIONAL_OPERATORS')}\n- command: {localisation.get('ANY_CMD_COMMAND')} {localisation.get('COMMANDS_MSG_OPTIONAL')}\n  - {localisation.get('COMMANDS_MSG_EMBED_DESC_OPTIONS')}\n    - {localisation.get('ADMINCOMMANDS_CMD_NAME')}\n    - {localisation.get('ADDADMIN_CMD_NAME')}\n    - {localisation.get('REMOVEADMIN_CMD_NAME')}\n    - {localisation.get('LISTADMIN_CMD_NAME')}\n    - {localisation.get('UPDATECODE_CMD_NAME')}\n    - {localisation.get('RESTART_CMD_NAME')}\n    - {localisation.get('BROADCAST_CMD_NAME')}\n    - {localisation.get('STATUS_CMD_NAME')}\n    - {localisation.get('CONNECTED_CMD_NAME')}\n    - {localisation.get('EXPORTDB_CMD_NAME')}\n    - {localisation.get('UPDATEDB_CMD_NAME')}\n    - {localisation.get('SCRAPE_CMD_NAME')}\n""",
                    """addadmin""": f"""## </{localisation.get('ADDADMIN_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("ADDADMIN_CMD_NAME")}_CMD'.upper())}>\n{localisation.get('ADDADMIN_CMD_DESC')}\n{localisation.get('COMMANDS_MSG_EMBED_DESC_ADDITIONAL_OPERATORS')}\n- user: {localisation.get('ADDADMIN_CMD_USER')}\n""",
                    """removeadmin""": f"""## </{localisation.get('REMOVEADMIN_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("REMOVEADMIN_CMD_NAME")}_CMD'.upper())}>\n{localisation.get('REMOVEADMIN_CMD_DESC')}\n{localisation.get('COMMANDS_MSG_EMBED_DESC_ADDITIONAL_OPERATORS')}\n- user: {localisation.get('REMOVEADMIN_CMD_USER')}\n""",
                    """listadmin""": f"""## </{localisation.get('LISTADMIN_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("LISTADMIN_CMD_NAME")}_CMD'.upper())}>\n{localisation.get('LISTADMIN_CMD_DESC')}\n""",
                    """updatecode""": f"""## </{localisation.get('UPDATECODE_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("UPDATECODE_CMD_NAME")}_CMD'.upper())}>\n{localisation.get('UPDATECODE_CMD_DESC')}\n{localisation.get('COMMANDS_MSG_EMBED_DESC_ADDITIONAL_OPERATORS')}\n- restart_in: {localisation.get('UPDATECODE_CMD_RESTART_IN')} {localisation.get('COMMANDS_MSG_OPTIONAL')}\n""",
                    """restart""": f"""## </{localisation.get('RESTART_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("RESTART_CMD_NAME")}_CMD'.upper())}>\n{localisation.get('RESTART_CMD_DESC')}\n""",
                    """broadcast""": f"""## </{localisation.get('BROADCAST_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("BROADCAST_CMD_NAME")}_CMD'.upper())}>\n{localisation.get('BROADCAST_CMD_DESC')}\n{localisation.get('COMMANDS_MSG_EMBED_DESC_ADDITIONAL_OPERATORS')}\n- message_title: {localisation.get('BROADCAST_CMD_MESSAGE_TITLE')}\n- {localisation.get('BROADCAST_ADDITIONAL')}""",
                    """status""": f"""## </{localisation.get('STATUS_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("STATUS_CMD_NAME")}_CMD'.upper())}>\n{localisation.get('STATUS_CMD_DESC')}\n{localisation.get('COMMANDS_MSG_EMBED_DESC_ADDITIONAL_OPERATORS')}\n- action: {localisation.get('STATUS_CMD_ACTION')}\n  - {localisation.get('COMMANDS_MSG_EMBED_DESC_OPTIONS')}\n    - {localisation.get('STATUS_CMD_ACTION_OPTION_ADD')}\n    - {localisation.get('STATUS_CMD_ACTION_OPTION_ACTIVATE')}\n    - {localisation.get('STATUS_CMD_ACTION_OPTION_REMOVE')}\n- status_type: {localisation.get('STATUS_CMD_STATUS_TYPE')} {localisation.get('COMMANDS_MSG_OPTIONAL')}\n  - {localisation.get('COMMANDS_MSG_EMBED_DESC_OPTIONS')}\n    - {localisation.get('STATUS_CMD_STATUS_TYPE_OPTION_PLAYING')}\n    - {localisation.get('STATUS_CMD_STATUS_TYPE_OPTION_WATCHING')}\n    - {localisation.get('STATUS_CMD_STATUS_TYPE_OPTION_STREAMING')}\n    - {localisation.get('STATUS_CMD_STATUS_TYPE_OPTION_LISTENING')}\n    - {localisation.get('STATUS_CMD_STATUS_TYPE_OPTION_COMPETING')}\n- status_text: {localisation.get('STATUS_CMD_STATUS_TEXT')} {localisation.get('COMMANDS_MSG_OPTIONAL')}\n- url: {localisation.get('STATUS_CMD_URL')} {localisation.get('COMMANDS_MSG_OPTIONAL')}\n""",
                    """connected""": f"""## </{localisation.get('CONNECTED_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("CONNECTED_CMD_NAME")}_CMD'.upper())}>\n{localisation.get('CONNECTED_CMD_DESC')}\n{localisation.get('COMMANDS_MSG_EMBED_DESC_ADDITIONAL_OPERATORS')}\n- mod: {localisation.get('CONNECTED_CMD_MOD')} {localisation.get('COMMANDS_MSG_OPTIONAL')}\n""",
                    """exportdb""": f"""## </{localisation.get('EXPORTDB_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("EXPORTDB_CMD_NAME")}_CMD'.upper())}>\n{localisation.get('EXPORTDB_CMD_DESC')}\n""",
                    """updatedb""": f"""## </{localisation.get('UPDATEDB_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("UPDATEDB_CMD_NAME")}_CMD'.upper())}>\n{localisation.get('UPDATEDB_CMD_DESC')}\n""",
                    """scrape""": f"""## </{localisation.get('SCRAPE_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("SCRAPE_CMD_NAME")}_CMD'.upper())}>\n{localisation.get('SCRAPE_CMD_DESC')}\n""",
                }

                description_text = descriptions[command]

                embed = discord.Embed(
                    title=title_text,
                    description=description_text,
                    color=discord.Color(0xff00ff)
                )
                embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')

                await interaction.followup.send(embed=embed, ephemeral=True)
                log += f"\n{header}{localisation.get('ADMIN_LOG_IS_ADMIN')}"
            else:
                await interaction.followup.send(f"{localisation.get('ADMIN_MSG_NO_PERMISSION')}", ephemeral=True)
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
        await bot.add_cog(AdminCommandsCog(bot), guilds=[discord.Object(id=int(server))], override=True)
