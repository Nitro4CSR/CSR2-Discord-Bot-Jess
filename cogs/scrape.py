import discord
from discord.ext import commands
from discord import app_commands
import version_check_manager_CSR2
import version_check_manager_CSR3
import logging
import in_app_logging
import helpers

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# File to store admin list
ADMIN_FILE = helpers.load_super_admin
ADMIN_SERVER = helpers.load_admin_server()

admins = helpers.load_admins()

def is_admin(interaction: discord.Interaction):
    if str(interaction.user.id) in admins:
        return interaction.user.id

class ScrapeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.admins = helpers.load_admins()

    @app_commands.command(name="csr2_scrape", description="Manually scrape for Store Updates")
    @app_commands.check(is_admin)
    async def scrape(self, interaction: discord.Interaction):
        # Log the command usage and parameters
        logger.info(f"The following command has been used: /csr2_scrape")
        log = f"The following command has been used: /scrape"
        await interaction.response.defer(ephemeral=True)

        if str(interaction.user.id) in self.admins:
            logger.info(f"User has permission to run command")
            log += f"\nUser has permission to run command"
            logger.info(f"Starting Scrape...")
            log += f"\nStarting Scrape..."
            await interaction.followup.send("Starting Scrape...", ephemeral=True)
            await version_check_manager_CSR2.version_check_task(self.bot)
            await version_check_manager_CSR3.version_check_task(self.bot)
            log += f"\nScrape Success"
            await interaction.followup.send("Scraped successfully.", ephemeral=True)
        else:
            logger.info(f"Interaction canceled, user lacks permissions...")
            log += f"\nInteraction canceled, user lacks permissions..."
            await interaction.followup.send("You do not have permission to use this command.", ephemeral=True)
        await in_app_logging.send_log(self.bot, log, interaction)

    @scrape.error
    async def update_db_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ScrapeCog(bot), guilds=[discord.Object(id=int(ADMIN_SERVER))], override=True)
