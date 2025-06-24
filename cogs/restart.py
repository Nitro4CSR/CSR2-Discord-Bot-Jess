import discord
from discord.ext import commands
from discord import app_commands
import in_app_logging
import helpers

logger = helpers.load_logging()

class RestartCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="csr2_restart", description="Manually restart the bot")
    async def update_db(self, interaction: discord.Interaction):
        logger.info(f"RESTART - The following command has been used: /csr2_restart")
        log = f"RESTART - The following command has been used: /csr2_restart"
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("Restarting...", ephemeral=True)
        await helpers.restart()
        await in_app_logging.send_log(self.bot, log, 2, 1, interaction)

async def setup(bot):
    ADMIN_SERVER = await helpers.load_admin_server()
    await bot.add_cog(RestartCog(bot), guilds=[discord.Object(id=int(ADMIN_SERVER))], override=True)