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
    @app_commands.choices(command=[app_commands.Choice(name="csr2_updatedb", value="updatedb"), app_commands.Choice(name="csr2_addadmin", value="addadmin"), app_commands.Choice(name="csr2_removeadmin", value="removeadmin"), app_commands.Choice(name="csr2_listadmins", value="listadmins")])
    @app_commands.check(is_admin)
    async def admincommands(self, interaction: discord.Interaction, command: str = None):
        # Log the command usage and parameters
        logger.info(f"The following command has been used: /csr2_admincommands commad: {command}")
        log = f"The following command has been used: /csr2_admincommands commad: {command}"

        admins = helpers.load_admins()
        if str(interaction.user.id) in admins:
            await interaction.response.defer(ephemeral=True)

            if command is None:
                command = 'default'

            if command == 'default':
                title_text = 'Available Commands'
            else:
                title_text = 'Command Usage'

            descriptions = {
                'default': '</csr2_updatedb:1296765246958207017>\n</csr2_addadmin:1296764993974439999>\n</csr2_removeadmin:1296764993974440000>\n</csr2_listadmins:1296764993974439998>\n',
                'updatedb': '## </csr2_updatedb:1296765246958207017>\nUpdates the internal DataBase\n',
                'addadmin': '## </csr2_addadmin:1296764993974439999>\nAdditional Operators:\n - user: ping a user and add him to the Bot Admin team\n',
                'removeadmin': '## </csr2_removeadmin:1296764993974440000>\nAdditional Operators:\n - user: ping a user and remove him from the Bot Admin team\n',
                'listadmins': '"## </csr2_listadmins:1296764993974439998>\nAdditional Operators:\n - List all Bot Admins\n'
            }

            description_text = descriptions[command]

            embed = discord.Embed(
                title=title_text,
                 description=description_text,
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
