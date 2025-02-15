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
TOKEN = helpers.load_token()
CLIENT_ID = helpers.load_client_id()
NITRO = helpers.load_super_admin()
ADMIN_SERVER = helpers.load_admin_server()

class ConnectedCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="csr2_connected", description="Get the amount of Servers this bot is used in")
    @app_commands.describe(mod="'y' if you want to see which servers exactly use the bot and not just the an integer for the amount of servers")
    async def connected(self, interaction: discord.Interaction, mod: str = None):
        logger.info(f"The following command hs been used: /csr2_connected mod:{mod}")
        log = f"The following command hs been used: /csr2_connected mod:{mod}"
        await interaction.response.defer(ephemeral=True)
        if str(interaction.user.id) == NITRO:
            guildlist = []
            for guild in self.bot.guilds:
                guildlist.append(guild.name + ' (' + str(guild.id) + ')')
            try:
                await interaction.followup.send('Connected Server Count : ' + str(len(self.bot.guilds)))
                if mod == 'y':
                    await interaction.followup.send('\n'.join(guildlist), ephemeral=True)
            except Exception as e: 
                print(e)
            log += f"\nUser is NITRO"
        else:
            await interaction.followup.send(f"You don't have permission to run this command", ephemeral=True)
            log += f"\nUser is not NITRO"
        await in_app_logging.send_log(self.bot, log, interaction)

async def setup(bot):
    await bot.add_cog(ConnectedCog(bot), guilds=[discord.Object(id=ADMIN_SERVER)], override=True)
