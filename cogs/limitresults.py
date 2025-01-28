import asyncio
import discord
from discord.ext import commands
from discord import app_commands
import json
import logging
import os
import in_app_logging
import helpers

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define the path to the JSON file
JSON_FILE_PATH = helpers.load_server_limits()

# Load environment variables from .env file
NITRO = helpers.load_super_admin()

def is_mod(interaction: discord.Interaction):
    if interaction.guild and (interaction.user.guild_permissions.administrator or str(interaction.user.id) == str(NITRO)):
        return interaction.user.id
    return None

class LimitResultsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Helper method to load the JSON data
    def load_json(self):
        if not os.path.exists(JSON_FILE_PATH):
            return {}
        with open(JSON_FILE_PATH, 'r') as file:
            return json.load(file)

    # Helper method to save data to the JSON file
    def save_json(self, data):
        with open(JSON_FILE_PATH, 'w') as file:
            json.dump(data, file, indent=4)

    @commands.Cog.listener()
    async def on_ready(self):
        # Register the slash commands with the bot
        await self.bot.tree.sync()

    @app_commands.command(name="csr2_limitresults", description="Set a limit on the number of results")
    @app_commands.check(is_mod)
    @app_commands.describe(limit="The number of results to limit to (0 = infinite)")
    async def limit_results(self, interaction: discord.Interaction, limit: int):
        # Log the command usage and parameters
        logger.info(f"The following command has been used: /csr2_limitresults limit:{limit}")
        log = f"The following command has been used: /csr2_limitresults limit:{limit}"
        await interaction.response.defer(ephemeral=True)

        # Check if the command is invoked in a guild (server) context
        if interaction.guild is None:
            await interaction.followup.send("This is DMs. There are no Limits here.")
            await in_app_logging.send_log(self.bot, log, interaction)
            return

        # Ensure the limit is non-negative
        if limit < 0:
            limit = 0

        # Load the current limits
        data = self.load_json()

        # Update or add the limit for the current server
        server_id = str(interaction.guild.id)
        if server_id not in data:
            data[server_id] = {"PostLimit": limit}
        else:
            data[server_id]["PostLimit"] = limit

        # Save the updated limits
        self.save_json(data)

        await interaction.followup.send(f"Post limit set to {limit} for this server.", ephemeral=True)
        await in_app_logging.send_log(self.bot, log, interaction)

    @limit_results.error
    async def limit_results_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)

    @app_commands.command(name="csr2_getlimit", description="View the limit on the number of results")
    async def get_limit(self, interaction: discord.Interaction):
        # Log the command usage and parameters
        logger.info(f"The following command has been used: /csr2_getlimit")
        log = f"The following command has been used: /csr2_getlimit"
        await interaction.response.defer(ephemeral=True)
        await asyncio.sleep(1)

        # Check if the command is invoked in a guild (server) context
        if interaction.guild is None:
            await interaction.followup.send("This is DMs. There are no Limits here.")
            await in_app_logging.send_log(self.bot, log, interaction)
            return

        # Load the current limits
        data = self.load_json()
        server_id = str(interaction.guild.id)

        # Fetch the limit for the current server
        limit = data.get(server_id, {"PostLimit": 0})["PostLimit"]

        if limit == 0:
            await interaction.followup.send("The post limit on this server is currently infinite. You can change it with </csr2_limitresults:1266755136114659370> and entering a value.")
        else:
            await interaction.followup.send(f"The post limit on this server is currently **{limit}**. You can change it with </csr2_limitresults:1266755136114659370> and entering a value.")
        await in_app_logging.send_log(self.bot, log, interaction)

async def setup(bot):
    await bot.add_cog(LimitResultsCog(bot))
