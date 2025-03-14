import discord
from discord.ext import commands
from discord import app_commands
import aiofiles
import json
import os
import in_app_logging
import helpers

logger = helpers.load_logging()

class LimitResultsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="csr2_limitresults", description="Set a limit on the number of results")
    @app_commands.describe(limit="The number of results to limit to (0 = infinite)")
    async def limit_results(self, interaction: discord.Interaction, limit: int):
        logger.info(f"LIMITRESULTS - The following command has been used: /csr2_limitresults limit:{limit}")
        log = f"LIMITRESULTS - The following command has been used: /csr2_limitresults limit:{limit}"
        await interaction.response.defer(ephemeral=True)

        if interaction.guild is None:
            await interaction.followup.send("This is DMs. There are no Limits here.")
            await in_app_logging.send_log(self.bot, log, interaction)
            return

        NITRO = await helpers.load_super_admin()    
        if interaction.user.guild_permissions.administrator or str(interaction.user.id) == str(NITRO):
            if limit < 0:
                limit = 0

            data = await load_limits()

            server_id = str(interaction.guild.id)
            if server_id not in data:
                data[server_id] = {"PostLimit": limit}
            else:
                data[server_id]["PostLimit"] = limit

            await save_limits(data)

            if limit == 0:
                limit = "∞"

            embed=discord.Embed(
                title=f"New Results limit on {interaction.guild.name}",
                description=f"## New Limit: {limit}",
                color=discord.Color(0xff00ff)
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        await in_app_logging.send_log(self.bot, log, 2, 1, interaction)

    @app_commands.command(name="csr2_getlimit", description="View the limit on the number of results")
    async def get_limit(self, interaction: discord.Interaction):
        logger.info(f"GETLIMIT - The following command has been used: /csr2_getlimit")
        log = f"GETLIMIT - The following command has been used: /csr2_getlimit"
        await interaction.response.defer(ephemeral=True)

        if interaction.guild is None:
            await interaction.followup.send("This is DMs. There are no Limits here.")
            await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
            return

        data = await load_limits()
        server_id = str(interaction.guild.id)

        limit = data.get(server_id, {"PostLimit": 0})["PostLimit"]

        if limit == 0:
            description=f"## Current limit: **∞**\n\n-# A moderator of this server can change it by </csr2_limitresults:1266755136114659370> and entering a value."
        else:
            description=f"## Current limit: **{limit}**\n\n-# A moderator of this server can change it by </csr2_limitresults:1266755136114659370> and entering a value."

        embed = discord.Embed(
                title=f"Results limit on {interaction.guild.name}",
                description=description,
                color=discord.Color(0xff00ff)
        )
        embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')

        await interaction.followup.send(embed=embed, ephemeral=True)
        await in_app_logging.send_log(self.bot, log, 2, 1, interaction)

async def load_limits():
    JSON_FILE_PATH =await helpers.load_file_path('limits')
    if not os.path.exists(JSON_FILE_PATH):
        return {}
    async with aiofiles.open(JSON_FILE_PATH, 'r') as file:
        content = await file.read()
        return json.loads(content)

async def save_limits(data):
    JSON_FILE_PATH =await helpers.load_file_path('limits')
    async with aiofiles.open(JSON_FILE_PATH, 'w') as file:
        await file.write(json.dumps(data, indent=4))

async def setup(bot):
    await bot.add_cog(LimitResultsCog(bot))
