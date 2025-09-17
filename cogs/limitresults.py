import discord
from discord.ext import commands
from discord import app_commands
import in_app_logging
import helpers

logger = helpers.load_logging()
localisation = dict(helpers.load_localisation())

class LimitResultsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name=localisation.get('LIMITRESULTS_CMD_NAME'), description=localisation.get("LIMITRESULTS_CMD_DESC"))
    @app_commands.describe(limit=localisation.get('LIMITRESULTS_CMD_LIMIT'), scope=localisation.get('LIMITRESULTS_CMD_SCOPE'))
    @app_commands.choices(scope=[app_commands.Choice(name=localisation.get('LIMIT_CMD_SCOPE_OPTION_SERVER'), value="server_limits"), app_commands.Choice(name=localisation.get('LIMIT_CMD_SCOPE_OPTION_PERSONAL'), value="user_limits")])
    async def limitresults(self, interaction: discord.Interaction, limit: int, scope: str = None):
        await interaction.response.defer(ephemeral=True)
        try:
            header = localisation.get('LIMITRESULTS_LOG_HEADER')
            logger.info(f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('LIMITRESULTS_CMD_NAME')} limit:{limit} scope: {scope}")
            log = f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('LIMITRESULTS_CMD_NAME')} limit:{limit} scope: {scope}"
            if scope is None:
                scope = "server_limits" if interaction.guild else "user_limits"
            if scope == "server_limits":
                if interaction.guild is None:
                    await interaction.followup.send(f"{localisation.get('LIMITRESULTS_MSG_NOTICE_DMS')}")
                    await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
                    return
                admins = await helpers.load_file('Admin file')
                if interaction.user.id != interaction.guild.owner.id and interaction.user.guild_permissions.administrator == False and str(interaction.user.id) not in admins and int(interaction.user.id) not in await helpers.load_json_key("config", "ClientAdminIDs"):
                    await interaction.followup.send(f"{localisation.get('LIMITRESULTS_MSG_NO_PERMISSION')}", ephemeral=True)
                    await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
                    return
                id = interaction.guild.id
            else:
                id = interaction.user.id
            limits = await helpers.load_file(scope)
            if str(id) not in limits:
                if limit != -1:
                    limits[str(id)] = {"PostLimit": limit}
            else:
                if limit == -1:
                    limits.pop(str(id))
                else:
                    limits[str(id)]["PostLimit"] = limit
            await helpers.save_file(scope, limits)
            embed=discord.Embed(
                title=f"{localisation.get('LIMITRESULTS_MSG_EMBED_TITLE')} {interaction.guild.name if scope == "server_limits" else interaction.user.display_name}",
                description=f"## {localisation.get('LIMITRESULTS_MSG_EMBED_DESC')} {limit}",
                color=discord.Color(0xff00ff)
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
        except Exception as e:
            await interaction.followup.send(f"{localisation.get('MSG_ERROR_FETCH')} {e}")
            logger.info(f"{localisation.get('LOG_ERROR_FETCH')} {e}")
            log += f"{localisation.get('LOG_ERROR_FETCH')} {e}"
            await in_app_logging.send_log(self.bot, log, 0, 1, interaction)

async def setup(bot):
    await bot.add_cog(LimitResultsCog(bot))
