import discord
from discord.ext import commands
from discord import app_commands
import os
import logging
import in_app_logging
import helpers

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file
NITRO = helpers.load_super_admin()

def is_mod(interaction: discord.Interaction):
    if ((interaction.user.guild_permissions.administrator) or (str(interaction.user.id) == str(NITRO))):
        return interaction.user.id
    else:
        return None

class ModcommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name="csr2_modcommands", description="List of all available commands")
    @app_commands.choices(command=[app_commands.Choice(name='csr2_limitresults', value='limitresults')])
    @app_commands.check(is_mod)
    async def modcommands(self, interaction: discord.Interaction, command: str = None):
        # Log the command usage and parameters
        logger.info(f"The following command has been used: /csr2_modcommands commad: {command}")
        log = f"The following command has been used: /csr2_modcommands commad: {command}"
        
        if interaction.user.guild_permissions.administrator or str(interaction.user.id) == str(NITRO):
            await interaction.response.defer()

            if command is None:
                command = 'default'

            if command == 'default':
                title_text = 'Available Commands'
            else:
                title_text = 'Command Usage'

            descriptions = {
                'default': '</csr2_limitresults:1266755136114659370>\n',
                'limitresults': '## </csr2_limitresults:1266755136114659370>\nAdditional operators:\n- limit: Accepts integers.\n'
            }

            description_text = descriptions[command]

            embed = discord.Embed(
                title=title_text,
                description=description_text,
                color=discord.Color(0xff00ff)
            )
            embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')
        
            await interaction.followup.send(embed=embed)
        else:
            await interaction.response.send_message("You don't have permission to use this command on this server!", ephemeral=True)
        await in_app_logging.send_log(self.bot, log, interaction)

async def setup(bot):
    await bot.add_cog(ModcommandsCog(bot))
