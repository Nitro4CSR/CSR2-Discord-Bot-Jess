import asyncio
import aiohttp
import discord
from cogs import announceupdates, notifyupdates
from discord.ext import commands
from bs4 import BeautifulSoup
import helpers
import in_app_logging

logger = helpers.load_logging()

async def version_check_task(bot: commands.Bot):
    global header
    header = bot.localisation.get('BLOG_LOG_HEADER')
    status = 2
    last_data = await load_last_scrape()
    logger.info(f"{header}{bot.localisation.get('BLOG_LOG_UPDATE_CHECK_START')}")
    log = f"{header}{bot.localisation.get('BLOG_LOG_UPDATE_CHECK_START')}"
    latest_data, log, status = await fetch_latest_blog_post(log, status)
    if latest_data is not None:
        logger.info(f"{header}Comparing data")
        log += f"\n{header}Comparing data"

        if latest_data is not None and last_data != latest_data:
            logger.info(f"{header}{bot.localisation.get('BLOG_LOG_UPDATE_CHECK_COMPARE_DATA')}")
            log += f"\n{header}{bot.localisation.get('BLOG_LOG_UPDATE_CHECK_COMPARE_DATA')}"
            messages = await announce_changes(latest_data)
            log, status, check = await send_changes(bot, messages, log)

            logger.info(f"{header}{bot.localisation.get('BLOG_LOG_UPDATE_CHECK_SAVE_SCRAPE')}")
            log += f"\n{header}{bot.localisation.get('BLOG_LOG_UPDATE_CHECK_SAVE_SCRAPE')}"
            await save_current_scrape(latest_data)
        else:
            logger.info(f"{header}{bot.localisation.get('BLOG_LOG_UPDATE_CHECK_DONE_UNCHANGED')}")
            log += f"\n{header}{bot.localisation.get('BLOG_LOG_UPDATE_CHECK_DONE_UNCHANGED')}"
    logger.info(f"{header}{bot.localisation.get('BLOG_LOG_UPDATE_CHECK_DONE')}")
    log += f"\n{header}{bot.localisation.get('BLOG_LOG_UPDATE_CHECK_DONE')}"
    await in_app_logging.send_log(bot, log, status, 2)
    last_data = None
    latest_data = None

async def load_headers():
    data = await helpers.load_file("Blog_versions")
    if data is None:
        return {}
    else:
        return data.get("headers", {})

async def save_headers(headers):
    data = await helpers.load_file("Blog_versions")
    if data is None:
        data = {}
    data["headers"] = headers
    await helpers.save_file("Blog_versions", data)

async def fetch_latest_blog_post(log: str, status: int):
    localisation = {k: k for k in helpers.load_file("localisation")} if await helpers.load_json_key("config", "DebugMode") else await helpers.load_file("localisation")
    global header
    url = "https://www.csr-racing.com/csr2/csr-news"
    headers = await load_headers()
    request_headers = {}

    if "ETag" in headers:
        request_headers["If-None-Match"] = headers["ETag"]

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=request_headers) as response:
            if response.status == 304:
                logger.info(f"{header}{localisation.get('BLOG_LOG_UPDATE_CHECK_UNCHANGED')}")
                log += f"\n{header}{localisation.get('BLOG_LOG_UPDATE_CHECK_UNCHANGED')}"
                return None, log, status

            if response.status != 200:
                logger.warning(f"{header}{localisation.get('BLOG_LOG_UPDATE_CHECK_ERROR_FETCH')} {response.status}")
                log += f"\n{header}{localisation.get('BLOG_LOG_UPDATE_CHECK_ERROR_FETCH')} {response.status}"
                return None, log, status

            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')

            new_headers = {}
            if "ETag" in response.headers:
                new_headers["ETag"] = response.headers["ETag"]
            await save_headers(new_headers)

            for link in soup.find_all('a', href=True):
                if "/news/" in link['href']:
                    blog_header = link.find('header')
                    title = blog_header.get_text(strip=True) if blog_header else None
                    href = link['href']
                    return {"title": title, "url": href}, log, status

            logger.error(f"{header}{localisation.get('BLOG_LOG_UPDATE_CHECK_ERROR_NOT_FOUND')}")
            log += f"\n{header}{localisation.get('BLOG_LOG_UPDATE_CHECK_ERROR_NOT_FOUND')}"
            return None, log, status

async def load_last_scrape():
    data = await helpers.load_file("Blog_versions")
    if data is None:
        return None
    else:
        return data.get("blog_data", None)

async def save_current_scrape(scrape_data):
    data = await helpers.load_file("Blog_versions")
    if data is None:
        data = {}
    data["blog_data"] = scrape_data
    await helpers.save_file("Blog_versions", data)

async def announce_changes(changes: dict):
    embed = discord.Embed(
        title="A new Blog Post was posted!",
        description=f"{changes['title']}\nhttps://www.csr-racing.com{changes['url']}",
        color=discord.Color(0xff00ff)
    )

    return embed

async def send_changes(bot: commands.Bot, messages: discord.Embed, log: str):
    global header
    status = 2
    check = 1
    channel_ids = await helpers.load_file('Blog announcement channel file')
    for channel_id in channel_ids:
        try:
            channel = bot.get_channel(int(channel_id))
            if not channel:
                logger.error(f"{header}{bot.localisation.get('LOG_UPDATE_CHECK_ERROR_NO_CHANNEL')} ({channel_id})")
                log += f"{header}{bot.localisation.get('LOG_UPDATE_CHECK_ERROR_NO_CHANNEL')} ({channel_id})"
                status = 1
            else:
                await channel.send(embed=messages)
                await asyncio.sleep(3)
        except discord.Forbidden as e:
            logger.error(f"{header}{bot.localisation.get('LOG_UPDATE_CHECK_ERROR_FORBIDDEN')} {channel_id}: {e}")
            log += f"{header}{bot.localisation.get('LOG_UPDATE_CHECK_ERROR_FORBIDDEN')} {channel_id}: {e}"
            status = 1
            bot_permissions = channel.permissions_for(channel.guild.me)
            required_permissions = await helpers.load_perms_dic()
            missing_permissions = [perm_name for perm, perm_name in required_permissions.items() if not getattr(bot_permissions, perm, False)]
            admins = [member for member in channel.guild.members if member.guild_permissions.administrator]
            if admins and missing_permissions:
                missing_perms_text = ", ".join(missing_permissions)
                for admin in admins:
                    try:
                        embed=discord.Embed(
                            title="I'm missing permissions!",
                            description=f"Sending Blog updates failed in **{channel.guild.name}** in the channel **{channel.name}**.\nThe following permissions are not present: **{missing_perms_text}**\nPlease update the bot's permissions to ensure proper functionality.",
                            color=discord.Color(0xff0000)
                        )
                        embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')
                        await admin.send(embed=embed)
                    except Exception as e:
                        logger.error(f"{header}{bot.localisation.get('LOG_UPDATE_CHECK_ERROR_SEND')} {admin.name} 🏠{channel.guild.name}: {e}")
                        log += f"\n{header}{bot.localisation.get('LOG_UPDATE_CHECK_ERROR_SEND')} {admin.name} 🏠{channel.guild.name}: {e}"
                        status = 0
        except discord.NotFound as e:
            check, log, status = await announceupdates.process_request(channel_id, "Blog", request = 0, log = log)
        except Exception as e:
            logger.error(f"{header}{bot.localisation.get('LOG_UPDATE_CHECK_ERROR_SEND_CHANNEL')} {channel_id}: {e}")
            log += f"{header}{bot.localisation.get('LOG_UPDATE_CHECK_ERROR_SEND_CHANNEL')} {channel_id}: {e}"
            status = 1
    user_ids = await helpers.load_file('Blog announcement user file')
    for user_id in user_ids:
        try:
            user = bot.get_user(int(user_id))
            if not user:
                logger.error(f"{header}User {user_id} not found.")
                log += f"{header}User {user_id} not found."
                status = 1
            else:
                await user.send(embed=messages)
                await asyncio.sleep(3)
        except discord.Forbidden as e:
            check, log, status = await notifyupdates.process_request(user_id, "Blog", request = 0, log = log)
        except discord.NotFound as e:
            check, log, status = await notifyupdates.process_request(user_id, "Blog", request = 0, log = log)
        except Exception as e:
            logger.error(f"{header}{bot.localisation.get('LOG_UPDATE_CHECK_ERROR_SEND_USER')} {user_id}: {e}")
            log += f"{header}Er{bot.localisation.get('LOG_UPDATE_CHECK_ERROR_SEND_USER')} {user_id}: {e}"
            status = 1

    return log, status, check
