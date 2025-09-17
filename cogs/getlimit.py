import discord
from discord.ext import commands
from discord import app_commands
import in_app_logging
import helpers

logger = helpers.load_logging()
localisation = dict(helpers.load_localisation())

class GetLimitCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name=localisation.get('GETLIMIT_CMD_NAME'), description=localisation.get('GETLIMIT_CMD_DESC'))
    @app_commands.describe(scope=localisation.get('GETLIMIT_CMD_SCOPE'))
    @app_commands.choices(scope=[app_commands.Choice(name=localisation.get('LIMIT_CMD_SCOPE_OPTION_SERVER'), value="server_limits"), app_commands.Choice(name=localisation.get('LIMIT_CMD_SCOPE_OPTION_PERSONAL'), value="user_limits")])
    async def getlimit(self, interaction: discord.Interaction, scope: str = None):
        await interaction.response.defer(ephemeral=True)
        try:
            header = localisation.get('GETLIMIT_LOG_HEADER')
            logger.info(f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('GETLIMIT_CMD_NAME')} scope: {scope}")
            log = f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('GETLIMIT_CMD_NAME')} scope: {scope}"
            if scope is None:
                scope = "server_limits" if interaction.guild else "user_limits"
            if scope == "server_limits" and interaction.guild is None:
                await interaction.followup.send(f"{localisation.get('GETLIMIT_MSG_WARNING_SCOPE_GUILD_NO_GUILD')}")
                return
            id = interaction.guild.id if scope == "server_limits" else interaction.user.id
            limits = await helpers.load_file(scope)
            limit = limits.get(str(id),{"PostLimit": await helpers.load_json_key("config", "DefaultUserLimit" if scope == "user_limits" else "DefaultServerLimit")})["PostLimit"]
            description=f"## {localisation.get('GETLIMIT_MSG_EMBED_DESC_LIMIT')} **{limit}**\n\n-# {localisation.get('GETLIMIT_MSG_EMBED_DESC_SERVER_1')} </{localisation.get('LIMITRESULTS_CMD_NAME')}:{await helpers.load_json_key('session', 'CSR2_LIMITRESULTS_CMD')}>{localisation.get('GETLIMIT_MSG_EMBED_DESC_SERVER_2')}" if scope == "server_limits" else f"## {localisation.get('GETLIMIT_MSG_EMBED_DESC_LIMIT')} **{limit}**\n\n-# {localisation.get('GETLIMIT_MSG_EMBED_DESC_PERSONAL_1')} </{localisation.get('LIMITRESULTS_CMD_NAME')}:{await helpers.load_json_key('session', 'CSR2_LIMITRESULTS_CMD')}>{localisation.get('GETLIMIT_MSG_EMBED_DESC_PERSONAL_2')}"
            embed = discord.Embed(
                title=f"{localisation.get('GETLIMIT_MSG_EMBED_TITLE')} {interaction.guild.name if scope == "server_limits" else interaction.user.display_name}",
                description=description,
                color=discord.Color(0xff00ff)
            )
            embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')
            await interaction.followup.send(embed=embed, ephemeral=True)
            await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
        except Exception as e:
            await interaction.followup.send(f"{localisation.get('MSG_ERROR_FETCH')} {e}")
            logger.info(f"{localisation.get('LOG_ERROR_FETCH')} {e}")
            log += f"{localisation.get('LOG_ERROR_FETCH')} {e}"
            await in_app_logging.send_log(self.bot, log, 0, 1, interaction)

async def setup(bot):
    await bot.add_cog(GetLimitCog(bot))
