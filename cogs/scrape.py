import discord
from discord.ext import commands
from discord import app_commands
import version_check_manager_apps
import version_check_manager_blog
import in_app_logging
import helpers

logger = helpers.load_logging()

class ScrapeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="csr2_scrape", description="Manually scrape for Store Updates")
    async def scrape(self, interaction: discord.Interaction):
        logger.info(f"SCRAPE - The following command has been used: /csr2_scrape")
        log = f"SCRAPE - The following command has been used: /scrape"
        await interaction.response.defer(ephemeral=True)

        admins = await helpers.load_file('Admin file')
        if str(interaction.user.id) in admins:
            logger.info(f"User has permission to run command")
            log += f"\nUser has permission to run command"
            logger.info(f"Starting Scrape...")
            log += f"\nStarting Scrape..."
            msg = await interaction.followup.send("Starting Blog Scrape...", ephemeral=True)
            await version_check_manager_blog.version_check_task(self.bot)
            await interaction.followup.edit_message(content="Blog Scrape done, starting Store scrapes for Apps...", message_id=msg.id)
            await version_check_manager_apps.version_check_task(self.bot)
            await interaction.followup.edit_message(content="All Scrapes were successful", message_id=msg.id)
            log += f"\nScrape Success"
        else:
            logger.info(f"SCRAPE - Interaction canceled, user lacks permissions...")
            log += f"\nSCRAPE - Interaction canceled, user lacks permissions..."
            await interaction.followup.send("You do not have permission to use this command.", ephemeral=True)
        await in_app_logging.send_log(self.bot, log, 2, 1, interaction)

async def setup(bot):
    ADMIN_SERVER = await helpers.load_admin_server()
    await bot.add_cog(ScrapeCog(bot), guilds=[discord.Object(id=int(ADMIN_SERVER))], override=True)
