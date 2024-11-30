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
ADMIN_SERVER = helpers.load_admin_server()

class StatusCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="jess_status", description="Change the bot's status if the user is authorized.")
    @app_commands.choices(status_type=[app_commands.Choice(name="playing", value="playing"), app_commands.Choice(name="watching", value="watching"), app_commands.Choice(name="streaming", value="streaming"), app_commands.Choice(name="listening", value="listening")])
    async def jess_status(self, interaction: discord.Interaction, status_type: str, status_text: str, url: str = None):
        logger.info(f"The following command has been used: /jess_status status_type: {status_type} status_text: {status_text} url: {url}")
        log = f"The following command has been used: /jess_status status_type: {status_type} status_text: {status_text} url: {url}"
        if not url:
            url = "https://www.youtube.com/@nitro4csr"
        if str(NITRO) == str(interaction.user.id):
            if status_type.lower() == 'playing':
                await self.bot.change_presence(activity=discord.Game(name=status_text))
                await self.success_message(interaction, log)
            elif status_type.lower() == 'watching':
                await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=status_text))
                await self.success_message(interaction, log)
            elif status_type.lower() == 'streaming':
                await self.bot.change_presence(activity=discord.Streaming(name=status_text, url=url))
                await self.success_message(interaction, log)
            elif status_type.lower() == 'listening':
                await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=status_text))
                await self.success_message(interaction, log)
            else:
                await interaction.response.send_message("You're not the Owner of this bot. You cant run dis command", ephemeral=True)
                return
            
    async def success_message(self, interaction: discord.Interaction, log: str):
        await interaction.response.send_message(f"Successfully changed Presense.", ephemeral=True)
        logger.info(f"Success")
        log += f"\nSuccess"
        await in_app_logging.send_log(self.bot, log, interaction)

async def setup(bot):
    await bot.add_cog(StatusCog(bot), guilds=[discord.Object(id=int(ADMIN_SERVER))])
    await bot.tree.sync(guild=discord.Object(id=int(ADMIN_SERVER)))
