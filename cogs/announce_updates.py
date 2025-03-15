import discord
from discord.ext import commands
from discord import app_commands
import aiofiles
import json
import in_app_logging
import helpers

logger = helpers.load_logging()

class AnnounceUpdatesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="csr2_announce_updates_add", description="Set a text channel as Announcements channel for app updates")
    @app_commands.choices(scope=[app_commands.Choice(name="All (CSR2, CSR3 & Blog)", value="All"), app_commands.Choice(name="CSR2", value="CSR2"), app_commands.Choice(name="CSR3", value="CSR3"), app_commands.Choice(name="Blog", value="Blog")])
    @app_commands.describe(channel="Channel to send announcements to", scope="Which app updates to announce")
    async def announce_updates_add(self, interaction: discord.Interaction, channel: discord.TextChannel, scope: str = None):
        logger.info(f"ANNOUNCE_UPDATES_ADD - The following command has been used: /csr2_announce_updates_add channel: {channel} scope: {scope}")
        log = f"ANNOUNCE_UPDATES_ADD - The following command has been used: /csr2_announce_updates_add channel: {channel} scope: {scope}"

        NITRO = await helpers.load_super_admin()
        status_list = []
        if interaction.user.id == interaction.guild.owner.id or interaction.user.id == interaction.user.guild_permissions.administrator or str(interaction.user.id) == str(NITRO):
            log += f"\nANNOUNCE_UPDATES_ADD - User has required permissions"
            await interaction.response.defer(ephemeral=True)

            if (scope == None):
                scope = ["CSR2", "CSR3", "Blog"]
            else:
                scope = await str_to_list(scope)

            embed = discord.Embed(title="Test Message", description=f"This channel will be used for {scope} update announcements.", color=discord.Color(0xff00ff))
            embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')

            checks = []
            try:
                send_channel = self.bot.get_channel(int(channel.id))
                message = await send_channel.send(embed=embed)
                for scope in scope:
                    check, log, status = await process_request(channel.id, scope, 1, log)
                    checks.append(check)
                    status_list.append(status)
                await message.delete()
            except Exception as e:
                await interaction.followup.send(f"There was an error with trying to send a message: {e}", ephemeral=True)
                status = 0
                return

            if max(checks) == 1:
                 await interaction.followup.send(f"The channel {channel} has been added to announcement channels list(s)", ephemeral=True)
                 log += f"\nANNOUNCE_UPDATES_ADD - The channel {channel} has been added to announcement channels list(s)"
            else:
                 await interaction.followup.send(f"There was an error adding the channel {channel} to announcement channels list(s)", ephemeral=True)
                 log += f"\nANNOUNCE_UPDATES_ADD - There was an error adding the channel {channel} to announcement channels list(s)"

        else:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            log += f"\nANNOUNCE_UPDATES_ADD - User lacks required permissions"
            status_list.append(2)
        await in_app_logging.send_log(self.bot, log, 2, 1, interaction)

    @app_commands.command(name="csr2_announce_updates_delete", description="Set a text channel as Announcements channel for app updates")
    @app_commands.choices(scope=[app_commands.Choice(name="All (CSR2, CSR3 & Blog)", value="All"), app_commands.Choice(name="CSR2", value="CSR2"), app_commands.Choice(name="CSR3", value="CSR3"), app_commands.Choice(name="Blog", value="Blog")])
    @app_commands.describe(channel="Channel to send announcements to", scope="Which app updates to announce")
    async def announce_updates_delete(self, interaction: discord.Interaction, channel: discord.TextChannel, scope: str = None):
        logger.info(f"The following command has been used: /csr2_announce_updates_delete channel: {channel} scope: {scope}")
        log = f"The following command has been used: /csr2_announce_updates_delete channel: {channel} scope: {scope}"

        NITRO = await helpers.load_super_admin()
        status_list = []
        if interaction.user.id == interaction.guild.owner.id or interaction.user.id == interaction.user.guild_permissions.administrator or str(interaction.user.id) == str(NITRO):
            log += f"\nANNOUNCE_UPDATES_DELETE - User has required permissions"
            await interaction.response.defer(ephemeral=True)

            if (scope == None):
                scope = ["CSR2", "CSR3", "Blog"]
            else:
                scope = await str_to_list(scope)

            checks = []
            for scope in scope:
                check, log, status = await process_request(channel.id, scope, 0, log)
                checks.append(check)
                status_list.append(status)

            if max(checks) == 1:
                 await interaction.followup.send(f"The channel {channel} has been removed from announcement channels list(s)", ephemeral=True)
                 log += f"\nANNOUNCE_UPDATES_DELETE - The channel {channel} has been removed from announcement channels list(s)"
            else:
                 await interaction.followup.send(f"There was an error removing the channel {channel} from announcement channels list(s)", ephemeral=True)
                 log += f"\nANNOUNCE_UPDATES_DELETE - There was an error removing the channel {channel} from announcement channels list(s)"

        else:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            log += f"\nANNOUNCE_UPDATES_DELETE - User lacks required permissions"
            status_list.append(2)
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
    list = await helpers.load_file(f'{scope} announcement channel file')
    if request == 1:
        check, log, status = await add_id(list, scope, id, log)
    elif request == 0:
        check, log, status = await del_id(list, scope, id, log)
    else:
        check = 0
        log += f"ANNOUNCE_UPDATES - There was an error processing the request"
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
    FILE = await helpers.load_file_path(f'{scope}_announcement_channels')
    try:
        async with aiofiles.open(FILE, mode='w') as f:
            await f.write(json.dumps(list(id_list)))
            check = 1
            status = 2
    except Exception as e:
        logger.error(f"ANNOUNCE_UPDATES - Error saving {scope} announcement user file: {e}")
        log += f"\nANNOUNCE_UPDATES - Error saving {scope} announcement user file: {e}"
        check = 0
        status = 0

    return check, log, status

async def setup(bot):
    await bot.add_cog(AnnounceUpdatesCog(bot))
