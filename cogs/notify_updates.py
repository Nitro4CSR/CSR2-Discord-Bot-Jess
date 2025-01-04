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

class NotifyUpdatesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name="csr2_notify_updates_add", description="Allow Jess to notify you about updates in DMs")
    @app_commands.choices(scope=[app_commands.Choice(name="Both (CSR2 & CSR3)", value="Both"), app_commands.Choice(name="CSR2", value="CSR2"), app_commands.Choice(name="CSR3", value="CSR3")])
    @app_commands.describe(scope="Which app updates to announce")
    async def notify_updates_add(self, interaction: discord.Interaction, scope: str = None):
        # Log the command usage and parameters
        logger.info(f"The following command has been used: /csr2_announce_updates_add scope: {scope}")
        log = f"The following command has been used: /csr2_announce_updates_add scope: {scope}"

        log += f"\nUser is Server Owner"
        await interaction.response.defer(ephemeral=True)
        if (scope == None):
             scope = "Both"

        embed = discord.Embed(title="Test Message", description=f"This channel will be used for {scope} app update announcements.", color=discord.Color(0xff00ff))
        embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')

        try:
            await interaction.user.send(embed=embed)
            check, log = add_user(scope, interaction, log)
        except Exception as e:
            await interaction.channel.send(f"There was an error with trying to send a message")
            return

        if check == 1:
             await interaction.followup.send(f"The user {interaction.user.display_name} has been added to announcement users list", ephemeral=True)
             log += f"The user {interaction.user.display_name} has been added to announcement users list"
        else:
             await interaction.followup.send(f"There was an error adding the user {interaction.user.display_name} to announcement users list", ephemeral=True)
             log += f"There was an error adding the user {interaction.user.display_name} to announcement users list"

        await in_app_logging.send_log(self.bot, log, interaction)


    @app_commands.command(name="csr2_notify_updates_delete", description="Allow Jess to notify you about updates in DMs")
    @app_commands.choices(scope=[app_commands.Choice(name="Both (CSR2 & CSR3)", value="Both"), app_commands.Choice(name="CSR2", value="CSR2"), app_commands.Choice(name="CSR3", value="CSR3")])
    @app_commands.describe(scope="Which app updates to announce")
    async def notify_updates_delete(self, interaction: discord.Interaction, scope: str = None):
        # Log the command usage and parameters
        logger.info(f"The following command has been used: /csr2_announce_updates_delete scope: {scope}")
        log = f"The following command has been used: /csr2_announce_updates_delete scope: {scope}"

        log += f"\nUser is Server Owner"
        await interaction.response.defer(ephemeral=True)
        if (scope == None):
             scope = "Both"

        check, log = delete_user(scope, interaction, log)
            
        if check == 1:
             await interaction.followup.send(f"You were removed from announcement channels list", ephemeral=True)
             log += f"\nYou were removed from announcement channels list"
        else:
             await interaction.followup.send(f"There was an error removing you from announcement channels list", ephemeral=True)
             log += f"\nThere was an error removing you from announcement channels list"
        await in_app_logging.send_log(self.bot, log, interaction)



def add_user(scope: str, interaction: discord.Interaction, log: str):
    csr2 = helpers.load_CSR2_announcement_users()
    csr3 = helpers.load_CSR3_announcement_users()

    csr2_check = 0
    csr3_check = 0

    if (scope == "Both"):
        if interaction.user.id not in csr2:
            csr2.add(str(interaction.user.id))
        csr2_check, log = save_csr2_users(csr2, log)
        if interaction.user.id not in csr3:
            csr3.add(str(interaction.user.id))
        csr3_check, log = save_csr3_users(csr3, log)
        if csr2_check == 1 and csr3_check == 1:
            check = 1
        else:
            check = 0
    elif (scope == "CSR2"):
        if interaction.user.id not in csr2:
            csr2.add(str(interaction.user.id))
        csr2_check, log = save_csr2_users(csr2, log)
        if csr2_check == 1:
            check = 1
        else:
             check = 0
    elif (scope == "CSR3"):
        if interaction.user.id not in csr3:
            csr3.add(str(interaction.user.id))
        csr3_check, log = save_csr3_users(csr3, log)
        if csr3_check == 1:
            check = 1
        else:
            check = 0
    else:
        logger.error(f"User {interaction.user.display_name} could not be added to announcements lists because no scope was defined")
        log += f"User {interaction.user.display_name} could not be added to announcements lists because no scope was defined"
        check = 0
    return check, log

def delete_user(scope: str, interaction: discord.Interaction, log: str):
    csr2 = helpers.load_CSR2_announcement_users()
    csr3 = helpers.load_CSR3_announcement_users()

    csr2_check = 0
    csr3_check = 0

    if (scope == "Both"):
        try:
            csr2.remove(str(interaction.user.id))
        except Exception as e:
            log += f"User {interaction.user.id} not in CSR2 announcemt user list"
        csr2_check, log = save_csr2_users(csr2, log)
        try:
            csr3.remove(str(interaction.user.id))
        except Exception as e:
            log += f"User {interaction.user.id} not in CSR3 announcemt user list"
        csr3_check, log = save_csr3_users(csr3, log)
        if csr2_check == 1 and csr3_check == 1:
            check = 1
        else:
            check = 0
    elif (scope == "CSR2"):
        try:
            csr2.remove(str(interaction.user.id))
        except Exception as e:
            log += f"User {interaction.user.id} not in CSR2 announcemt user list"
        csr2_check, log = save_csr2_users(csr2, log)
        if csr2_check == 1:
            check = 1
        else:
             check = 0
    elif (scope == "CSR3"):
        try:
            csr3.remove(str(interaction.user.id))
        except Exception as e:
            log += f"User {interaction.user.id} not in CSR3 announcemt user list"
        csr3_check, log = save_csr3_users(csr3, log)
        if csr3_check == 1:
            check = 1
        else:
            check = 0
    else:
        logger.error(f"User {interaction.user.display_name} could not be removed from announcements lists because no scope was defined")
        log += f"\nUser {interaction.user.display_name} could not be removed from announcements lists because no scope was defined"
        check = 0
    return check, log

def save_csr2_users(csr2, log):
    CSR2_ANNOUNCEMENT_USER_FILE = helpers.load_CSR2_announcement_user_file()
    try:
        with open(CSR2_ANNOUNCEMENT_USER_FILE, 'w') as f:
            json.dump(list(csr2), f)
            check = 1
    except Exception as e:
        logger.error(f"Error saving CSR2 announcement user file: {e}")
        log += f"\nError saving CSR2 announcement user file: {e}"
    return check, log

def save_csr3_users(csr3, log):
    CSR3_ANNOUNCEMENT_USER_FILE = helpers.load_CSR3_announcement_user_file()
    try:
        with open(CSR3_ANNOUNCEMENT_USER_FILE, 'w') as f:
            json.dump(list(csr3), f)
            check = 1
    except Exception as e:
        logger.error(f"Error saving CSR3 announcement user file: {e}")
        log += f"\nError saving CSR3 announcement user file: {e}"
    return check, log

async def setup(bot):
    await bot.add_cog(NotifyUpdatesCog(bot))
