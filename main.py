import discord
from discord.ext import commands
import os
import logging
import asyncio
import datetime
import database_manager
import tunes_manager
import version_check_manager_CSR2
import version_check_manager_CSR3
import version_check_manager_blog
import helpers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load environment variables from .env file
TOKEN = helpers.load_token()
CLIENT_ID = helpers.load_client_id()
ADMIN_SERVER = helpers.load_admin_server()
LOG_CHANNEL = helpers.load_log_channel()
FIRST_SETUP_DONE = helpers.load_setup_status()

# Paths to the profile images
DEFAULT_PFP_PATH = helpers.load_default_pfp()
HALLOWEEN_PFP_PATH = helpers.load_halloween_pfp()
CHRISTMAS_PFP_PATH = helpers.load_xmas_pfp()
BIRTHDAY_PFP_PATH = helpers.load_bday_pfp()

# Desired names
DEFAULT_NAME = helpers.load_default_name()
HALLOWEEN_NAME = helpers.load_halloween_name()
CHRISTMAS_NAME = helpers.load_xmas_name()
BIRTHDAY_NAME = helpers.load_bday_name()

BDAY_MONTH = helpers.load_bday_month()
BDAY_DAY = helpers.load_bday_day()

# Ensure CLIENT_ID and TOKEN are loaded
if not TOKEN or not CLIENT_ID:
    logging.error("TOKEN or CLIENT_ID is missing from the environment variables.")
    exit(1)

# Create the bot object with intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.emojis_and_stickers = True
intents.presences = True  # Enable presence intent
bot = commands.Bot(command_prefix="?CSR2", intents=intents)

async def load_cogs():
    for filename in os.listdir(f'{os.path.dirname(os.path.abspath(__file__))}/cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')

async def setup_hook():
    await load_cogs()
    await bot.tree.sync()

@bot.event
async def on_ready():
    logging.info(f"Logged in as {bot.user.name} ({bot.user.id})")

    if not FIRST_SETUP_DONE:
        logging.info(f"First time setup detected! Running tasks for initial setup...")
        emojis = {}
        for file in os.listdir(f'{os.path.dirname(os.path.abspath(__file__))}/bot-emojis'):
            if file.endswith((".png", ".gif")):
                try:
                    with open(f"{os.path.dirname(os.path.abspath(__file__))}/bot-emojis/{file}", "rb") as image:
                        emoji_name = os.path.splitext(file)[0]
                        emoji = await bot.create_application_emoji(name=emoji_name, image=image.read())
                        emojis[emoji_name] = str(emoji)
                        logging.info(f"Uploaded emoji: {emoji.name} (ID: {emoji.id})")
                except Exception as e:
                    logging.error(f"Failed to upload {emoji_name}: {e}")
        if emojis:
            logging.info("Emoji markdowns:")
            dotenv = helpers.load_dotenv_dir()
            with open(dotenv, "a") as f:
                for name, markdown in emojis.items():
                    f.write(f"\n{name.upper()}_EMOJI={markdown}")
                    logging.info(f"{name}: {markdown}")
                    asyncio.sleep(0.1)
            with open(dotenv, "r") as f:
                lines = f.readlines()
            with open(dotenv, "w") as f:
                found = False
                for line in lines:
                    if line.startswith("FIRST_SETUP_DONE="):
                        f.write("FIRST_SETUP_DONE=True\n")
                        found = True
                    else:
                        f.write(line)
                if not found:
                    f.write("\nFIRST_SETUP_DONE=True\n")

            logging.info("Reloading environment variables...")
            helpers.load_dotenv_data()

    # Set a simple presence for the bot using discord.py
    await bot.change_presence(activity=discord.Game(name="CSR Racing"))
    logging.info("Basic presence set")

    try:
        admin_guild = bot.get_guild(int(ADMIN_SERVER))
        logging.info(f"Trying to sync commands to Admin Server ({admin_guild.name})")
        await bot.tree.sync(guild=discord.Object(id=int(ADMIN_SERVER)))
        logging.info(f"Commands synced to to Admin Server ({admin_guild.name})")
    except Exception as e:
        logging.error(f"Failed to sync commands: {e}")

    asyncio.create_task(schedule_profile_update())
    await asyncio.sleep(3)
    asyncio.create_task(schedule_version_check())
    await asyncio.sleep(3)
    asyncio.create_task(schedule_blog_check())

async def profile_update():
    # Runs daily at midnight to check if it's October 1st or November 1st.
    today = datetime.datetime.now().date()
    
    # Check if current day is Birthday
    if today.month == BDAY_MONTH and today.day == BDAY_DAY:
        await update_bot_profile(BIRTHDAY_PFP_PATH, DEFAULT_NAME)
    # Check if current month is October
    elif today.month == 10:
        await update_bot_profile(HALLOWEEN_PFP_PATH, HALLOWEEN_NAME)
    # Check if current month is December
    elif today.month == 12:
        await update_bot_profile(CHRISTMAS_PFP_PATH, CHRISTMAS_NAME)
    # Fallback to default
    else:
        await update_bot_profile(DEFAULT_PFP_PATH, DEFAULT_NAME)

async def update_bot_profile(pfp_path, new_name):
    # Updates bot's profile picture and name based on given parameters.
    with open(pfp_path, 'rb') as pfp_file:
        bot_pfp = bot.user.avatar
        if bot_pfp != pfp_file:
            try:
                # Update bot name and avatar
                await bot.user.edit(username=new_name, avatar=pfp_file.read())
                logging.info(f"Updated bot name to '{new_name}' and profile picture.")
            except discord.HTTPException as e:
                logging.info(f"Failed to update bot profile: {e}")

async def schedule_db_updates():
    tunes_manager.create_database()
    while True:
        try:
            await database_manager.recreate_database()
        except Exception as e:
            logging.error(f"Error during database update: {e}")
        await asyncio.sleep(300)  # Sleep for 5 minutes

async def schedule_version_check():
    while True:
        try:
            await asyncio.gather(version_check_manager_CSR2.version_check_task(bot), version_check_manager_CSR3.version_check_task(bot))
        except Exception as e:
            logging.error(f"Error during version check: {e}")
        await asyncio.sleep(1788)  # Sleep for 29 minutes 48 seconds

async def schedule_blog_check():
    while True:
        try:
            await asyncio.gather(version_check_manager_blog.version_check_task(bot))
        except Exception as e:
            logging.error(f"Error during version check: {e}")
        await asyncio.sleep(60)  # Sleep for 1 minute

async def schedule_profile_update():
    while True:
        try:
            await profile_update()
        except Exception as e:
            logging.error(f"Error during profile update: {e}")
        await asyncio.sleep(86400) # Sleep for 1 day

async def main():
    asyncio.create_task(schedule_db_updates())
    await bot.start(TOKEN)

if __name__ == "__main__":
    bot.setup_hook = setup_hook
    asyncio.run(main())
