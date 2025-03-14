import discord
import os
from discord.ext import commands
from discord import app_commands
import in_app_logging
import helpers

# Configure logging
logger = helpers.load_logging()

class ModcommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="csr2_modcommands", description="List of all available commands")
    @app_commands.choices(command=[app_commands.Choice(name='csr2_limitresults', value='limitresults'), app_commands.Choice(name='csr2_announce_updates_add', value='announce_updates_add'), app_commands.Choice(name='csr2_announce_updates_delete', value='announce_updates_delete')])
    async def modcommands(self, interaction: discord.Interaction, command: str = None):
        logger.info(f"MODCOMMANDS - The following command has been used: /csr2_modcommands commad: {command}")
        log = f"MODCOMMANDS - The following command has been used: /csr2_modcommands commad: {command}"

        NITRO = await helpers.load_super_admin()
        if interaction.user.guild_permissions.administrator or str(interaction.user.id) == str(NITRO):
            await interaction.response.defer()

            helpers.load_dotenv

            if command is None:
                command = 'default'

            if command == 'default':
                title_text = 'Available Commands'
            else:
                title_text = 'Command Usage'

            descriptions = {
                'default': f'</csr2_limitresults:{os.getenv('CSR2_LIMITRESULTS_COMMAND')}>\n</csr2_announce_updates_add:{os.getenv('CSR2_ANNOUNCE_UPDATES_ADD_COMMAND')}>\n</csr2_announce_updates_delete:{os.getenv('CSR2_ANNOUNCE_UPDATES_DELETE_COMMAND')}>\n',
                'limitresults': f'## </csr2_limitresults:{os.getenv('CSR2_LIMITRESULTS_COMMAND')}>\nAdditional operators:\n- limit: Accepts integers.\n',
                'announce_updates_add': f'## </csr2_announce_updates_add:{os.getenv('CSR2_ANNOUNCE_UPDATES_ADD_COMMAND')}>\nAdditional operators:\n- channel: any text-channel is selectable\n- scope: Defaults to "All". Available: CSR2, CSR3, Blog & All (optional)\n',
                'announce_updates_delete': f'## </csr2_announce_updates_delete:{os.getenv('CSR2_ANNOUNCE_UPDATES_DELETE_COMMAND')}>\nAdditional operators:\n- channel: any text-channel is selectable\n- scope: Defaults to "All". Available: CSR2, CSR3, Blog & All (optional)\n',
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
        await in_app_logging.send_log(self.bot, log, 2, 1, interaction)

async def setup(bot):
    await bot.add_cog(ModcommandsCog(bot))
