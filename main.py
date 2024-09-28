import discord
from discord.ext import commands
import os
import logging
import asyncio
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

async def schedule_updates():
    tunes_manager.create_database()
    while True:
        try:
            database_manager.recreate_database()
        except Exception as e:
            logging.error(f"Error during database update: {e}")
        await asyncio.sleep(3600)  # Sleep for 1 hour

async def main():
    asyncio.create_task(schedule_updates())
    await bot.start(TOKEN)

if __name__ == "__main__":
    bot.setup_hook = setup_hook
    asyncio.run(main())
