import discord
import os
from discord.ext import commands
from discord import app_commands
import helpers
import in_app_logging

logger = helpers.load_logging()

class ClientInfoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="csr2_clientinfo", description="List of all available commands")
    async def commands(self, interaction: discord.Interaction):
        logger.info(f"COMMANDS - The following command has been used: /csr2_clientinfo")
        log = f"COMMANDS - The following command has been used: /csr2_clientinfo"
        await interaction.response.defer()

        version = await helpers.load_file('Version')

        embed = discord.Embed(
            title="Client Info",
            description=f"### Current Source Code Version: {list(version)[0]}",
            color=discord.Color(0xff00ff)
        )
        embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')

        await interaction.followup.send(embed=embed)
        await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
        
async def setup(bot):
    await bot.add_cog(ClientInfoCog(bot))