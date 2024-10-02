import discord
from discord.ext import commands
from discord import app_commands
import database_manager  # Import the database manager module
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

class DatabaseUpdateCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.admins = helpers.load_admins()

    @app_commands.command(name="csr2_updatedb", description="Manually update the database")
    @app_commands.check(is_admin)
    async def update_db(self, interaction: discord.Interaction):
        # Log the command usage and parameters
        logger.info(f"The following command has been used: /csr2_updatedb")
        log = f"The following command has been used: /csr2_updatedb"
        await interaction.response.defer(ephemeral=True)

        if str(interaction.user.id) in self.admins:
            logger.info(f"User has permission to run command")
            log += f"\nUser has permission to run command"
            logger.info(f"Starting DB update...")
            log += f"\nStarting DB update..."
            database_manager.recreate_database()
            log += f"\nUpdate Success"
            await interaction.followup.send("Database has been updated successfully.", ephemeral=True)
        else:
            logger.info(f"Interaction canceled, user lacks permissions...")
            log += f"\nInteraction canceled, user lacks permissions..."
            await interaction.followup.send("You do not have permission to use this command.", ephemeral=True)
        await in_app_logging.send_log(self.bot, log, interaction)

    @update_db.error
    async def update_db_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(DatabaseUpdateCog(bot), guilds=[discord.Object(id=int(ADMIN_SERVER))])
    await bot.tree.sync(guild=discord.Object(id=int(ADMIN_SERVER)))
