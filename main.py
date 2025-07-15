import discord
from discord.ext import commands, tasks
import aiofiles
import asyncio
import datetime
import json
import os
import database_manager
import tunes_manager
import version_check_manager_apps
import version_check_manager_blog
import helpers
import in_app_logging

logger = helpers.load_logging()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.emojis_and_stickers = True
intents.presences = True
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
    log = ""
    VERSION_FILE = await helpers.load_file_path('Version')
    if os.path.exists(VERSION_FILE):
        version = await helpers.load_file('Version')
    else:
        version = {'INITIAL', 'INITIAL'}
        async with aiofiles.open(VERSION_FILE, mode="w") as file:
            await file.write(json.dumps(['INITIAL', 'INITIAL']))
    if len(list(version)) > 1:
        logger.info(f"BOOT - Upgraded Source Code version from {list(version)[1]} to {list(version)[0]}")
        log += f"BOOT - Upgraded Source Code version from {list(version)[1]} to {list(version)[0]}\n"
        async with aiofiles.open(VERSION_FILE, mode="w") as file:
            await file.write(json.dumps([list(version)[0], list(version)[0]]))

    if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "limits.json")):
        log += f"BOOT - Renaming limits.json to server_limits.json due to Code update"
        logger.info(f"BOOT - Renaming limits.json to server_limits.json due to Code update")
        os.rename(os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "limits.json"), os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "server_limits.json"))

    logger.info(f"BOOT - Logged in as {bot.user.name} ({bot.user.id})")
    log += f"BOOT - Logged in as {bot.user.name} ({bot.user.id})"
    status = 2

    if not schedule_db_updates.is_running():
        logger.info(f"BOOT - Starting EDB update scheduler")
        log += f"\nBOOT - Starting EDB update scheduler"
        schedule_db_updates.start()
    if not schedule_version_check.is_running():
        logger.info(f"BOOT - Starting VC store update check scheduler")
        log += f"\nBOOT - Starting VC store update check scheduler"
        schedule_version_check.start()
    if not schedule_blog_check.is_running():
        logger.info(f"BOOT - Starting BLOG update check scheduler")
        log += f"\nBOOT - Starting BLOG update check scheduler"
        schedule_blog_check.start()
    if not schedule_profile_update.is_running():
        logger.info(f"BOOT - Starting PROFILE update scheduler")
        log += f"\nBOOT - Starting PROFILE update scheduler"
        schedule_profile_update.start()

    try:
        ADMIN_SERVER = await helpers.load_admin_server()
        admin_guild = bot.get_guild(int(ADMIN_SERVER))
        logger.info(f"BOOT - Trying to sync commands to Admin Server ({admin_guild.name})")
        log += f"\nBOOT - Trying to sync commands to Admin Server ({admin_guild.name})"
        await bot.tree.sync(guild=discord.Object(id=int(ADMIN_SERVER)))
        logger.info(f"BOOT - Commands synced to to Admin Server ({admin_guild.name})")
        log += f"\nBOOT - Commands synced to to Admin Server ({admin_guild.name})"
    except Exception as e:
        logger.error(f"BOOT - Failed to sync commands: {e}")
        log += f"BOOT - Failed to sync commands: {e}"
        status = 0

    FIRST_SETUP_DONE = await helpers.load_setup_status()

    if not FIRST_SETUP_DONE:
        logger.info(f"BOOT - First time setup detected! Running tasks for initial setup...")
        log += f"\nBOOT - First time setup detected! Running tasks for initial setup..."
        emojis = {}
        for file in os.listdir(f'{os.path.dirname(os.path.abspath(__file__))}/bot-emojis'):
            if file.endswith((".png", ".gif")):
                try:
                    async with aiofiles.open(f"{os.path.dirname(os.path.abspath(__file__))}/bot-emojis/{file}", mode="rb") as image:
                        emoji_name = os.path.splitext(file)[0]
                        emoji = await bot.create_application_emoji(name=emoji_name, image=await image.read())
                        emojis[emoji_name] = str(emoji)
                        logger.info(f"BOOT - Uploaded emoji: {emoji.name} (ID: {emoji.id})")
                        log += f"\nBOOT - Uploaded emoji: {emoji.name} (ID: {emoji.id})"
                except Exception as e:
                    logger.error(f"BOOT - Failed to upload {emoji_name}: {e}")
                    log += f"\nBOOT - Failed to upload {emoji_name}: {e}"
                    status = 1
        if emojis:
            logger.info("BOOT - Emoji markdowns:")
            log += "\nBOOT - Emoji markdowns:"
            dotenv = await helpers.load_dotenv_dir()
            async with aiofiles.open(dotenv, mode="a") as f:
                for name, markdown in emojis.items():
                    await f.write(f"\n{name.upper()}_EMOJI={markdown}")
                    logger.info(f"BOOT - {name}: {markdown}")
                    log += f"\nBOOT - {name}: {markdown}"
                    await asyncio.sleep(0.1)

        async with aiofiles.open(dotenv, mode="r") as f:
            lines = await f.readlines()
        async with aiofiles.open(dotenv, mode="w") as f:
            found = False
            for line in lines:
                if line.startswith("FIRST_SETUP_DONE="):
                    await f.write("FIRST_SETUP_DONE=True\n")
                    found = True
                else:
                    await f.write(line)
            if not found:
                await f.write("\nFIRST_SETUP_DONE=True\n")

    logger.info(f"BOOT - Fetching slash commands")
    log += f"\nBOOT - Fetching slash commands"
    commands = await bot.tree.fetch_commands(guild=discord.Object(id=await helpers.load_admin_server()))
    commands += await bot.tree.fetch_commands()

    if commands:
        dotenv = await helpers.load_dotenv_dir()
        try:
            async with aiofiles.open(dotenv, mode="a") as f:
                for command in commands:
                    async with aiofiles.open(dotenv, mode="r") as f:
                        lines = await f.readlines()
                    async with aiofiles.open(dotenv, mode="w") as f:
                        found = False
                        while not found:
                            for line in lines:
                                if line.startswith(f"{command.name.upper()}_COMMAND"):
                                    await f.write(f"{command.name.upper()}_COMMAND={command.id}\n")
                                    found = True
                                else:
                                    await f.write(line)
                            if not found:
                                await f.write(f"{command.name.upper()}_COMMAND={command.id}\n")
                                found =True
                    logger.info(f"BOOT - {command.name}: {command.id}")
                    log += f"\nBOOT - {command.name}: {command.id}"
                    await asyncio.sleep(0.1)
        except Exception as e:
            logger.error(f"BOOT - Slash Command {command.name} couldn't get registered in .env file: {e}")
            log += f"\nBOOT - Slash Command {command.name} couldn't get registered in .env file: {e}"
            status = 1

    logger.info("BOOT - Reloading environment variables...")
    log += "\nBOOT - Reloading environment variables..."
    await helpers.load_dotenv_data()

    await bot.change_presence(activity=discord.Game(name="CSR Racing"))
    logger.info("BOOT - Basic presence set")
    log += "\nBOOT - Basic presence set"

    await in_app_logging.send_log(bot, log, status, 2)

async def profile_update():
    today = datetime.datetime.now().date()
    BDAY_MONTH = await helpers.load_bday_month()
    BDAY_DAY = await helpers.load_bday_day()

    if today.month == BDAY_MONTH and today.day == BDAY_DAY:
        BIRTHDAY_PFP_PATH = await helpers.load_asset_path('PfP_Birthday')
        BIRTHDAY_NAME = await helpers.load_bday_name()
        await update_bot_profile(BIRTHDAY_PFP_PATH, BIRTHDAY_NAME)
    elif today.month == 10:
        HALLOWEEN_PFP_PATH = await helpers.load_asset_path('PfP_Halloween')
        HALLOWEEN_NAME = await helpers.load_halloween_name()
        await update_bot_profile(HALLOWEEN_PFP_PATH, HALLOWEEN_NAME)
    elif today.month == 12:
        CHRISTMAS_PFP_PATH = await helpers.load_asset_path('PfP_Christmas')
        CHRISTMAS_NAME = await helpers.load_xmas_name()
        await update_bot_profile(CHRISTMAS_PFP_PATH, CHRISTMAS_NAME)
    else:
        DEFAULT_PFP_PATH = await helpers.load_asset_path('PfP')
        DEFAULT_NAME = await helpers.load_default_name()
        await update_bot_profile(DEFAULT_PFP_PATH, DEFAULT_NAME)

async def update_bot_profile(pfp_path, new_name):
    async with aiofiles.open(pfp_path, mode='rb') as pfp_file:
        bot_pfp = bot.user.avatar
        if bot_pfp != pfp_file:
            try:
                await bot.user.edit(username=new_name, avatar=await pfp_file.read())
                logger.info(f"Updated bot name to '{new_name}' and profile picture.")
            except discord.HTTPException as e:
                logger.info(f"PROFILE - Failed to update bot profile: {e}")
                log = f"PROFILE - Failed to update bot profile: {e}"
                await in_app_logging.send_log(bot, log, 0, 2)

@tasks.loop(minutes=5)
async def schedule_db_updates():
    await tunes_manager.create_database(bot, log="")
    try:
        await database_manager.recreate_database(bot)
        await asyncio.sleep(0.0)
    except Exception as e:
        logger.error(f"EDB - Error during database update: {e}")
        log = f"EDB - Error during database update: {e}"
        await in_app_logging.send_log(bot, log, 0, 2)

@tasks.loop(minutes=30)
async def schedule_version_check():
    try:
        await asyncio.gather(version_check_manager_apps.version_check_task(bot))
        await asyncio.sleep(0.0)
    except Exception as e:
        logger.error(f"VC - Error during version check: {e}")
        log  = f"VC - Error during version check: {e}"
        await in_app_logging.send_log(bot, log, 0, 2)

@tasks.loop(minutes=1)
async def schedule_blog_check():
    try:
        await asyncio.gather(version_check_manager_blog.version_check_task(bot))
        await asyncio.sleep(0.0)
    except Exception as e:
        logger.error(f"Blog - Error during version check: {e}")
        log = f"Blog - Error during version check: {e}"
        await in_app_logging.send_log(bot, log, 0, 2)

@tasks.loop(time=datetime.time(0, 0))
async def schedule_profile_update():
    try:
        await profile_update()
        await asyncio.sleep(1)
    except Exception as e:
        logger.error(f"PROFILE - Error during profile update: {e}")
        log = f"PROFILE - Error during profile update: {e}"
        await in_app_logging.send_log(bot, log, 0, 2)

async def main():
    await bot.start(await helpers.load_token())

if __name__ == "__main__":
    bot.setup_hook = setup_hook
    asyncio.run(main())
