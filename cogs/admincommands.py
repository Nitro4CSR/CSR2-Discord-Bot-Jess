import discord
from discord.ext import commands
from discord import app_commands
import in_app_logging
import helpers

logger = helpers.load_logging()

class AdminCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):

        @app_commands.command(name=self.bot.localisation.get('ADMINCOMMANDS_CMD_NAME'), description=self.bot.localisation.get('ADMINCOMMANDS_CMD_DESC'))
        @app_commands.describe(command=self.bot.localisation.get('ANY_CMD_COMMAND'))
        @app_commands.choices(command=[app_commands.Choice(name=self.bot.localisation.get('ADMINCOMMANDS_CMD_NAME'), value="admincommands"),app_commands.Choice(name={self.bot.localisation.get('ADDADMIN_CMD_NAME')}, value="addadmin"), app_commands.Choice(name={self.bot.localisation.get('REMOVEADMIN_CMD_NAME')}, value="removeadmin"), app_commands.Choice(name={self.bot.localisation.get('LISTADMIN_CMD_NAME')}, value="listadmin"), app_commands.Choice(name={self.bot.localisation.get('UPDATECODE_CMD_NAME')}, value="updatecode"), app_commands.Choice(name={self.bot.localisation.get('RESTART_CMD_NAME')}, value="restart"), app_commands.Choice(name={self.bot.localisation.get('BROADCAST_CMD_NAME')}, value="broadcast"), app_commands.Choice(name={self.bot.localisation.get('STATUS_CMD_NAME')}, value="status"), app_commands.Choice(name={self.bot.localisation.get('CONNECTED_CMD_NAME')}, value="connected"), app_commands.Choice(name={self.bot.localisation.get('EXPORTDB_CMD_NAME')}, value="exportdb"), app_commands.Choice(name={self.bot.localisation.get('UPDATEDB_CMD_NAME')}, value="updatedb"), app_commands.Choice(name={self.bot.localisation.get('SCRAPE_CMD_NAME')}, value="scrape")])
        async def admincommands(interaction: discord.Interaction, command: str = None):
            await interaction.response.defer(ephemeral=True)
            try:
                header = self.bot.localisation.get('ADMINCOMMANDS_LOG_HEADER')
                logger.info(f"{header}{self.bot.localisation.get('LOG_CMD_TRIGGERED')} /{self.bot.localisation.get('ADMINCOMMANDS_CMD_NAME')} commad: {command}")
                log = f"{header}{self.bot.localisation.get('LOG_CMD_TRIGGERED')} /{self.bot.localisation.get('ADMINCOMMANDS_CMD_NAME')} commad: {command}"

                admins = await helpers.load_file('Admin file')
                if str(interaction.user.id) in admins or int(interaction.user.id) in await helpers.load_json_key("config", "ClientAdminIDs"):

                    if command is None:
                        command = "default"

                    if command == "default":
                        title_text = f"{self.bot.localisation.get('COMMANDS_MSG_EMBED_TITLE_AVAILABLE_COMMANDS')}"
                    else:
                        title_text = f"{self.bot.localisation.get('COMMANDS_MSG_EMBED_TITLE_COMMAND_USAGE')}"

                    descriptions = {
                        """default""": f"""</{self.bot.localisation.get('ADMINCOMMANDS_CMD_NAME')}:{await helpers.load_json_key('session', f'{self.bot.localisation.get("ADMINCOMMANDS_CMD_NAME")}_CMD'.upper())}>\n</{self.bot.localisation.get('ADDADMIN_CMD_NAME')}:{await helpers.load_json_key('session', f'{self.bot.localisation.get("ADDADMIN_CMD_NAME")}_CMD'.upper())}>\n</{self.bot.localisation.get('REMOVEADMIN_CMD_NAME')}:{await helpers.load_json_key('session', f'{self.bot.localisation.get("REMOVEADMIN_CMD_NAME")}_CMD'.upper())}>\n</{self.bot.localisation.get('LISTADMIN_CMD_NAME')}:{await helpers.load_json_key('session', f'{self.bot.localisation.get("LISTADMIN_CMD_NAME")}_CMD'.upper())}>\n</{self.bot.localisation.get('UPDATECODE_CMD_NAME')}:{await helpers.load_json_key('session', f'{self.bot.localisation.get("UPDATECODE_CMD_NAME")}_CMD'.upper())}>\n</{self.bot.localisation.get('RESTART_CMD_NAME')}:{await helpers.load_json_key('session', f'{self.bot.localisation.get("RESTART_CMD_NAME")}_CMD'.upper())}>\n</{self.bot.localisation.get('BROADCAST_CMD_NAME')}:{await helpers.load_json_key('session', f'{self.bot.localisation.get("BROADCAST_CMD_NAME")}_CMD'.upper())}>\n</{self.bot.localisation.get('STATUS_CMD_NAME')}:{await helpers.load_json_key('session', f'{self.bot.localisation.get("STATUS_CMD_NAME")}_CMD'.upper())}>\n</{self.bot.localisation.get('CONNECTED_CMD_NAME')}:{await helpers.load_json_key('session', f'{self.bot.localisation.get("CONNECTED_CMD_NAME")}_CMD'.upper())}>\n</{self.bot.localisation.get('EXPORTDB_CMD_NAME')}:{await helpers.load_json_key('session', f'{self.bot.localisation.get("EXPORTDB_CMD_NAME")}_CMD'.upper())}>\n</{self.bot.localisation.get('UPDATEDB_CMD_NAME')}:{await helpers.load_json_key('session', f'{self.bot.localisation.get("UPDATEDB_CMD_NAME")}_CMD'.upper())}>\n</{self.bot.localisation.get('SCRAPE_CMD_NAME')}:{await helpers.load_json_key('session', f'{self.bot.localisation.get("SCRAPE_CMD_NAME")}_CMD'.upper())}>\n""",
                        """admincommands""": f"""## </{self.bot.localisation.get('ADMINCOMMANDS_CMD_NAME')}:{await helpers.load_json_key('session', f'{self.bot.localisation.get("ADMINCOMMANDS_CMD_NAME")}_CMD'.upper())}>\n{self.bot.localisation.get('ADMINCOMMANDS_CMD_DESC')}\n{self.bot.localisation.get('COMMANDS_MSG_EMBED_DESC_ADDITIONAL_OPERATORS')}\n- command: {self.bot.localisation.get('ANY_CMD_COMMAND')} {self.bot.localisation.get('COMMANDS_MSG_OPTIONAL')}\n  - {self.bot.localisation.get('COMMANDS_MSG_EMBED_DESC_OPTIONS')}\n    - {self.bot.localisation.get('ADMINCOMMANDS_CMD_NAME')}\n    - {self.bot.localisation.get('ADDADMIN_CMD_NAME')}\n    - {self.bot.localisation.get('REMOVEADMIN_CMD_NAME')}\n    - {self.bot.localisation.get('LISTADMIN_CMD_NAME')}\n    - {self.bot.localisation.get('UPDATECODE_CMD_NAME')}\n    - {self.bot.localisation.get('RESTART_CMD_NAME')}\n    - {self.bot.localisation.get('BROADCAST_CMD_NAME')}\n    - {self.bot.localisation.get('STATUS_CMD_NAME')}\n    - {self.bot.localisation.get('CONNECTED_CMD_NAME')}\n    - {self.bot.localisation.get('EXPORTDB_CMD_NAME')}\n    - {self.bot.localisation.get('UPDATEDB_CMD_NAME')}\n    - {self.bot.localisation.get('SCRAPE_CMD_NAME')}\n""",
                        """addadmin""": f"""## </{self.bot.localisation.get('ADDADMIN_CMD_NAME')}:{await helpers.load_json_key('session', f'{self.bot.localisation.get("ADDADMIN_CMD_NAME")}_CMD'.upper())}>\n{self.bot.localisation.get('ADDADMIN_CMD_DESC')}\n{self.bot.localisation.get('COMMANDS_MSG_EMBED_DESC_ADDITIONAL_OPERATORS')}\n- user: {self.bot.localisation.get('ADDADMIN_CMD_USER')}\n""",
                        """removeadmin""": f"""## </{self.bot.localisation.get('REMOVEADMIN_CMD_NAME')}:{await helpers.load_json_key('session', f'{self.bot.localisation.get("REMOVEADMIN_CMD_NAME")}_CMD'.upper())}>\n{self.bot.localisation.get('REMOVEADMIN_CMD_DESC')}\n{self.bot.localisation.get('COMMANDS_MSG_EMBED_DESC_ADDITIONAL_OPERATORS')}\n- user: {self.bot.localisation.get('REMOVEADMIN_CMD_USER')}\n""",
                        """listadmin""": f"""## </{self.bot.localisation.get('LISTADMIN_CMD_NAME')}:{await helpers.load_json_key('session', f'{self.bot.localisation.get("LISTADMIN_CMD_NAME")}_CMD'.upper())}>\n{self.bot.localisation.get('LISTADMIN_CMD_DESC')}\n""",
                        """updatecode""": f"""## </{self.bot.localisation.get('UPDATECODE_CMD_NAME')}:{await helpers.load_json_key('session', f'{self.bot.localisation.get("UPDATECODE_CMD_NAME")}_CMD'.upper())}>\n{self.bot.localisation.get('UPDATECODE_CMD_DESC')}\n{self.bot.localisation.get('COMMANDS_MSG_EMBED_DESC_ADDITIONAL_OPERATORS')}\n- restart_in: {self.bot.localisation.get('UPDATECODE_CMD_RESTART_IN')} {self.bot.localisation.get('COMMANDS_MSG_OPTIONAL')}\n""",
                        """restart""": f"""## </{self.bot.localisation.get('RESTART_CMD_NAME')}:{await helpers.load_json_key('session', f'{self.bot.localisation.get("RESTART_CMD_NAME")}_CMD'.upper())}>\n{self.bot.localisation.get('RESTART_CMD_DESC')}\n""",
                        """broadcast""": f"""## </{self.bot.localisation.get('BROADCAST_CMD_NAME')}:{await helpers.load_json_key('session', f'{self.bot.localisation.get("BROADCAST_CMD_NAME")}_CMD'.upper())}>\n{self.bot.localisation.get('BROADCAST_CMD_DESC')}\n{self.bot.localisation.get('COMMANDS_MSG_EMBED_DESC_ADDITIONAL_OPERATORS')}\n- message_title: {self.bot.localisation.get('BROADCAST_CMD_MESSAGE_TITLE')}\n- {self.bot.localisation.get('BROADCAST_ADDITIONAL')}""",
                        """status""": f"""## </{self.bot.localisation.get('STATUS_CMD_NAME')}:{await helpers.load_json_key('session', f'{self.bot.localisation.get("STATUS_CMD_NAME")}_CMD'.upper())}>\n{self.bot.localisation.get('STATUS_CMD_DESC')}\n{self.bot.localisation.get('COMMANDS_MSG_EMBED_DESC_ADDITIONAL_OPERATORS')}\n- action: {self.bot.localisation.get('STATUS_CMD_ACTION')}\n  - {self.bot.localisation.get('COMMANDS_MSG_EMBED_DESC_OPTIONS')}\n    - {self.bot.localisation.get('STATUS_CMD_ACTION_OPTION_ADD')}\n    - {self.bot.localisation.get('STATUS_CMD_ACTION_OPTION_ACTIVATE')}\n    - {self.bot.localisation.get('STATUS_CMD_ACTION_OPTION_REMOVE')}\n- status_type: {self.bot.localisation.get('STATUS_CMD_STATUS_TYPE')} {self.bot.localisation.get('COMMANDS_MSG_OPTIONAL')}\n  - {self.bot.localisation.get('COMMANDS_MSG_EMBED_DESC_OPTIONS')}\n    - {self.bot.localisation.get('STATUS_CMD_STATUS_TYPE_OPTION_PLAYING')}\n    - {self.bot.localisation.get('STATUS_CMD_STATUS_TYPE_OPTION_WATCHING')}\n    - {self.bot.localisation.get('STATUS_CMD_STATUS_TYPE_OPTION_STREAMING')}\n    - {self.bot.localisation.get('STATUS_CMD_STATUS_TYPE_OPTION_LISTENING')}\n    - {self.bot.localisation.get('STATUS_CMD_STATUS_TYPE_OPTION_COMPETING')}\n- status_text: {self.bot.localisation.get('STATUS_CMD_STATUS_TEXT')} {self.bot.localisation.get('COMMANDS_MSG_OPTIONAL')}\n- url: {self.bot.localisation.get('STATUS_CMD_URL')} {self.bot.localisation.get('COMMANDS_MSG_OPTIONAL')}\n""",
                        """connected""": f"""## </{self.bot.localisation.get('CONNECTED_CMD_NAME')}:{await helpers.load_json_key('session', f'{self.bot.localisation.get("CONNECTED_CMD_NAME")}_CMD'.upper())}>\n{self.bot.localisation.get('CONNECTED_CMD_DESC')}\n{self.bot.localisation.get('COMMANDS_MSG_EMBED_DESC_ADDITIONAL_OPERATORS')}\n- mod: {self.bot.localisation.get('CONNECTED_CMD_MOD')} {self.bot.localisation.get('COMMANDS_MSG_OPTIONAL')}\n""",
                        """exportdb""": f"""## </{self.bot.localisation.get('EXPORTDB_CMD_NAME')}:{await helpers.load_json_key('session', f'{self.bot.localisation.get("EXPORTDB_CMD_NAME")}_CMD'.upper())}>\n{self.bot.localisation.get('EXPORTDB_CMD_DESC')}\n""",
                        """updatedb""": f"""## </{self.bot.localisation.get('UPDATEDB_CMD_NAME')}:{await helpers.load_json_key('session', f'{self.bot.localisation.get("UPDATEDB_CMD_NAME")}_CMD'.upper())}>\n{self.bot.localisation.get('UPDATEDB_CMD_DESC')}\n""",
                        """scrape""": f"""## </{self.bot.localisation.get('SCRAPE_CMD_NAME')}:{await helpers.load_json_key('session', f'{self.bot.localisation.get("SCRAPE_CMD_NAME")}_CMD'.upper())}>\n{self.bot.localisation.get('SCRAPE_CMD_DESC')}\n""",
                    }

                    description_text = descriptions[command]

                    embed = discord.Embed(
                        title=title_text,
                        description=description_text,
                        color=discord.Color(0xff00ff)
                    )
                    embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')

                    await interaction.followup.send(embed=embed, ephemeral=True)
                    log += f"\n{header}{self.bot.localisation.get('ADMIN_LOG_IS_ADMIN')}"
                else:
                    await interaction.followup.send(f"{self.bot.localisation.get('ADMIN_MSG_NO_PERMISSION')}", ephemeral=True)
                    log += f"\n{header}{self.bot.localisation.get('ADMIN_LOG_NOT_ADMIN')}"
                await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
            except Exception as e:
                await interaction.followup.send(f"{self.bot.localisation.get('MSG_ERROR_FETCH')} {e}", ephemeral=True)
                logger.info(f"{self.bot.localisation.get('LOG_ERROR_FETCH')} {e}")
                log += f"{self.bot.localisation.get('LOG_ERROR_FETCH')} {e}"
                await in_app_logging.send_log(self.bot, log, 0, 1, interaction)

        self.bot.tree.add_command(admincommands, guilds=[discord.Object(id=int(server)) for server in await helpers.load_json_key("config", "ClientAdminServers")])

async def setup(bot):
    ADMIN_SERVERS = await helpers.load_json_key("config", "ClientAdminServers")
    for server in ADMIN_SERVERS:
        await bot.add_cog(AdminCommandsCog(bot), guilds=[discord.Object(id=int(server))], override=True)
