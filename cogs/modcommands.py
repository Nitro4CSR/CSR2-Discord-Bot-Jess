import discord
from discord.ext import commands
from discord import app_commands
import in_app_logging
import helpers

logger = helpers.load_logging()

class ModcommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):

        @app_commands.command(name=self.bot.localisation.get('MODCOMMANDS_CMD_NAME'), description=self.bot.localisation.get('MODCOMMANDS_CMD_DESC'))
        @app_commands.describe(command=self.bot.localisation.get('ANY_CMD_COMMAND'))
        @app_commands.choices(command=[app_commands.Choice(name='csr2_limitresults', value='limitresults'), app_commands.Choice(name='csr2_announce_updates_add', value='announce_updates_add'), app_commands.Choice(name='csr2_announce_updates_delete', value='announce_updates_delete')])
        async def modcommands(interaction: discord.Interaction, command: str = None):
            await interaction.response.defer()
            try:
                header = self.bot.localisation.get('MODCOMMANDS_LOG_HEADER')
                logger.info(f"{header}{self.bot.localisation.get('LOG_CMD_TRIGGERED')} /{self.bot.localisation.get('MODCOMMANDS_CMD_NAME')} commad: {command}")
                log = f"{header}{self.bot.localisation.get('LOG_CMD_TRIGGERED')} /{self.bot.localisation.get('MODCOMMANDS_CMD_NAME')} commad: {command}"
    
                if not interaction.guild or not interaction.user.guild_permissions.administrator and str(interaction.user.id) not in await helpers.load_json_key("config", "ClientAdminIDs"):
                    await interaction.followup.send(f"{self.bot.localisation.get('MODCOMMANDS_MSG_WARNING_NO_PERMISSION_SERVER')}", ephemeral=True)
                    await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
                    return
                command = "default" if command is None else command
                title_text = f"{self.bot.localisation.get('COMMANDS_MSG_EMBED_TITLE_AVAILABLE_COMMANDS')}" if command == "default" else f"{self.bot.localisation.get('COMMANDS_MSG_EMBED_TITLE_COMMAND_USAGE')}"
                descriptions = {
                    """default""": f"""</{self.bot.localisation.get('LIMITRESULTS_CMD_NAME')}:{await helpers.load_json_key('session', f'{self.bot.localisation.get("LIMITRESULTS_CMD_NAME")}_CMD'.upper())}>\n</{self.bot.localisation.get('ANNOUNCE_UPDATES_ADD_CMD_NAME')}:{await helpers.load_json_key('session', f'{self.bot.localisation.get("ANNOUNCE_UPDATES_ADD_CMD_NAME")}_CMD'.upper())}>\n</{self.bot.localisation.get('ANNOUNCE_UPDATES_DELETE_CMD_NAME')}:{await helpers.load_json_key('session', f'{self.bot.localisation.get("ANNOUNCE_UPDATES_DELETE_CMD_NAME")}_CMD'.upper())}>\n""",
                    """limitresults""": f"""## </{self.bot.localisation.get('LIMITRESULTS_CMD_NAME')}:{await helpers.load_json_key('session', f'{self.bot.localisation.get("LIMITRESULTS_CMD_NAME")}_CMD'.upper())}>\n{self.bot.localisation.get("LIMITRESULTS_CMD_DESC")}\n{self.bot.localisation.get('COMMANDS_MSG_EMBED_DESC_ADDITIONAL_OPERATORS')}\n- limit: {self.bot.localisation.get('LIMITRESULTS_CMD_LIMIT')}\n- scope: {self.bot.localisation.get('GETLIMIT_CMD_SCOPE')} {self.bot.localisation.get('COMMANDS_MSG_OPTIONAL')}\n  - {self.bot.localisation.get('COMMANDS_MSG_EMBED_DESC_OPTIONS')}\n    - {self.bot.localisation.get('LIMIT_CMD_SCOPE_OPTION_SERVER')}\n    - {self.bot.localisation.get('LIMIT_CMD_SCOPE_OPTION_PERSONAL')}\n""",
                    """announceupdates_add""": f"""## </{self.bot.localisation.get('ANNOUNCE_UPDATES_ADD_CMD_NAME')}:{await helpers.load_json_key('session', f'{self.bot.localisation.get("ANNOUNCE_UPDATES_ADD_CMD_NAME")}_CMD'.upper())}>\n{self.bot.localisation.get("NOTIFY_UPDATES_ADD_CMD_DESC")}\n{self.bot.localisation.get('COMMANDS_MSG_EMBED_DESC_ADDITIONAL_OPERATORS')}\n- channel: {self.bot.localisation.get('ANNOUNCE_UPDATES_CMD_CHANNEL')}\n- scope: {self.bot.localisation.get('ANY_CMD_SCOPE')} {self.bot.localisation.get('COMMANDS_MSG_OPTIONAL')}\n  - {self.bot.localisation.get('COMMANDS_MSG_EMBED_DESC_OPTIONS')}\n    - {self.bot.localisation.get('ANY_CMD_SCOPE_OPTION_ALL')}\n    - {self.bot.localisation.get('ANY_CMD_SCOPE_OPTION_CSR2')}\n    - {self.bot.localisation.get('ANY_CMD_SCOPE_OPTION_CSR3')}\n    - {self.bot.localisation.get('ANY_CMD_SCOPE_OPTION_BLOG')}\n""",
                    """announceupdates_delete""": f"""## </{self.bot.localisation.get('ANNOUNCE_UPDATES_DELETE_CMD_NAME')}:{await helpers.load_json_key('session', f'{self.bot.localisation.get("ANNOUNCE_UPDATES_DELETE_CMD_NAME")}_CMD'.upper())}>\n{self.bot.localisation.get("NOTIFY_UPDATES_DELETE_CMD_DESC")}\n{self.bot.localisation.get('COMMANDS_MSG_EMBED_DESC_ADDITIONAL_OPERATORS')}\n- channel: {self.bot.localisation.get('ANNOUNCE_UPDATES_CMD_CHANNEL')}\n- scope: {self.bot.localisation.get('ANY_CMD_SCOPE')} {self.bot.localisation.get('COMMANDS_MSG_OPTIONAL')}\n  - {self.bot.localisation.get('COMMANDS_MSG_EMBED_DESC_OPTIONS')}\n    - {self.bot.localisation.get('ANY_CMD_SCOPE_OPTION_ALL')}\n    - {self.bot.localisation.get('ANY_CMD_SCOPE_OPTION_CSR2')}\n    - {self.bot.localisation.get('ANY_CMD_SCOPE_OPTION_CSR3')}\n    - {self.bot.localisation.get('ANY_CMD_SCOPE_OPTION_BLOG')}\n""",
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
                await interaction.followup.send(f"{self.bot.localisation.get('MSG_ERROR_FETCH')} {e}")
                logger.info(f"{self.bot.localisation.get('LOG_ERROR_FETCH')} {e}")
                log += f"{self.bot.localisation.get('LOG_ERROR_FETCH')} {e}"
                await in_app_logging.send_log(self.bot, log, 0, 1, interaction)

        self.bot.tree.add_command(modcommands)

async def setup(bot):
    await bot.add_cog(ModcommandsCog(bot))
