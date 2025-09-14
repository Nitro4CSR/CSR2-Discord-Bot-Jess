import discord
from discord.ext import commands
from discord import app_commands
import in_app_logging
import helpers

logger = helpers.load_logging()

class AnnounceUpdatesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):

        @app_commands.command(name=self.bot.localisation.get('ANNOUNCE_UPDATES_ADD_CMD_NAME'), description=self.bot.localisation.get('ANNOUNCE_UPDATES_ADD_CMD_DESC'))
        @app_commands.choices(scope=helpers.load_command_options_scope(self.bot.localisation))
        @app_commands.describe(channel=self.bot.localisation.get('ANNOUNCE_UPDATES_CMD_CHANNEL'), scope=self.bot.localisation.get('ANY_CMD_SCOPE'))
        async def announceupdates_add(interaction: discord.Interaction, channel: discord.TextChannel, scope: str = None):
            await interaction.response.defer(ephemeral=True)
            try:
                header = self.bot.localisation.get('ANNOUNCE_UPDATES_ADD_LOG_HEADER')
                logger.info(f"{header}{self.bot.localisation.get('LOG_CMD_TRIGGERED')} /{self.bot.localisation.get('ANNOUNCE_UPDATES_ADD_CMD_NAME')} channel: {channel} scope: {scope}")
                log = f"{header}{self.bot.localisation.get('LOG_CMD_TRIGGERED')} /{self.bot.localisation.get('ANNOUNCE_UPDATES_ADD_CMD_NAME')} channel: {channel} scope: {scope}"

                if interaction.user.id == interaction.guild.owner.id or interaction.user.guild_permissions.administrator or interaction.user.id in await helpers.load_json_key("config", "ClientAdminIDs"):
                    logger.info(f"{header}{self.bot.localisation.get('MODERATOR_LOG_IS_MOD')}")
                    log += f"\n{header}{self.bot.localisation.get('MODERATOR_LOG_IS_MOD')}"

                    scope = await str_to_list(scope)

                    embed = discord.Embed(title=f"{self.bot.localisation.get('ANNOUNCE_UPDATES_ADD_MSG_EMBED_TITLE')}", description=f"{self.bot.localisation.get('ANNOUNCE_UPDATES_ADD_MSG_EMBED_DESC')} {scope}", color=discord.Color(0xff00ff))
                    embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')

                    try:
                        send_channel = self.bot.get_channel(int(channel.id))
                        message = await send_channel.send(embed=embed)
                        for scope in scope:
                            await process_request(channel.id, scope, 1)
                            status = 2
                        await interaction.followup.send(f"{self.bot.localisation.get('LOG_THE_CHANNEL')} {channel.mention} {self.bot.localisation.get('ANNOUNCE_UPDATES_ADD_LOG_DONE')}", ephemeral=True)
                        logger.info(f"{header}{self.bot.localisation.get('LOG_THE_CHANNEL')} {channel} {self.bot.localisation.get('ANNOUNCE_UPDATES_ADD_LOG_DONE')}")
                        log += f"\n{header}{self.bot.localisation.get('LOG_THE_CHANNEL')} {channel} {self.bot.localisation.get('ANNOUNCE_UPDATES_ADD_LOG_DONE')}"
                        await message.delete()
                    except Exception as e:
                        await interaction.followup.send(f"{self.bot.localisation.get('ANNOUNCE_UPDATES_ADD_LOG_FAIL_1')} {channel.mention} {self.bot.localisation.get('ANNOUNCE_UPDATES_ADD_LOG_FAIL_2')}", ephemeral=True)
                        logger.error(f"{header}{self.bot.localisation.get('ANNOUNCE_UPDATES_ADD_LOG_FAIL_1')} {channel} {self.bot.localisation.get('ANNOUNCE_UPDATES_ADD_LOG_FAIL_2')} {e}")
                        log += f"\n{header}{self.bot.localisation.get('ANNOUNCE_UPDATES_ADD_LOG_FAIL_1')} {channel} {self.bot.localisation.get('ANNOUNCE_UPDATES_ADD_LOG_FAIL_2')} {e}"
                        status = 0
                else:
                    await interaction.followup.send(f"{self.bot.localisation.get('ADMIN_MSG_NO_PERMISSION')}", ephemeral=True)
                    logger.error(f"{header}{self.bot.localisation.get('MODERATOR_LOG_NOT_MOD')}")
                    log += f"\n{header}{self.bot.localisation.get('MODERATOR_LOG_NOT_MOD')}"
                await in_app_logging.send_log(self.bot, log, status, 1, interaction)
            except Exception as e:
                await interaction.followup.send(f"{self.bot.localisation.get('MSG_ERROR_FETCH')} {e}", ephemeral=True)
                logger.info(f"{self.bot.localisation.get('LOG_ERROR_FETCH')} {e}")
                log += f"{self.bot.localisation.get('LOG_ERROR_FETCH')} {e}"
                await in_app_logging.send_log(self.bot, log, 0, 1, interaction)

        self.bot.tree.add_command(announceupdates_add)

        @app_commands.command(name=self.bot.localisation.get('ANNOUNCE_UPDATES_DELETE_CMD_NAME'), description=self.bot.localisation.get('ANNOUNCE_UPDATES_DELETE_CMD_DESC'))
        @app_commands.choices(scope=helpers.load_command_options_scope(self.bot.localisation))
        @app_commands.describe(channel=self.bot.localisation.get('ANNOUNCE_UPDATES_CMD_CHANNEL'), scope=self.bot.localisation.get('ANY_CMD_SCOPE'))
        async def announceupdates_delete(interaction: discord.Interaction, channel: discord.TextChannel, scope: str = None):
            await interaction.response.defer(ephemeral=True)
            try:
                header = self.bot.localisation.get('ANNOUNCE_UPDATES_DELETE_LOG_HEADER')
                logger.info(f"{header}{self.bot.localisation.get('LOG_CMD_TRIGGERED')} /{self.bot.localisation.get('ANNOUNCE_UPDATES_DELETE_CMD_NAME')} channel: {channel} scope: {scope}")
                log = f"{header}{self.bot.localisation.get('LOG_CMD_TRIGGERED')} /{self.bot.localisation.get('ANNOUNCE_UPDATES_DELETE_CMD_NAME')} channel: {channel} scope: {scope}"

                if interaction.user.id == interaction.guild.owner.id or interaction.user.guild_permissions.administrator or interaction.user.id in await helpers.load_json_key("config", "ClientAdminIDs"):
                    logger.info(f"{header}{self.bot.localisation.get('MODERATOR_LOG_IS_MOD')}")
                    log += f"\n{header}{self.bot.localisation.get('MODERATOR_LOG_IS_MOD')}"

                    scope = await str_to_list(scope)

                    try:
                        for scope in scope:
                            await process_request(channel.id, scope, 0)
                            status = 2
                        await interaction.followup.send(f"{self.bot.localisation.get('LOG_THE_CHANNEL')} {channel.mention} {self.bot.localisation.get('ANNOUNCE_UPDATES_REMOVE_LOG_DONE')}", ephemeral=True)
                        logger.info(f"{header}{self.bot.localisation.get('LOG_THE_CHANNEL')} {channel} {self.bot.localisation.get('ANNOUNCE_UPDATES_REMOVE_LOG_DONE')}")
                        log += f"\n{header}{self.bot.localisation.get('LOG_THE_CHANNEL')} {channel} {self.bot.localisation.get('ANNOUNCE_UPDATES_REMOVE_LOG_DONE')}"
                    except Exception as e:
                        await interaction.followup.send(f"{self.bot.localisation.get('ANNOUNCE_UPDATES_REMOVE_LOG_FAIL_1')} {channel.mention} {self.bot.localisation.get('ANNOUNCE_UPDATES_REMOVE_LOG_FAIL_2')}", ephemeral=True)
                        logger.error(f"{header}{self.bot.localisation.get('ANNOUNCE_UPDATES_REMOVE_LOG_FAIL_1')} {channel} {self.bot.localisation.get('ANNOUNCE_UPDATES_REMOVE_LOG_FAIL_2')} {e}")
                        log += f"\n{header}{self.bot.localisation.get('ANNOUNCE_UPDATES_REMOVE_LOG_FAIL_1')} {channel} {self.bot.localisation.get('ANNOUNCE_UPDATES_REMOVE_LOG_FAIL_2')} {e}"
                        status = 0
                else:
                    await interaction.followup.send(f"{self.bot.localisation.get('ADMIN_MSG_NO_PERMISSION')}", ephemeral=True)
                    logger.error(f"{header}{self.bot.localisation.get('MODERATOR_LOG_NOT_MOD')}")
                    log += f"\n{header}{self.bot.localisation.get('MODERATOR_LOG_NOT_MOD')}"
                await in_app_logging.send_log(self.bot, log, status, 1, interaction)
            except Exception as e:
                await interaction.followup.send(f"{self.bot.localisation.get('MSG_ERROR_FETCH')} {e}", ephemeral=True)
                logger.info(f"{self.bot.localisation.get('LOG_ERROR_FETCH')} {e}")
                log += f"{self.bot.localisation.get('LOG_ERROR_FETCH')} {e}"
                await in_app_logging.send_log(self.bot, log, 0, 1, interaction)

        self.bot.tree.add_command(announceupdates_delete)

async def str_to_list(scope):
    scope_list = []
    if scope == "CSR2" or scope == "All":
        scope_list.append("CSR2")
    if scope == "CSR3" or scope == "All":
        scope_list.append("CSR3")
    if scope == "Blog" or scope == "All":
        scope_list.append("Blog")
    if scope == None:
        scope_list = ["CSR2", "CSR3", "Blog"]
    return scope_list

async def process_request(id: str, scope: str, request: int):
    list = await helpers.load_file(f'{scope} announcement channel file')
    if (str(id) in list and request == 0) or (str(id) not in list and request == 1):
        list.remove(str(id)) if request == 0 and str(id) in list else list.append(str(id))
    await helpers.save_file(f"{scope}_announcement_channels", list)

async def setup(bot):
    await bot.add_cog(AnnounceUpdatesCog(bot))
