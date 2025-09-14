import discord
from discord.ext import commands
from discord import app_commands
import helpers
import in_app_logging

logger = helpers.load_logging()

class ClientInfoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):

        @app_commands.command(name=self.bot.localisation.get('CLIENTINFO_CMD_NAME'), description=self.bot.localisation.get('CLIENTINFO_CMD_DESC'))
        async def clientinfo(interaction: discord.Interaction):
            await interaction.response.defer()
            try:
                header = self.bot.localisation.get('CLIENTINFO_LOG_HEADER')
                logger.info(f"{header}{self.bot.localisation.get('LOG_CMD_TRIGGERED')} /{self.bot.localisation.get('CLIENTINFO_CMD_NAME')}")
                log = f"{header}{self.bot.localisation.get('LOG_CMD_TRIGGERED')} /{self.bot.localisation.get('CLIENTINFO_CMD_NAME')}"

                version = await helpers.load_file('version')

                embed = discord.Embed(
                    title=f"{self.bot.localisation.get('CLIENT_INFO_MSG_EMBED_TITLE')}",
                    description=f"### {self.bot.localisation.get('CLIENT_INFO_MSG_EMBED_DESC_VERSION')} {list(version)[0]}",
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
        
        self.bot.tree.add_command(clientinfo)
        
async def setup(bot):
    await bot.add_cog(ClientInfoCog(bot))