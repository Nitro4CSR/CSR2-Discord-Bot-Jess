import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
import in_app_logging
import helpers

logger = helpers.load_logging()

class ExportDBCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="csr2_exportdb", description="Export the internal SQLite 3 DB")
    async def exportDB(self, interaction: discord.Interaction):
        logger.info(f"EXPORTDB - The following command has been used: /csr2_exportdb")
        log = f"EXPORTDB - The following command has been used: /csr2_exportdb"

        admins = await helpers.load_file('Admin file')
        if str(interaction.user.id) in admins:
            await interaction.response.defer(ephemeral=True)

            DB_FILE = await helpers.load_file_path('EDB')
            TUNES_FILE = await helpers.load_file_path('tunes')

            while not os.path.exists(DB_FILE):
                asyncio.sleep(0.2)
            while not os.path.exists(TUNES_FILE):
                asyncio.sleep(0.2)

            files = []
            file = discord.File(DB_FILE, filename="CSR2_Data_SQLite3.db")
            files.append(file)
            file = discord.File(TUNES_FILE, filename="Community_Data_SQLite3.db")
            files.append(file)
            user = interaction.user
            try:
                await user.send(files=files)
                await interaction.followup.send("The Export was sent to you via DMs.", ephemeral=True)
            except discord.Forbidden:
                await interaction.followup.send("DMs are closed or closed for non friended accounts. No records will be send. Please open your DMs and try again.", ephemeral=True)
        else:
            await interaction.response.send_message("You don't have permission to use this command because you are not an Admin of this bot!", ephemeral=True)
        await in_app_logging.send_log(self.bot, log, 2, 1, interaction)

async def setup(bot):
    ADMIN_SERVER = await helpers.load_admin_server()
    await bot.add_cog(ExportDBCog(bot), guilds=[discord.Object(id=ADMIN_SERVER)], override=True)
