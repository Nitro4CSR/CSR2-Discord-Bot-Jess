import json
import discord
from discord.ext import commands
from discord import app_commands
import logging
import in_app_logging
import helpers

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file
NITRO = helpers.load_super_admin()

def is_server_owner(interaction: discord.Interaction):
    if ((interaction.user.id == interaction.guild.owner_id) or (str(interaction.user.id) == str(NITRO))):
        return interaction.user.id
    else:
        return None

class AnnounceUpdatesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name="csr2_announce_updates_add", description="Set a text channel as Announcements channel for app updates")
    @app_commands.choices(scope=[app_commands.Choice(name="All (CSR2, CSR3 & Blog)", value="All"), app_commands.Choice(name="CSR2", value="CSR2"), app_commands.Choice(name="CSR3", value="CSR3"), app_commands.Choice(name="Blog", value="Blog")])
    @app_commands.check(is_server_owner)
    @app_commands.describe(channel="Channel to send announcements to", scope="Which app updates to announce")
    async def announce_updates_add(self, interaction: discord.Interaction, channel: discord.TextChannel, scope: str = None):
        # Log the command usage and parameters
        logger.info(f"The following command has been used: /csr2_announce_updates_add channel: {channel} scope: {scope}")
        log = f"The following command has been used: /csr2_announce_updates_add channel: {channel} scope: {scope}"
        
        if interaction.user.id == interaction.guild.owner_id or str(interaction.user.id) == str(NITRO):
            log += f"\nUser is Server Owner"
            await interaction.response.defer(ephemeral=True)

            if (scope == None):
                scope = "All"

            embed = discord.Embed(title="Test Message", description=f"This channel will be used for {scope} app update announcements.", color=discord.Color(0xff00ff))
            embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')

            try:
                send_channel = self.bot.get_channel(int(channel.id))
                await send_channel.send(embed=embed)
                check, log = await add_channel(channel, scope, log)
            except Exception as e:
                await interaction.followup.send(f"There was an error with trying to send a message: {e}", ephemeral=True)
                return
            
            if check == 1:
                 await interaction.followup.send(f"The channel {channel} has been added to announcement channels list", ephemeral=True)
                 log += f"\nThe channel {channel} has been added to announcement channels list"
            else:
                 await interaction.followup.send(f"There was an error adding the channel {channel} to announcement channels list", ephemeral=True)
                 log += f"\nThere was an error adding the channel {channel} to announcement channels list"

        else:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            log += f"\nUser is not Server Owner"
        await in_app_logging.send_log(self.bot, log, interaction)

    @app_commands.command(name="csr2_announce_updates_delete", description="Set a text channel as Announcements channel for app updates")
    @app_commands.choices(scope=[app_commands.Choice(name="All (CSR2, CSR3 & Blog)", value="All"), app_commands.Choice(name="CSR2", value="CSR2"), app_commands.Choice(name="CSR3", value="CSR3"), app_commands.Choice(name="Blog", value="Blog")])
    @app_commands.check(is_server_owner)
    @app_commands.describe(channel="Channel to send announcements to", scope="Which app updates to announce")
    async def announce_updates_delete(self, interaction: discord.Interaction, channel: discord.TextChannel, scope: str = None):
        # Log the command usage and parameters
        logger.info(f"The following command has been used: /csr2_announce_updates_delete channel: {channel} scope: {scope}")
        log = f"The following command has been used: /csr2_announce_updates_delete channel: {channel} scope: {scope}"
        
        if interaction.user.id == interaction.guild.owner_id or str(interaction.user.id) == str(NITRO):
            log += f"\nUser is Server Owner"
            await interaction.response.defer(ephemeral=True)

            if (scope == None):
                scope = "All"

            check, log = await delete_channel(channel.id, scope, log)
            
            if check == 1:
                 await interaction.followup.send(f"The channel {channel} has been removed from announcement channels list", ephemeral=True)
                 log += f"\nThe channel {channel} has been removed from announcement channels list"
            else:
                 await interaction.followup.send(f"There was an error removing the channel {channel} from announcement channels list", ephemeral=True)
                 log += f"\nThere was an error removing the channel {channel} from announcement channels list"

        else:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            log += f"\nUser is not Server Owner"
        await in_app_logging.send_log(self.bot, log, interaction)


async def add_channel(channel: discord.TextChannel, scope: str, log: str):
    csr2 = await helpers.load_CSR2_announcement_channels()
    csr3 = await helpers.load_CSR3_announcement_channels()
    blog = await helpers.load_blog_announcement_channels()

    csr2_check = 0
    csr3_check = 0
    blog_check = 0

    if (scope == "All"):
        if channel.id not in csr2:
            csr2.add(str(channel.id))
        csr2_check, log = save_csr2_channels(csr2, log)
        if channel.id not in csr3:
            csr3.add(str(channel.id))
        csr3_check, log = save_csr3_channels(csr3, log)
        if channel.id not in blog:
            blog.add(str(channel.id))
        blog_check, log = save_blog_channels(blog, log)
        if csr2_check == 1 and blog_check == 1 and blog_check == 1:
            check = 1
        else:
            check = 0
    elif (scope == "CSR2"):
        if channel.id not in csr2:
            csr2.add(str(channel.id))
        csr2_check, log = save_csr2_channels(csr2, log)
        if csr2_check == 1:
            check = 1
        else:
            check = 0
    elif (scope == "CSR3"):
        if channel.id not in csr3:
            csr3.add(str(channel.id))
        csr3_check, log = save_csr3_channels(csr3, log)
        if csr3_check == 1:
            check = 1
        else:
            check = 0
    elif (scope == "Blog"):
        if channel.id not in blog:
            blog.add(str(channel.id))
        blog_check, log = save_blog_channels(blog, log)
        if blog_check == 1:
            check = 1
        else:
            check = 0
    else:
        logger.error(f"Channel {channel} could not be added to announcements lists because no scope was defined")
        log += f"\nChannel {channel} could not be added to announcements lists because no scope was defined"
        check = 0
    return check, log

async def delete_channel(channel: str, scope: str, log: str = None):
    csr2 = await helpers.load_CSR2_announcement_channels()
    csr3 = await helpers.load_CSR3_announcement_channels()
    blog = await helpers.load_blog_announcement_channels()

    csr2_check = 0
    csr3_check = 0
    blog_check = 0

    if (scope == "All"):
        try:
            csr2.remove(str(channel))
        except Exception as e:
            log += f"Channel {channel} not in CSR2 announcemt channel list"
        csr2_check, log = save_csr2_channels(csr2, log)
        try:
            csr3.remove(str(channel))
        except Exception as e:
            log += f"Channel {channel} not in CSR3 announcemt channel list"
        csr3_check, log = save_csr3_channels(csr3, log)
        try:
            blog.remove(str(channel))
        except Exception as e:
            log += f"Channel {channel} not in Blog announcemt channel list"
        blog_check, log = save_blog_channels(blog, log)
        if csr2_check == 1 and csr3_check == 1 and blog_check == 1:
            check = 1
        else:
            check = 0
    elif (scope == "CSR2"):
        try:
            csr2.remove(str(channel))
        except Exception as e:
            log += f"Channel {channel} not in CSR2 announcemt channel list"
        csr2_check, log = save_csr2_channels(csr2, log)
        if csr2_check == 1:
            check = 1
        else:
            check = 0
    elif (scope == "CSR3"):
        try:
            csr3.remove(str(channel))
        except Exception as e:
            log += f"Channel {channel} not in CSR3 announcemt channel list"
        csr3_check, log = save_csr3_channels(csr3, log)
        if csr3_check == 1:
            check = 1
        else:
            check = 0
    elif (scope == "Blog"):
        try:
            blog.remove(str(channel))
        except Exception as e:
            log += f"Channel {channel} not in Blog announcemt channel list"
        blog_check, log = save_blog_channels(blog, log)
        if blog_check == 1:
            check = 1
        else:
            check = 0
    else:
        logger.error(f"Channel {channel} could not be removed from announcements lists because no scope was defined")
        log += f"\nChannel {channel} could not be removed from announcements lists because no scope was defined"
        check = 0
    return check, log

def save_csr2_channels(csr2, log):
    CSR2_ANNOUNCEMENT_CHANNEL_FILE = helpers.load_CSR2_announcement_channel_file()
    try:
        with open(CSR2_ANNOUNCEMENT_CHANNEL_FILE, 'w') as f:
            json.dump(list(csr2), f)
            check = 1
    except Exception as e:
        logger.error(f"Error saving CSR2 announcement channels file: {e}")
        log += f"\nError saving CSR2 announcement channels file: {e}"
    return check, log

def save_csr3_channels(csr3, log):
    CSR3_ANNOUNCEMENT_CHANNEL_FILE = helpers.load_CSR3_announcement_channel_file()
    try:
        with open(CSR3_ANNOUNCEMENT_CHANNEL_FILE, 'w') as f:
            json.dump(list(csr3), f)
            check = 1
    except Exception as e:
        logger.error(f"Error saving CSR3 announcement channels file: {e}")
        log += f"\nError saving CSR3 announcement channels file: {e}"
    return check, log

def save_blog_channels(blog, log):
    BLOG_ANNOUNCEMENT_CHANNEL_FILE = helpers.load_blog_announcement_channel_file()
    try:
        with open(BLOG_ANNOUNCEMENT_CHANNEL_FILE, 'w') as f:
            json.dump(list(blog), f)
            check = 1
    except Exception as e:
        logger.error(f"Error saving Blog announcement channels file: {e}")
        log += f"\nError saving Blog announcement channels file: {e}"
    return check, log

async def setup(bot):
    await bot.add_cog(AnnounceUpdatesCog(bot))
