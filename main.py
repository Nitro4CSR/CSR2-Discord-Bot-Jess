import discord
from discord.ext import commands, tasks
import aiofiles
import asyncio
import datetime
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

db_update_timer = None
version_check_timer = None
blog_check_timer = None
status_change_timer = None


async def load_cogs():
    for filename in os.listdir(f'{os.path.dirname(os.path.abspath(__file__))}/cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')


async def setup_hook():
    global db_update_timer, version_check_timer, blog_check_timer, status_change_timer
    db_update_timer = 60 / await helpers.load_json_key("config", "DB_UpdatesPerHour")
    version_check_timer = 60 / await helpers.load_json_key("config", "VersionChecksPerHour")
    blog_check_timer = 60 / await helpers.load_json_key("config", "BlogChecksPerHour")
    status_change_timer = 60 / await helpers.load_json_key("config", "DynamicStatusUpdatesPerHour")

    schedule_db_updates.change_interval(minutes=db_update_timer)
    schedule_version_check.change_interval(minutes=version_check_timer)
    schedule_blog_check.change_interval(minutes=blog_check_timer)
    schedule_dynamic_status_change.change_interval(minutes=status_change_timer)

    bot.localisation = {k: k for k in helpers.load_file("localisation")} if await helpers.load_json_key("config", "DebugMode") else await helpers.load_file("localisation")

    await load_cogs()
    await bot.tree.sync()


@bot.event
async def on_ready():
    log = ""
    header = bot.localisation.get('BOOT_LOG_HEADER')
    logger.info(f"{header}{bot.localisation.get('BOOT_LOG_BOT_LOGIN')} {bot.user.name} ({bot.user.id})")
    log += f"{header}{bot.localisation.get('BOOT_LOG_BOT_LOGIN')} {bot.user.name} ({bot.user.id})"
    status = 2
    if os.path.exists(await helpers.load_file_path('version')):
        version = set(await helpers.load_file('version'))
    else:
        version = {'INITIAL', 'INITIAL'}
        await helpers.save_file('version', ['INITIAL', 'INITIAL'])
    if len(list(set(version))) > 1:
        logger.info(f"{header}{bot.localisation.get('BOOT_LOG_SOURCE_CODE_VERSION_UPDATE')} {list(version)[1]} ➡️ {list(version)[0]}")
        log += f"{header}{bot.localisation.get('BOOT_LOG_SOURCE_CODE_VERSION_UPDATE')} {list(version)[1]} ➡️ {list(version)[0]}\n"
        await helpers.save_file('version', [list(version)[0], list(version)[0]])

    if not schedule_db_updates.is_running():
        logger.info(f"{header}{bot.localisation.get('BOOT_LOG_EDB_TASK_SCHEDULE_START')}")
        log += f"\n{header}{bot.localisation.get('BOOT_LOG_EDB_TASK_SCHEDULE_START')}"
        schedule_db_updates.start()
    if not schedule_version_check.is_running():
        logger.info(f"{header}{bot.localisation.get('BOOT_LOG_VERSION_CHECK_TASK_SCHEDULE_START')}")
        log += f"\n{header}{bot.localisation.get('BOOT_LOG_VERSION_CHECK_TASK_SCHEDULE_START')}"
        schedule_version_check.start()
    if not schedule_blog_check.is_running():
        logger.info(f"{header}{bot.localisation.get('BOOT_LOG_BLOG_TASK_SCHEDULE_START')}")
        log += f"\n{header}{bot.localisation.get('BOOT_LOG_BLOG_TASK_SCHEDULE_START')}"
        schedule_blog_check.start()
    if not schedule_profile_update.is_running():
        logger.info(f"{header}{bot.localisation.get('BOOT_LOG_IDENTITY_UPDATE_TASK_SCHEDULE_START')}")
        log += f"\n{header}{bot.localisation.get('BOOT_LOG_IDENTITY_UPDATE_TASK_SCHEDULE_START')}"
        schedule_profile_update.start()
    if not schedule_dynamic_status_change.is_running():
        logger.info(f"{header}{bot.localisation.get('BOOT_LOG_DYNAMIC_STATUS_TASK_SCHEDULE_START')}")
        log += f"\n{header}{bot.localisation.get('BOOT_LOG_DYNAMIC_STATUS_TASK_SCHEDULE_START')}"
        schedule_dynamic_status_change.start(bot)

    try:
        ADMIN_SERVERS = await helpers.load_json_key("config", "ClientAdminServers")
        ADMIN_SERVERS = [int(s) for s in ADMIN_SERVERS]
        for server in ADMIN_SERVERS:
            admin_guild = bot.get_guild(int(server))
            logger.info(f"{header}{bot.localisation.get('BOOT_LOG_SYNC_CMD_ADMIN_SERVER_START')} {admin_guild.name}")
            log += f"\n{header}{bot.localisation.get('BOOT_LOG_SYNC_CMD_ADMIN_SERVER_START')} {admin_guild.name}"
            await bot.tree.sync(guild=discord.Object(id=int(server)))
            logger.info(f"{header}{bot.localisation.get('BOOT_LOG_SYNC_CMD_ADMIN_SERVER_DONE')} {admin_guild.name}")
            log += f"\n{header}{bot.localisation.get('BOOT_LOG_SYNC_CMD_ADMIN_SERVER_DONE')} {admin_guild.name}"
    except Exception as e:
        logger.error(f"{header}{bot.localisation.get('BOOT_LOG_SYNC_CMD_ADMIN_SERVER_FAIL')} {e}")
        log += f"\n{header}{bot.localisation.get('BOOT_LOG_SYNC_CMD_ADMIN_SERVER_FAIL')} {e}"
        status = 0

    FIRST_SETUP_DONE = await helpers.load_json_key("config", "FirstSetupDone")

    if not FIRST_SETUP_DONE:
        logger.info(f"{header}{bot.localisation.get('BOOT_LOG_FIRST_SETUP_NOTICE')}")
        log += f"\n{header}{bot.localisation.get('BOOT_LOG_FIRST_SETUP_NOTICE')}"
        for file in os.listdir(f'{os.path.dirname(os.path.abspath(__file__))}/bot-emojis'):
            if file.endswith((".png", ".gif")):
                try:
                    async with aiofiles.open(f"{os.path.dirname(os.path.abspath(__file__))}/bot-emojis/{file}", mode="rb") as image:
                        emoji_name = os.path.splitext(file)[0]
                        emoji = await bot.create_application_emoji(name=emoji_name, image=await image.read())
                    logger.info(f"{header}{bot.localisation.get('BOOT_LOG_FIRST_SETUP_EMOJI_UPLOAD_DONE')} {emoji.name} ({emoji.id})")
                    log += f"\n{header}{bot.localisation.get('BOOT_LOG_FIRST_SETUP_EMOJI_UPLOAD_DONE')} {emoji.name} ({emoji.id})"
                except Exception as e:
                    logger.error(f"{header}{emoji_name} {bot.localisation.get('BOOT_LOG_FIRST_SETUP_EMOJI_UPLOAD_FAIL')} {e}")
                    log += f"\n{header}{emoji_name} {bot.localisation.get('BOOT_LOG_FIRST_SETUP_EMOJI_UPLOAD_FAIL')} {str(e)[:35]}"
                    status = 1

        config = await helpers.load_file("config")
        config["FirstSetupDone"] = True
        await helpers.save_file("config", config)

    session_variables = {}
    logger.info(f"{header}{bot.localisation.get('BOOT_LOG_SESSION_VAR_NOTICE')}")
    log += f"\n{header}{bot.localisation.get('BOOT_LOG_SESSION_VAR_NOTICE')}"
    logger.info(f"{header}{bot.localisation.get('BOOT_LOG_SESSION_VAR_FETCH_CMD')}")
    log += f"\n{header}{bot.localisation.get('BOOT_LOG_SESSION_VAR_FETCH_CMD')}"
    commands = await bot.tree.fetch_commands(guild=discord.Object(id=list(await helpers.load_json_key("config", "ClientAdminServers"))[0]))
    commands += await bot.tree.fetch_commands()
    logger.info(f"{header}{bot.localisation.get('BOOT_LOG_SESSION_VAR_FETCH_EMOJI')}")
    log += f"\n{header}{bot.localisation.get('BOOT_LOG_SESSION_VAR_FETCH_EMOJI')}"
    emojis = await bot.fetch_application_emojis()
    if commands:
        for command in commands:
            session_variables[f"{command.name.upper()}_CMD"] = command.id
    if emojis:
        for emoji in emojis:
            session_variables[f"{emoji.name.upper()}_EMOJI"] = f"<a:{emoji.name}:{emoji.id}>" if emoji.animated else f"<:{emoji.name}:{emoji.id}>"
    await helpers.save_file("session", session_variables)
    logger.info(f"{header}{bot.localisation.get('BOOT_LOG_SESSION_VAR_SAVED')}")
    log += f"\n{header}{bot.localisation.get('BOOT_LOG_SESSION_VAR_SAVED')}"

    if await helpers.load_json_key("status", "IsStaticStatusActive"):
        await helpers.change_presence(bot, await helpers.load_json_key("status", "StaticStatusType"), await helpers.load_json_key("status", "StaticStatusText"), await helpers.load_json_key("status", "StaticStatusURL"))
    else:
        await helpers.set_dynamic_status(bot)
        logger.info(f"{header}{bot.localisation.get('BOOT_LOG_PRESSENCE_DONE')}")
        log += f"\n{header}{bot.localisation.get('BOOT_LOG_PRESSENCE_DONE')}"
    await in_app_logging.send_log(bot, log, status if status else 2, 2)

async def profile_update():
    today = datetime.datetime.now().date()
    BDAY_MONTH = await helpers.load_json_key("config", "BirthdayMonth")
    BDAY_DAY = await helpers.load_json_key("config", "BirthdayDay")

    if today.month == BDAY_MONTH and today.day == BDAY_DAY:
        BIRTHDAY_PFP_PATH = await helpers.load_file_path('PfP_Birthday')
        BIRTHDAY_NAME = await helpers.load_json_key("config", "ClientName_Birthday")
        await update_bot_profile(BIRTHDAY_PFP_PATH, BIRTHDAY_NAME)
    elif today.month == 10:
        HALLOWEEN_PFP_PATH = await helpers.load_file_path('PfP_Halloween')
        HALLOWEEN_NAME = await helpers.load_json_key("config", "ClientName_Halloween")
        await update_bot_profile(HALLOWEEN_PFP_PATH, HALLOWEEN_NAME)
    elif today.month == 12:
        CHRISTMAS_PFP_PATH = await helpers.load_file_path('PfP_Christmas')
        CHRISTMAS_NAME = await helpers.load_json_key("config", "ClientName_Christmas")
        await update_bot_profile(CHRISTMAS_PFP_PATH, CHRISTMAS_NAME)
    else:
        DEFAULT_PFP_PATH = await helpers.load_file_path('PfP')
        DEFAULT_NAME = await helpers.load_json_key("config", "ClientName_Default")
        await update_bot_profile(DEFAULT_PFP_PATH, DEFAULT_NAME)

async def update_bot_profile(pfp_path, new_name):
    log = ""
    header = bot.localisation.get('IDENTITY_UPDATE_LOG_HEADER')
    logger.info(f"{header}{bot.localisation.get('IDENTITY_UPDATE_LOG_START')}")
    log += f"{header}{bot.localisation.get('IDENTITY_UPDATE_LOG_START')}"
    async with aiofiles.open(pfp_path, mode='rb') as pfp_file:
        bot_pfp = bot.user.avatar
        if bot_pfp.to_file() != pfp_file:
            try:
                await bot.user.edit(username=new_name, avatar=await pfp_file.read())
                logger.info(f"{header}{bot.localisation.get('IDENTITY_UPDATE_LOG_DONE')}")
                log += f"\n{header}{bot.localisation.get('IDENTITY_UPDATE_LOG_DONE')}"
            except discord.HTTPException as e:
                logger.info(f"{header}{bot.localisation.get('IDENTITY_UPDATE_LOG_FAIL')} {e}")
                log += f"\n{header}{bot.localisation.get('IDENTITY_UPDATE_LOG_FAIL')} {e}"
                await in_app_logging.send_log(bot, log, 0, 2)

@tasks.loop(time=datetime.time(0, 0))
async def schedule_profile_update():
    try:
        await profile_update()
        await asyncio.sleep(1)
    except Exception as e:
        logger.error(f"{bot.localisation.get('IDENTITY_UPDATE_LOG_HEADER')}{bot.localisation.get('IDENTITY_UPDATE_LOG_FAIL')} {e}")
        log = f"{bot.localisation.get('IDENTITY_UPDATE_LOG_HEADER')}{bot.localisation.get('IDENTITY_UPDATE_LOG_FAIL')} {e}"
        await in_app_logging.send_log(bot, log, 0, 2)

@tasks.loop(minutes=1)
async def schedule_db_updates():
    header = bot.localisation.get('EDB_LOG_HEADER')
    await tunes_manager.create_database(bot)
    try:
        await database_manager.recreate_database(bot)
        await asyncio.sleep(0.0)
    except Exception as e:
        logger.error(f"{header}{bot.localisation.get('EDB_LOG_UPDATE_FAIL')} {e}")
        log = f"{header}{bot.localisation.get('EDB_LOG_UPDATE_FAIL')} {e}"
        await in_app_logging.send_log(bot, log, 0, 2)


@tasks.loop(minutes=1)
async def schedule_version_check():
    header = bot.localisation.get('VERSIONCHECK_LOG_HEADER')
    try:
        await version_check_manager_apps.version_check_task(bot)
        await asyncio.sleep(0.0)
    except Exception as e:
        logger.error(f"{header}{bot.localisation.get('VERSION_CHECK_LOG_FAIL')} {e}")
        log = f"{header}{bot.localisation.get('VERSION_CHECK_LOG_FAIL')} {e}"
        await in_app_logging.send_log(bot, log, 0, 2)


@tasks.loop(minutes=1)
async def schedule_blog_check():
    try:
        await version_check_manager_blog.version_check_task(bot)
        await asyncio.sleep(0.0)
    except Exception as e:
        logger.error(f"{bot.localisation.get('IDENTITY_UPDATE_LOG_HEADER')}"
                     f"{bot.localisation.get('BLOG_LOG_UPDATE_CHECK_FAIL')} {e}")
        log = (f"{bot.localisation.get('IDENTITY_UPDATE_LOG_HEADER')}"
               f"{bot.localisation.get('BLOG_LOG_UPDATE_CHECK_FAIL')} {e}")
        await in_app_logging.send_log(bot, log, 0, 2)


@tasks.loop(minutes=1)
async def schedule_dynamic_status_change(bot: commands.Bot):
    try:
        await helpers.set_dynamic_status(bot)
        await asyncio.sleep(0.0)
    except Exception as e:
        logger.error(f"{bot.localisation.get('DYNAMIC_STATUS_LOG_HEADER')}"
                     f"{bot.localisation.get('DYNAMIC_STATUS_LOG_FAIL')} {e}")
        log = (f"{bot.localisation.get('DYNAMIC_STATUS_LOG_HEADER')}"
               f"{bot.localisation.get('DYNAMIC_STATUS_LOG_FAIL')} {e}")
        await in_app_logging.send_log(bot, log, 0, 2)


async def main():
    bot.setup_hook = setup_hook
    await bot.start(await helpers.load_token())


if __name__ == "__main__":
    asyncio.run(main())
