import discord
from discord.ext import commands
from discord import app_commands
import in_app_logging
import helpers

logger = helpers.load_logging()

class GetLimitCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):

        @app_commands.command(name=self.bot.localisation.get('GETLIMIT_CMD_NAME'), description=self.bot.localisation.get('GETLIMIT_CMD_DESC'))
        @app_commands.describe(scope=self.bot.localisation.get('GETLIMIT_CMD_SCOPE'))
        @app_commands.choices(scope=[app_commands.Choice(name="Server", value="server_limits"), app_commands.Choice(name="Personal", value="user_limits")])
        async def getlimit(interaction: discord.Interaction, scope: str = None):
            await interaction.response.defer(ephemeral=True)
            try:
                header = self.bot.localisation.get('GETLIMIT_LOG_HEADER')
                logger.info(f"{header}{self.bot.localisation.get('LOG_CMD_TRIGGERED')} /{self.bot.localisation.get('GETLIMIT_CMD_NAME')} scope: {scope}")
                log = f"{header}{self.bot.localisation.get('LOG_CMD_TRIGGERED')} /{self.bot.localisation.get('GETLIMIT_CMD_NAME')} scope: {scope}"
                if scope is None:
                    scope = "server_limits" if interaction.guild else "user_limits"
                if scope == "server_limits" and interaction.guild is None:
                    await interaction.followup.send(f"{self.bot.localisation.get('GETLIMIT_MSG_WARNING_SCOPE_GUILD_NO_GUILD')}")
                    return
                id = interaction.guild.id if scope == "server_limits" else interaction.user.id
                limits = await helpers.load_file(scope)
                limit = limits.get(str(id),{"PostLimit": await helpers.load_json_key("config", "DefaultUserLimit" if scope == "user_limits" else "DefaultServerLimit")})["PostLimit"]
                description=f"## {self.bot.localisation.get('GETLIMIT_MSG_EMBED_DESC_LIMIT')} **{limit}**\n\n-# {self.bot.localisation.get('GETLIMIT_MSG_EMBED_DESC_SERVER_1')} </{self.bot.localisation.get('LIMITRESULTS_CMD_NAME')}:{await helpers.load_json_key('session', 'CSR2_LIMITRESULTS_CMD')}>{self.bot.localisation.get('GETLIMIT_MSG_EMBED_DESC_SERVER_2')}" if scope == "server_limits" else f"## {self.bot.localisation.get('GETLIMIT_MSG_EMBED_DESC_LIMIT')} **{limit}**\n\n-# {self.bot.localisation.get('GETLIMIT_MSG_EMBED_DESC_PERSONAL_1')} </{self.bot.localisation.get('LIMITRESULTS_CMD_NAME')}:{await helpers.load_json_key('session', 'CSR2_LIMITRESULTS_CMD')}>{self.bot.localisation.get('GETLIMIT_MSG_EMBED_DESC_PERSONAL_2')}"
                embed = discord.Embed(
                    title=f"{self.bot.localisation.get('GETLIMIT_MSG_EMBED_TITLE')} {interaction.guild.name if scope == "server_limits" else interaction.user.display_name}",
                    description=description,
                    color=discord.Color(0xff00ff)
                )
                embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')
                await interaction.followup.send(embed=embed, ephemeral=True)
                await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
            except Exception as e:
                await interaction.followup.send(f"{self.bot.localisation.get('MSG_ERROR_FETCH')} {e}")
                logger.info(f"{self.bot.localisation.get('LOG_ERROR_FETCH')} {e}")
                log += f"{self.bot.localisation.get('LOG_ERROR_FETCH')} {e}"
                await in_app_logging.send_log(self.bot, log, 0, 1, interaction)

        self.bot.tree.add_command(getlimit)
            
async def setup(bot):
    await bot.add_cog(GetLimitCog(bot))
