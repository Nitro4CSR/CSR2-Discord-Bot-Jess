import discord
from discord.ext import commands
from discord import app_commands
import helpers
import in_app_logging

logger = helpers.load_logging()
localisation = dict(helpers.load_localisation())

class ClientInfoCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name=localisation.get('CLIENTINFO_CMD_NAME'), description=localisation.get('CLIENTINFO_CMD_DESC'))
    async def clientinfo(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            header = localisation.get('CLIENTINFO_LOG_HEADER')
            logger.info(f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('CLIENTINFO_CMD_NAME')}")
            log = f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('CLIENTINFO_CMD_NAME')}"

            version = await helpers.load_file('version')

            embed = discord.Embed(
                title=f"{localisation.get('CLIENT_INFO_MSG_EMBED_TITLE')}",
                description=f"### {localisation.get('CLIENT_INFO_MSG_EMBED_DESC_VERSION')} {list(version)[0]}",
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
    await bot.add_cog(ClientInfoCog(bot))