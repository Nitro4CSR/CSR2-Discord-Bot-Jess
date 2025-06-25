import discord
import os
from discord.ext import commands
from discord import app_commands
import in_app_logging
import helpers

logger = helpers.load_logging()

class AdminCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="csr2_admincommands", description="List of all available commands")
    @app_commands.choices(command=[app_commands.Choice(name="csr2_updatedb", value="updatedb"), app_commands.Choice(name="csr2_addadmin", value="addadmin"), app_commands.Choice(name="csr2_removeadmin", value="removeadmin"), app_commands.Choice(name="csr2_listadmins", value="listadmins"), app_commands.Choice(name="csr2_connected", value="connected"), app_commands.Choice(name="csr2_scrape", value="scrape"), app_commands.Choice(name="csr2_broadcast", value="broadcast"), app_commands.Choice(name="csr2_updatecode", value="updatecode"), app_commands.Choice(name="csr2_restart", value="restart")])
    async def admincommands(self, interaction: discord.Interaction, command: str = None):
        logger.info(f"ADMINCOMMANDS - The following command has been used: /csr2_admincommands commad: {command}")
        log = f"ADMINCOMMANDS - The following command has been used: /csr2_admincommands commad: {command}"

        admins = await helpers.load_file('Admin file')
        helpers.load_dotenv
        if str(interaction.user.id) in admins or str(interaction.user.id) == str(await helpers.load_super_admin()):
            await interaction.response.defer(ephemeral=True)

            if command is None:
                command = 'default'

            if command == 'default':
                title_text = 'Available Commands'
            else:
                title_text = 'Command Usage'

            descriptions = {
                "default": f"</csr2_updatedb:{os.getenv('CSR2_UPDATEDB_COMMAND')}>\n</csr2_addadmin:{os.getenv('CSR2_ADDADMIN_COMMAND')}>\n</csr2_removeadmin:{os.getenv('CSR2_REMOVEADMIN_COMMAND')}>\n</csr2_listadmins:{os.getenv('CSR2_LISTADMINS_COMMAND')}>\n</csr2_connected:{os.getenv('CSR2_CONNECTED_COMMAND')}>\n</csr2_scrape:{os.getenv('CSR2_SCRAPE_COMMAND')}>\n</csr2_broadcast:{os.getenv('CSR2_BROADCAST_COMMAND')}>\n</csr2_updatecode:{os.getenv('CSR2_UPDATECODE_COMMAND')}>\n</csr2_restart:{os.getenv('CSR2_RESTART_COMMAND')}>\n",
                "updatedb": f"## </csr2_updatedb:{os.getenv('CSR2_UPDATEDB_COMMAND')}>\nUpdates the internal DataBase\n",
                "addadmin": f"## </csr2_addadmin:{os.getenv('CSR2_ADDADMIN_COMMAND')}>\nAdditional Operators:\n - user: ping a user and add him to the Bot Admin team\n",
                "removeadmin": f"## </csr2_removeadmin:{os.getenv('CSR2_REMOVEADMIN_COMMAND')}>\nAdditional Operators:\n - user: ping a user and remove him from the Bot Admin team\n",
                "listadmins": f"## </csr2_listadmins:{os.getenv('CSR2_LISTADMINS_COMMAND')}>\nAdditional Operators:\n - List all Bot Admins\n",
                "connected": f"## </csr2_connected:{os.getenv('CSR2_CONNECTED_COMMAND')}>\nAdditional Operators:\n - mod: `y` to see all server names and IDs\n",
                "scrape": f"## </csr2_scrape:{os.getenv('CSR2_SCRAPE_COMMAND')}>\nScrape the appstores for CSR2 and CSR3 app updates\n",
                "broadcast": f"## </csr2_broadcast:{os.getenv('CSR2_BROADCAST_COMMAND')}>\nAdditional Operators:\n - message_title: title of the broadcasted embed message\n - You will be asked to send a text message containing the containing the messages text body that will be broadcasted.",
                "updatecode": f"## </csr2_updatecode:{os.getenv('CSR2_UPDATECODE_COMMAND')}>\nAdditional Operators:\n - restart_in: Delay time in hours until the bot auto restarts after the code update, format: `X.XX...`",
                "restart": f"</csr2_restart:{os.getenv('CSR2_RESTART_COMMAND')}>\nRestarts the bot"
            }

            description_text = descriptions[command]

            embed = discord.Embed(
                title=title_text,
                 description=description_text,
                color=discord.Color(0xff00ff)
            )
            embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')

            await interaction.followup.send(embed=embed, ephemeral=True)
            log += f"\nADMINCOMMANDS - User is Admin"
        else:
            await interaction.response.send_message("You don't have permission to use this command because you are not an Admin of this bot!", ephemeral=True)
            log += f"\nADMINCOMMANDS - User is not Admin"
        await in_app_logging.send_log(self.bot, log, 2, 1, interaction)

async def setup(bot):
    ADMIN_SERVER = await helpers.load_admin_server()
    await bot.add_cog(AdminCommandsCog(bot), guilds=[discord.Object(id=int(ADMIN_SERVER))], override=True)
