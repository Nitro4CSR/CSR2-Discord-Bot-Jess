import discord
from discord.ext import commands
from discord import app_commands
import logging
import in_app_logging
import helpers

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file
NITRO = helpers.load_super_admin()

# Define the path to the JSON file
ADMIN_FILE = helpers.load_admin_file()
DB_FILE = helpers.load_external_db
TUNES_FILE = helpers.load_community_db()

admins = helpers.load_admins()

def is_admin(interaction: discord.Interaction):
    if str(interaction.user.id) in admins:
        return interaction.user.id

class exportDBCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="csr2_exportdb", description="Export the internal SQLite 3 DB")
    @app_commands.check(is_admin)
    async def exportDB(self, interaction: discord.Interaction):
        # Log the command usage and parameters
        logger.info(f"The following command has been used: /csr2_exportdb")
        log = f"The following command has been used: /csr2_exportdb"

        admins = helpers.load_admins()
        if str(interaction.user.id) in admins:
            await interaction.response.defer(ephemeral=True)
            files = []
            file = discord.File(DB_FILE, filename="CSR2_Data_SQLite3.db")
            files.append(file)
            file = discord.File(TUNES_FILE, filename="Community_Data_SQLite3.db")
            files.append(file)
            user = interaction.user
            try:
                await user.send(files=files)
                await interaction.followup.send("The Export was sent to you via DMs.", ephemeral=True)
            except discord.Forbidden:
                await interaction.followup.send("DMs are closed or closed for non friended accounts. No records will be send. Please open your DMs and try again.", ephemeral=True)
        else:
            await interaction.response.send_message("You don't have permission to use this command because you are not an Admin of this bot!", ephemeral=True)
        await in_app_logging.send_log(self.bot, log, interaction)

    @exportDB.error
    async def exportDB_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(exportDBCog(bot), guilds=[discord.Object(id=911297387765567498)])