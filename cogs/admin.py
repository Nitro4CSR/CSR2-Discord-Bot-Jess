import discord
from discord.ext import commands
from discord import app_commands
import json
import logging
import in_app_logging
import helpers

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Determine the base directory (project root)
# File to store admin list
ADMIN_FILE = helpers.load_admin_file()
ADMIN_SERVER = helpers.load_admin_server()

def save_admins(admins):
    """Save admin user IDs to a JSON file."""
    try:
        with open(ADMIN_FILE, 'w') as f:
            json.dump(list(admins), f)
    except Exception as e:
        logger.error(f"Error saving admin file: {e}")
        log =+ f"Error saving admin file: {e}"

admins = helpers.load_admins()

def is_admin(interaction: discord.Interaction):
    if str(interaction.user.id) in admins:
        return interaction.user.id

class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.admins = helpers.load_admins()

    @app_commands.command(name="csr2_listadmins", description="Lists all registered admins")
    @app_commands.check(is_admin)
    async def list_admins(self, interaction: discord.Interaction):
        # Log the command usage and parameters
        logger.info(f"The following command has been used: /csr2_listadmins")
        log = f"The following command has been used: /csr2_listadmins"
        if str(interaction.user.id) in self.admins:
            admin_list = ", ".join([f"<@{admin_id}>" for admin_id in self.admins])
            await interaction.response.send_message(f"Current admins: {admin_list}")
            log += f"\nUser is Admin"
        else:
            await interaction.response.send_message("You do not have permission to use this command.")
            log += f"\nUser is not Admin"
        await in_app_logging.send_log(self.bot, log, interaction)

    @list_admins.error
    async def list_admins_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)

    @app_commands.command(name="csr2_addadmin", description="Manually add a user to the admin list (for development only)")
    @app_commands.check(is_admin)
    @app_commands.describe(user="Mention the user that gets Admin privileges")
    async def add_admin(self, interaction: discord.Interaction, user: discord.User):
        # Log the command usage and parameters
        logger.info(f"The following command has been used: /csr2_addadmin {user}")
        log = f"The following command has been used: /csr2_addadmin {user}"
        if str(interaction.user.id) in self.admins:  # Only bot owner can use this command
            self.admins.add(str(user.id))  # Convert to string
            save_admins(self.admins)
            await interaction.response.send_message(f"User {user} has been added as an admin.")
            log += f"\nUser is Admin"
        else:
            await interaction.response.send_message("You do not have permission to use this command.")
            log += f"\nUser is not Admin"
        await in_app_logging.send_log(self.bot, log, interaction)

    @add_admin.error
    async def add_admin_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)

    @app_commands.command(name="csr2_removeadmin", description="Manually remove a user from the admin list (for development only)")
    @app_commands.check(is_admin)
    @app_commands.describe(user="Mention the user that gets taken his Admin privileges")
    async def remove_admin(self, interaction: discord.Interaction, user: discord.User):
        # Log the command usage and parameters
        logger.info(f"The following command has been used: /csr2_removeadmin {user}")
        log = f"The following command has been used: /csr2_removeadmin {user}"
        if str(interaction.user.id) in self.admins:  # Only bot owner can use this command
            if str(user.id) in self.admins:  # Convert to string
                self.admins.remove(str(user.id))  # Convert to string
                save_admins(self.admins)
                await interaction.response.send_message(f"User {user} has been removed from the admin list.")
            else:
                await interaction.response.send_message(f"User {user} is not in the admin list.")
            log += f"\nUser is Admin"
        else:
            await interaction.response.send_message("You do not have permission to use this command.")
            log += f"\nUser is not Admin"
        await in_app_logging.send_log(self.bot, log, interaction)

    @remove_admin.error
    async def remove_admin_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AdminCog(bot), guilds=[discord.Object(id=int(ADMIN_SERVER))], override=True)
