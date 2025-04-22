import aiofiles
import asyncio
import aiohttp
import discord
import json
import os
from cogs import announce_updates, notify_updates
from discord.ext import commands
from bs4 import BeautifulSoup
import helpers
import in_app_logging

logger = helpers.load_logging()

async def load_headers():
    BLOG_DATA_FILE = await helpers.load_file_path('Blog_versions')
    if not os.path.exists(BLOG_DATA_FILE):
        return {}

    async with aiofiles.open(BLOG_DATA_FILE, "r") as file:
        content = await file.read()
        data = json.loads(content)
        return data.get("headers", {})

async def save_headers(headers):
    BLOG_DATA_FILE = await helpers.load_file_path('Blog_versions')
    if os.path.exists(BLOG_DATA_FILE):
        async with aiofiles.open(BLOG_DATA_FILE, "r") as file:
            content = await file.read()
            data = json.loads(content)
    else:
        data = {}

    data["headers"] = headers

    async with aiofiles.open(BLOG_DATA_FILE, "w") as file:
        await file.write(json.dumps(data, indent=4))

async def fetch_latest_blog_post(log: str, status: int):
    url = "https://www.csr-racing.com/csr2/csr-news"
    headers = await load_headers()
    request_headers = {}

    if "ETag" in headers:
        request_headers["If-None-Match"] = headers["ETag"]

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=request_headers) as response:
            if response.status == 304:
                logger.info("Blog - No new updates (304 Not Modified)")
                log += f"\nBlog - No new updates (304 Not Modified)"
                return None, log, status

            if response.status != 200:
                logger.warning(f"Blog - Failed to fetch page: {response.status}")
                log += f"\nBlog - Failed to fetch page: {response.status}"
                return None, log, status

            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')

            new_headers = {}
            if "ETag" in response.headers:
                new_headers["ETag"] = response.headers["ETag"]
            await save_headers(new_headers)

            for link in soup.find_all('a', href=True):
                if "/news/" in link['href']:
                    header = link.find('header')
                    title = header.get_text(strip=True) if header else None
                    href = link['href']
                    return {"title": title, "url": href}, log, status

            logger.error(f"Blog - No blog post found on the page with '/news/' in the URL.")
            log += f"\nBlog - No blog post found on the page with '/news/' in the URL."
            return None, log, status

async def load_last_scrape():
    BLOG_DATA_FILE = await helpers.load_file_path('Blog_versions')
    if not os.path.exists(BLOG_DATA_FILE):
        return None

    async with aiofiles.open(BLOG_DATA_FILE, "r") as file:
        content = await file.read()
        data = json.loads(content)
        return data.get("blog_data", None)

async def save_current_scrape(data):
    BLOG_DATA_FILE = await helpers.load_file_path('Blog_versions')
    if os.path.exists(BLOG_DATA_FILE):
        async with aiofiles.open(BLOG_DATA_FILE, "r") as file:
            content = await file.read()
            saved_data = json.loads(content)
    else:
        saved_data = {}

    saved_data["blog_data"] = data

    async with aiofiles.open(BLOG_DATA_FILE, "w") as file:
        await file.write(json.dumps(saved_data, indent=4))

async def version_check_task(bot: commands.Bot):
    status = 2
    last_data = await load_last_scrape()
    logger.info("Blog - Starting Blog check")
    log = f"Blog - Starting Blog check"
    latest_data, log, status = await fetch_latest_blog_post(log, status)
    if latest_data is not None:
        logger.info("Blog - Comparing data")
        log += f"\nBlog - Comparing data"

        if latest_data is not None and last_data != latest_data:
            logger.info("Blog - Sending detected Changes")
            log += f"\nBlog - Sending detected Changes"
            messages = await announce_changes(latest_data)
            log, status, check = await send_changes(bot, messages, log)

            logger.info("Blog - Overwriting old data with the new data")
            log += "\nBlog - Overwriting old data with the new data"
            await save_current_scrape(latest_data)
        else:
            logger.info("Blog - No changes detected. Exiting...")
            log += f"\nBlog - No changes detected. Exiting..."
    logger.info("Blog - Blog check completed")
    log += f"\nBlog - Blog check completed"
    await in_app_logging.send_log(bot, log, status if check == 1 else 1, 2)
    last_data = None
    latest_data = None

async def announce_changes(changes: dict):
    embed = discord.Embed(
        title="A new Blog Post was posted!",
        description=f"{changes['title']}\nhttps://www.csr-racing.com{changes['url']}",
        color=discord.Color(0xff00ff)
    )

    return embed

async def send_changes(bot: commands.Bot, messages: discord.Embed, log: str):
    status = 2
    channel_ids = await helpers.load_file('Blog announcement channel file')
    for channel_id in channel_ids:
        try:
            channel = bot.get_channel(int(channel_id))
            if not channel:
                logger.error(f"Blog - Channel {channel_id} not found.")
                log += f"Blog - Channel {channel_id} not found."
                status = 1
            else:
                await channel.send(embed=messages)
                await asyncio.sleep(3)
        except discord.Forbidden as e:
            logger.error(f"Blog - Error while trying to send changes to {channel_id}: {e}")
            log += f"Blog - Error while trying to send changes to {channel_id}: {e}"
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
                            description=f"Sending App updates failed in **{channel.guild.name}** in the channel **{channel.name}**.\nThe following permissions are not present: **{missing_perms_text}**\nPlease update the bot's permissions to ensure proper functionality.",
                            color=discord.Color(0xff0000)
                        )
                        embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')
                        await admin.send(embed=embed)
                    except Exception as e:
                        logger.error(f"Blog - Error while notifying Admin {admin.name} of {channel.guild.name}: {e}")
                        log += f"\nBlog - Error while notifying Admin {admin.name} of {channel.guild.name}: {e}"
                        status = 0
        except discord.NotFound as e:
            check, log, status = announce_updates.process_request(channel_id, "Blog", 0, log)
        except Exception as e:
            logger.error(f"Blog - Error while trying to send changes to {channel_id}: {e}")
            log += f"Blog - Error while trying to send changes to {channel_id}: {e}"
            status = 1
    user_ids = await helpers.load_file('Blog announcement user file')
    for user_id in user_ids:
        try:
            user = bot.get_user(int(user_id))
            if not user:
                logger.error(f"Blog - User {user_id} not found.")
                log += f"Blog - User {user_id} not found."
                status = 1
            else:
                await user.send(embed=messages)
                await asyncio.sleep(3)
        except discord.Forbidden as e:
            check, log, status = await notify_updates.process_request(user_id, "Blog", 0, log)
        except discord.NotFound as e:
            check, log, status = await notify_updates.process_request(user_id, "Blog", 0, log)
        except Exception as e:
            logger.error(f"Blog - Error while trying to send changes to {user_id}: {e}")
            log += f"Blog - Error while trying to send changes to {user_id}: {e}"
            status = 1

    return log, status, check
