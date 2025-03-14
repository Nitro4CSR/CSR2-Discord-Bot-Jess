import discord
from discord.ext import commands
from discord import app_commands
import database_manager
import in_app_logging
import helpers

logger = helpers.load_logging()

class DatabaseUpdateCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="csr2_updatedb", description="Manually update the database")
    async def update_db(self, interaction: discord.Interaction):
        logger.info(f"UPDATEDB - The following command has been used: /csr2_updatedb")
        log = f"UPDATEDB - The following command has been used: /csr2_updatedb"
        await interaction.response.defer(ephemeral=True)

        admins = await helpers.load_file('Admin file')
        if str(interaction.user.id) in admins:
            logger.info(f"UPDATEDB - User has permission to run command")
            log += f"\nUPDATEDB - User has permission to run command"
            logger.info(f"UPDATEDB - Starting DB update...")
            log += f"\nUPDATEDB - Starting DB update..."
            await database_manager.recreate_database(self.bot)
            log += f"\nUpdate Success"
            await interaction.followup.send("Database has been updated successfully.", ephemeral=True)
        else:
            logger.info(f"UPDATEDB - Interaction canceled, user lacks permissions...")
            log += f"\nUPDATEDB - Interaction canceled, user lacks permissions..."
            await interaction.followup.send("You do not have permission to use this command.", ephemeral=True)
        await in_app_logging.send_log(self.bot, log, 2, 1, interaction)

async def setup(bot):
    ADMIN_SERVER = await helpers.load_admin_server()
    await bot.add_cog(DatabaseUpdateCog(bot), guilds=[discord.Object(id=int(ADMIN_SERVER))], override=True)
