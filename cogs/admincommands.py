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

ADMIN_SERVER = helpers.load_admin_server()

admins = helpers.load_admins()

def is_admin(interaction: discord.Interaction):
    if str(interaction.user.id) in admins:
        return interaction.user.id
    
class AdmincommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="csr2_admincommands", description="List of all available commands")
    @app_commands.check(is_admin)
    async def admincommands(self, interaction: discord.Interaction):
        # Log the command usage and parameters
        logger.info(f"The following command has been used: /csr2_admincommands")
        log = f"The following command has been used: /csr2_admincommands"

        admins = helpers.load_admins()
        if str(interaction.user.id) in admins:
            await interaction.response.defer(ephemeral=True)

            embed = discord.Embed(
                title="Available Admin Commands",
                 description=(
                    f"## </csr2_updatedb:1265025856539983888>\nUpdates the internal DataBase\n"
                    f"## </csr2_addadmin:1266756642100346975>\nAdditional Operators:\n - user: ping a user and add him to the Bot Admin team\n"
                    f"## </csr2_removeadmin:1265025856539983885>\nAdditional Operators:\n - user: ping a user and remove him from the Bot Admin team\n"
                    f"## </csr2_listadmins:1265025856539983883>\nAdditional Operators:\n - List all Bot Admins\n"
                ),
                color=discord.Color(0xff00ff)
            )
            embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')
        
            await interaction.followup.send(embed=embed, ephemeral=True)
            log += f"\nUser is Admin"
        else:
            await interaction.response.send_message("You don't have permission to use this command because you are not an Admin of this bot!", ephemeral=True)
            log += f"\nUser is not Admin"
        await in_app_logging.send_log(self.bot, log, interaction)

    @admincommands.error
    async def admincommands_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AdmincommandsCog(bot), guilds=[discord.Object(id=int(ADMIN_SERVER))])
    await bot.tree.sync(guild=discord.Object(id=int(ADMIN_SERVER)))
