import discord
from discord.ext import commands
from discord.ext import tasks
import os
import logging
import asyncio
import datetime
import database_manager
import tunes_manager
import helpers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load environment variables from .env file
TOKEN = helpers.load_token()
CLIENT_ID = helpers.load_client_id()

# Paths to the profile images
DEFAULT_PFP_PATH = helpers.load_default_pfp()
HALLOWEEN_PFP_PATH = helpers.load_halloween_pfp()
CHRISTMAS_PFP_PATH = helpers.load_xmas_pfp()

# Desired names
DEFAULT_NAME = helpers.load_default_name()
HALLOWEEN_NAME = helpers.load_halloween_name()
CHRISTMAS_NAME = helpers.load_xmas_name()

# Ensure CLIENT_ID and TOKEN are loaded
if not TOKEN or not CLIENT_ID:
    logging.error("TOKEN or CLIENT_ID is missing from the environment variables.")
    exit(1)

# Create the bot object with intents
intents = discord.Intents.default()
intents.message_content = True
intents.presences = True  # Enable presence intent
bot = commands.Bot(command_prefix="?CSR2", intents=intents)

async def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')

async def setup_hook():
    await load_cogs()
    await bot.tree.sync()

@bot.event
async def on_ready():
    logging.info(f"Logged in as {bot.user.name} ({bot.user.id})")
    # await bot.get_channel(1281701107999047814).send(f"Logged in as {bot.user.name} ({bot.user.id})")

    # Set a simple presence for the bot using discord.py
    activity = discord.Game(name="CSR Racing")
    await bot.change_presence(activity=activity)
    logging.info("Basic presence set")
    await profile_update()

async def profile_update():
    # Runs daily at midnight to check if it's October 1st or November 1st.
    today = datetime.datetime.now().date()
    
    # Check if current month is November or January
    if today.month == 11 or today.month == 1:
        await update_bot_profile(DEFAULT_PFP_PATH, DEFAULT_NAME)
    # Check if current month is October
    elif today.month == 10:
        await update_bot_profile(HALLOWEEN_PFP_PATH, HALLOWEEN_NAME)
    # Check if current month is December
    elif today.month == 12:
        await update_bot_profile(CHRISTMAS_PFP_PATH, CHRISTMAS_NAME)



async def update_bot_profile(pfp_path, new_name):
    # Updates bot's profile picture and name based on given parameters.
    with open(pfp_path, 'rb') as pfp_file:
        try:
            # Update bot name and avatar
            await bot.user.edit(username=new_name, avatar=pfp_file.read())
            print(f"Updated bot name to '{new_name}' and profile picture.")
        except discord.HTTPException as e:
            print(f"Failed to update bot profile: {e}")

async def schedule_db_updates():
    tunes_manager.create_database()
    while True:
        try:
            database_manager.recreate_database()
        except Exception as e:
            logging.error(f"Error during database update: {e}")
        await asyncio.sleep(3600)  # Sleep for 1 hour

async def schedule_profile_update():
    while True:
        try:
            await schedule_profile_update()
        except Exception as e:
            logging.error(f"Error during profile update: {e}")
        await asyncio.sleep(86400)

async def main():
    asyncio.create_task(schedule_db_updates())
    asyncio.create_task(schedule_profile_update())
    await bot.start(TOKEN)

if __name__ == "__main__":
    bot.setup_hook = setup_hook
    asyncio.run(main())
