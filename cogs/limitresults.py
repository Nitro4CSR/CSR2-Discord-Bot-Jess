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
    @app_commands.choices(scope=[app_commands.Choice(name="Server", value="server_limits"), app_commands.Choice(name="Personal", value="user_limits")])
    async def limit_results(self, interaction: discord.Interaction, limit: int, scope: str):
        logger.info(f"LIMITRESULTS - The following command has been used: /csr2_limitresults limit:{limit} scope: {scope}")
        log = f"LIMITRESULTS - The following command has been used: /csr2_limitresults limit:{limit} scope: {scope}"
        await interaction.response.defer(ephemeral=True)

        if scope == "server_limits":
            if interaction.guild is None:
                await interaction.followup.send("This is DMs. You can't set a server limit here.")
                await in_app_logging.send_log(self.bot, log, interaction)
                return
            NITRO = await helpers.load_super_admin()
            if interaction.user.id != interaction.guild.owner.id or interaction.user.guild_permissions.administrator == False or str(interaction.user.id) != str(NITRO):
                await interaction.followup.send("You do not have permission to use this command with the scope `Server` in the server.", ephemeral=True)
                return
            await set_limit(interaction, interaction.guild.id, scope, limit)
        else:
            await set_limit(interaction, interaction.user.id, scope, limit)
        await in_app_logging.send_log(self.bot, log, 2, 1, interaction)

    @app_commands.command(name="csr2_getlimit", description="View the limit on the number of results")
    @app_commands.choices(scope=[app_commands.Choice(name="Server", value="server_limits"), app_commands.Choice(name="Personal", value="user_limits")])
    async def get_limit(self, interaction: discord.Interaction, scope: str = None):
        logger.info(f"GETLIMIT - The following command has been used: /csr2_getlimit scope: {scope}")
        log = f"GETLIMIT - The following command has been used: /csr2_getlimit scope: {scope}"
        await interaction.response.defer(ephemeral=True)

        if interaction.guild is None:
            if scope == "server_limits":
                await interaction.followup.send("This is DMs. Server limits do not apply here")
                await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
                return
            else:
                limit = await get_limit(interaction.user.id, scope)
        else:
            if scope == "server_limits":
                limit = await get_limit(interaction.guild.id, scope)
            else:
                limit = await get_limit(interaction.user.id, scope)

        if scope == "server_limits":
            description=f"## Current limit: **{limit}**\n\n-# A moderator of this server can change it by using </csr2_limitresults:{os.getenv('CSR2_LIMITRESULTS_COMMAND')}>, entering a value and selecting `Server` as the scope."
        else:
            description=f"## Current limit: **{limit}**\n\n-# You can change it by using </csr2_limitresults:{os.getenv('CSR2_LIMITRESULTS_COMMAND')}>, entering a value and selecting `Personal` as the scope."

        embed = discord.Embed(
            title=f"Results limit for {interaction.guild.name if scope == "server_limits" else interaction.user.display_name}",
            description=description,
            color=discord.Color(0xff00ff)
        )
        embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')

        await interaction.followup.send(embed=embed, ephemeral=True)
        await in_app_logging.send_log(self.bot, log, 2, 1, interaction)

async def set_limit(interaction: discord.Interaction, id: str, scope: str, limit: int):
    data = await load_limits(scope)

    if str(id) not in data:
        data[str(id)] = {"PostLimit": limit}
    else:
        data[str(id)]["PostLimit"] = limit

    await save_limits(data, scope)

    if limit == 0:
        limit = "∞"

    embed=discord.Embed(
        title=f"New Results limit for {interaction.guild.name if scope == "server_limits" else interaction.user.display_name}",
        description=f"## New Limit: {limit}",
        color=discord.Color(0xff00ff)
    )
    await interaction.followup.send(embed=embed, ephemeral=True)

async def get_limit(id: str, scope: str):
    data = await load_limits(scope)
    limit = data.get(id,{"PostLimit": 0})["PostLimit"]
    if limit == 0:
        limit = "∞"
    return limit

async def load_limits(scope: str):
    JSON_FILE_PATH =await helpers.load_file_path(f'{scope}')
    if not os.path.exists(JSON_FILE_PATH):
        return {}
    async with aiofiles.open(JSON_FILE_PATH, 'r') as file:
        content = await file.read()
        return json.loads(content)

async def save_limits(data, scope: str):
    JSON_FILE_PATH = await helpers.load_file_path(f'{scope}')
    async with aiofiles.open(JSON_FILE_PATH, 'w') as file:
        await file.write(json.dumps(data, indent=4))

async def setup(bot):
    await bot.add_cog(LimitResultsCog(bot))
