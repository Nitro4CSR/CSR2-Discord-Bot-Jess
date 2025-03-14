import discord
from discord.ext import commands
from discord import app_commands
import aiofiles
import json
import in_app_logging
import helpers

logger = helpers.load_logging()

async def save_admins(admins, log):
    """Save admin user IDs to a JSON file."""
    ADMIN_FILE = await helpers.load_file_path('admins')
    try:
        async with aiofiles.open(ADMIN_FILE, mode='w') as f:
            await f.write(json.dumps(list(admins), indent=4))
    except Exception as e:
        logger.error(f"Error saving admin file: {e}")
        log += f"Error saving admin file: {e}"

    return log

class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="csr2_listadmins", description="Lists all registered admins")
    async def list_admins(self, interaction: discord.Interaction):
        logger.info(f"LISTADMIN - The following command has been used: /csr2_listadmins")
        log = f"LISTADMIN - The following command has been used: /csr2_listadmins"

        admins = await helpers.load_file('Admin file')
        if str(interaction.user.id) in admins:
            admin_list = ", ".join([f"<@{admin_id}>" for admin_id in admins])
            await interaction.response.send_message(f"Current admins: {admin_list}", ephemeral=True)
            log += f"\nUser is Admin"
        else:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            log += f"\nUser is not Admin"
        await in_app_logging.send_log(self.bot, log, 2, 1, interaction)

    @app_commands.command(name="csr2_addadmin", description="Manually add a user to the admin list (for development only)")
    @app_commands.describe(user="Mention the user that gets Admin privileges")
    async def add_admin(self, interaction: discord.Interaction, user: discord.User):
        logger.info(f"ADDADMIN - The following command has been used: /csr2_addadmin {user}")
        log = f"ADDADMIN - The following command has been used: /csr2_addadmin {user}"

        admins = await helpers.load_file('Admin file')
        if str(interaction.user.id) in admins:
            admins.add(str(user.id))
            log = await save_admins(admins, log)
            await interaction.response.send_message(f"User {user} has been added as an admin.", ephemeral=True)
            log += f"\nADDADMIN - User is Admin"
        else:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            log += f"\nADDADMIN - User is not Admin"
        await in_app_logging.send_log(self.bot, log, 2, 1, interaction)

    @app_commands.command(name="csr2_removeadmin", description="Manually remove a user from the admin list (for development only)")
    @app_commands.describe(user="Mention the user that gets taken his Admin privileges")
    async def remove_admin(self, interaction: discord.Interaction, user: discord.User):
        logger.info(f"REMOVEADMIN - The following command has been used: /csr2_removeadmin {user}")
        log = f"REMOVEADMIN - The following command has been used: /csr2_removeadmin {user}"

        admins = await helpers.load_file('Admin file')
        if str(interaction.user.id) in admins:
            if str(user.id) in admins:
                admins.remove(str(user.id))
                log = await save_admins(admins, log)
                await interaction.response.send_message(f"User {user} has been removed from the admin list.", ephemeral=True)
            else:
                await interaction.response.send_message(f"User {user} is not in the admin list.", ephemeral=True)
            log += f"\nREMOVEADMIN - User is Admin"
        else:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            log += f"\nREMOVEADMIN - User is not Admin"
        await in_app_logging.send_log(self.bot, log, 2, 1, interaction)

async def setup(bot):
    ADMIN_SERVER = await helpers.load_admin_server()
    await bot.add_cog(AdminCog(bot), guilds=[discord.Object(id=int(ADMIN_SERVER))], override=True)
