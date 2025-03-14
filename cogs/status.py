import discord
from discord.ext import commands
from discord import app_commands
import in_app_logging
import helpers

logger = helpers.load_logging()

class StatusCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="jess_status", description="Change the bot's status if the user is authorized.")
    @app_commands.choices(status_type=[app_commands.Choice(name="playing", value="playing"), app_commands.Choice(name="watching", value="watching"), app_commands.Choice(name="streaming", value="streaming"), app_commands.Choice(name="listening", value="listening")])
    async def csr2_status(self, interaction: discord.Interaction, status_type: str, status_text: str, url: str = None):
        logger.info(f"STATUS - The following command has been used: /jess_status status_type: {status_type} status_text: {status_text} url: {url}")
        log = f"STATUS - The following command has been used: /jess_status status_type: {status_type} status_text: {status_text} url: {url}"
        NITRO = await helpers.load_super_admin()
        if not url:
            url = "https://www.youtube.com/@nitro4csr"
        if str(NITRO) == str(interaction.user.id):
            if status_type.lower() == 'playing':
                await self.bot.change_presence(activity=discord.Game(name=status_text))
                await success_message(self.bot, interaction, log)
            elif status_type.lower() == 'watching':
                await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=status_text))
                await success_message(self.bot, interaction, log)
            elif status_type.lower() == 'streaming':
                await self.bot.change_presence(activity=discord.Streaming(name=status_text, url=url))
                await success_message(self.bot, interaction, log)
            elif status_type.lower() == 'listening':
                await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=status_text))
                await success_message(self.bot, interaction, log)
            else:
                await interaction.response.send_message("You're not the Owner of this bot. You cant run dis command", ephemeral=True)
                return

async def success_message(bot: commands.Bot, interaction: discord.Interaction, log: str):
    await interaction.response.send_message(f"Successfully changed Presense.", ephemeral=True)
    logger.info(f"STATUS - Success")
    log += f"\nSTATUS - Success"
    await in_app_logging.send_log(bot, log, 2, 1, interaction)

async def setup(bot):
    ADMIN_SERVER = await helpers.load_admin_server()
    await bot.add_cog(StatusCog(bot), guilds=[discord.Object(id=int(ADMIN_SERVER))], override=True)
