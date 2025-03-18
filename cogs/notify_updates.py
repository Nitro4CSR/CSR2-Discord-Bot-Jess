import discord
from discord.ext import commands
from discord import app_commands
import aiofiles
import json
import in_app_logging
import helpers

logger = helpers.load_logging()

class NotifyUpdatesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="csr2_notify_updates_add", description="Allow Jess to notify you about updates in DMs")
    @app_commands.choices(scope=helpers.load_command_options_scope())
    @app_commands.describe(scope="Which app updates to announce")
    async def notify_updates_add(self, interaction: discord.Interaction, scope: str = None):
        logger.info(f"NOTIFY_UPDATES_ADD - The following command has been used: /csr2_notify_updates_add scope: {scope}")
        log = f"NOTIFY_UPDATES_ADD - The following command has been used: /csr2_notify_updates_add scope: {scope}"
        await interaction.response.defer()

        log += f"\nUser is Server Owner"

        if (scope == None):
             scope = ["CSR2", "CSR3", "Blog"]
        else:
            scope = await str_to_list(scope)

        embed = discord.Embed(title="Test Message", description=f"This channel will be used for {scope} update announcements.", color=discord.Color(0xff00ff))
        embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')

        checks = []
        status_list = []
        try:
            message = await interaction.user.send(embed=embed, silent=True)
            for scope in scope:
                check, log, status = await process_request(interaction.user.id, scope, 1, log)
                checks.append(check)
                status_list.append(status)
            await message.delete()
        except Exception as e:
            await interaction.channel.send(f"There was an error with trying to send a message: {e}")
            return

        if max(checks) == 1:
             await interaction.followup.send(f"The user {interaction.user.display_name} has been added to announcement users list(s)", ephemeral=True)
             log += f"NOTIFY_UPDATES_ADD - The user {interaction.user.display_name} has been added to announcement users list(s)"
        else:
             await interaction.followup.send(f"There was an error adding the user {interaction.user.display_name} to announcement users list(s)", ephemeral=True)
             log += f"NOTIFY_UPDATES_ADD - There was an error adding the user {interaction.user.display_name} to announcement users list(s)"

        await in_app_logging.send_log(self.bot, log, min(status_list), 1, interaction)

    @app_commands.command(name="csr2_notify_updates_delete", description="Allow Jess to notify you about updates in DMs")
    @app_commands.choices(scope=helpers.load_command_options_scope())
    @app_commands.describe(scope="Which app updates to announce")
    async def notify_updates_delete(self, interaction: discord.Interaction, scope: str = None):
        logger.info(f"NOTIFY_UPDATES_DELETE - The following command has been used: /csr2_notify_updates_delete scope: {scope}")
        log = f"NOTIFY_UPDATES_DELETE - The following command has been used: /csr2_notify_updates_delete scope: {scope}"

        log += f"\nUser is Server Owner"
        await interaction.response.defer(ephemeral=True)

        if (scope == None):
            scope = ["CSR2", "CSR3", "Blog"]
        else:
            scope = await str_to_list(scope)

        checks = []
        status_list = []
        for scope in scope:
            check, log, status = await process_request(interaction.user.id, scope, 0, log)
            checks.append(check)
            status_list.append(status)

        if max(checks) == 1:
             await interaction.followup.send(f"You were removed from announcement channels list(s)", ephemeral=True)
             log += f"\nNOTIFY_UPDATES_DELETE - You were removed from announcement channels list(s)"
        else:
             await interaction.followup.send(f"There was an error removing you from announcement channels list(s)", ephemeral=True)
             log += f"\nNOTIFY_UPDATES_DELETE - There was an error removing you from announcement channels list(s)"
        await in_app_logging.send_log(self.bot, log, min(status_list), 1, interaction)

async def str_to_list(scope: str):
    scope_list = []
    if scope == "CSR2" or scope == "All":
        scope_list.append("CSR2")

    if scope == "CSR3" or scope == "All":
        scope_list.append("CSR3")

    if scope == "Blog" or scope == "All":
        scope_list.append("Blog")

    return scope_list

async def process_request(id: str, scope: str, request: int, log: str):
    list = await helpers.load_file(f'{scope} announcement user file')
    if request == 1:
        check, log, status = await add_id(list, scope, id, log)
    elif request == 0:
        check, log, status = await del_id(list, scope, id, log)
    else:
        check = 0
        log += f"NOTIFY_UPDATES - There was an error processing the request"
        status = 0

    return check, log, status

async def add_id(list: set, scope: str, id: str, log: str):
    if str(id) not in list:
        list.add(str(id))
    check, log, status = await save_list(list, scope, log)

    return check, log, status

async def del_id(list: set, scope: str, id: str, log: str):
    if str(id) in list:
        list.remove(str(id))
    check, log, status = await save_list(list, scope, log)

    return check, log, status

async def save_list(id_list: set, scope: str, log: str):
    FILE = await helpers.load_file_path(f'{scope}_announcement_users')
    try:
        async with aiofiles.open(FILE, 'w') as f:
            await f.write(json.dumps(list(id_list)))
            check = 1
            status = 2
    except Exception as e:
        logger.error(f"NOTIFY_UPDATES - Error saving {scope} announcement user file: {e}")
        log += f"\nNOTIFY_UPDATES - Error saving {scope} announcement user file: {e}"
        check = 0
        status = 0

    return check, log, status

async def setup(bot):
    await bot.add_cog(NotifyUpdatesCog(bot))
