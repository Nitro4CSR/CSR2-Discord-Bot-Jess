import aiofiles
import asyncio
import aiohttp
import discord
import json
import logging
import os
import re
from cogs import announce_updates, notify_updates
from discord.ext import commands
from bs4 import BeautifulSoup
import helpers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

BLOG_DATA_FILE = helpers.load_blogversions_json()

async def load_headers():
    if not os.path.exists(BLOG_DATA_FILE):
        return {}

    async with aiofiles.open(BLOG_DATA_FILE, "r") as file:
        content = await file.read()
        data = json.loads(content)
        return data.get("headers", {})  # Get the headers part of the data (or empty dict if not present)

async def save_headers(headers):
    if os.path.exists(BLOG_DATA_FILE):
        # Load existing data first to preserve other parts of the JSON
        async with aiofiles.open(BLOG_DATA_FILE, "r") as file:
            content = await file.read()
            data = json.loads(content)
    else:
        data = {}

    # Update or set the headers part of the data
    data["headers"] = headers

    # Save the updated data back to the file
    async with aiofiles.open(BLOG_DATA_FILE, "w") as file:
        await file.write(json.dumps(data, indent=4))

async def fetch_latest_blog_post():
    """Fetch the latest blog post's URL and title from the CSR2 news page asynchronously, using ETag caching."""
    url = "https://www.csr-racing.com/csr2/csr-news"
    headers = await load_headers()  # Load headers (ETag) from BLOG_DATA_FILE
    request_headers = {}

    if "ETag" in headers:
        request_headers["If-None-Match"] = headers["ETag"]

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=request_headers) as response:
            if response.status == 304:
                logging.info("Blog - No new updates (304 Not Modified)")
                return None  # No changes, return None

            if response.status != 200:
                raise Exception(f"Failed to fetch page: {response.status}")

            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')

            # Save ETag if present
            new_headers = {}
            if "ETag" in response.headers:
                new_headers["ETag"] = response.headers["ETag"]
            await save_headers(new_headers)  # Save ETag in BLOG_DATA_FILE

            for link in soup.find_all('a', href=True):
                if "/news/" in link['href']:
                    header = link.find('header')
                    title = header.get_text(strip=True) if header else None
                    href = link['href']
                    return {"title": title, "url": href}

            raise Exception("No blog post found on the page with '/news/' in the URL.")

async def load_last_scrape():
    """Load the last scraped data from the JSON file asynchronously."""
    if not os.path.exists(BLOG_DATA_FILE):
        return None

    async with aiofiles.open(BLOG_DATA_FILE, "r") as file:
        content = await file.read()
        data = json.loads(content)
        return data.get("blog_data", None)  # Get the actual blog data part (or None if not present)

async def save_current_scrape(data):
    """Save the current scrape data to the JSON file asynchronously."""
    if os.path.exists(BLOG_DATA_FILE):
        # Load existing data first to preserve other parts of the JSON
        async with aiofiles.open(BLOG_DATA_FILE, "r") as file:
            content = await file.read()
            saved_data = json.loads(content)
    else:
        saved_data = {}

    # Update or set the blog data part of the file
    saved_data["blog_data"] = data

    # Save the updated data back to the file
    async with aiofiles.open(BLOG_DATA_FILE, "w") as file:
        await file.write(json.dumps(saved_data, indent=4))

async def version_check_task(bot: commands.Bot):
    """Main function to check for changes and update the JSON file asynchronously."""
    try:
        last_data = await load_last_scrape()
        logging.info("Blog - Starting Blog check")
        latest_data = await fetch_latest_blog_post()
        if latest_data is not None:
            logging.info("Blog - Comparing data")

            if last_data != latest_data and latest_data is not None:
                # Log the change to the console
                logging.info("Blog - Sending detected Changes")
                messages = await announce_changes(latest_data)
                await send_changes(bot, messages)

                # Save the new data
                logging.info("Blog - Overwriting old data with the new data")
                await save_current_scrape(latest_data)
            else:
                logging.info("Blog - No changes detected. Exiting...")
        logging.info("Blog - Blog check completed")
        last_data = None
        latest_data = None
    except Exception as e:
        logging.info(f"Blog - An error occurred: {e}")

async def announce_changes(changes: dict):
    embed = discord.Embed(
        title="A new Blog Post was posted!",
        description=f"{changes['title']}\nhttps://www.csr-racing.com{changes['url']}",
        color=discord.Color(0xff00ff)
    )
    return embed

async def send_changes(bot: commands.Bot, messages: discord.Embed):
    channel_ids = await helpers.load_blog_announcement_channels()
    for channel_id in channel_ids:
        try:
            channel = bot.get_channel(int(channel_id))
            if not channel:
                logging.error(f"Channel {channel_id} not found.")
            else:
                await channel.send(embed=messages)
                await asyncio.sleep(3)
        except discord.Forbidden as e:
            logging.error(f"Error while trying to send changes to {channel_id}: {e}")
            permission_ids = re.findall(r"\b\d{15,}\b", e)
            discord_permissions = helpers.load_perms_dic()
            if permission_ids:
                for permission_id in permission_ids:
                    permissions = [perm for perm, value in discord_permissions.items() if permission_id & value]
            guild = channel.guild
            admins = [member for member in guild.members if member.guild_permissions.administrator]
            if admins:
                for admin in admins:
                    try:
                        admin.send(f"I detected missing permissions on the server {guild.name} in the channel {channel.name} for me to be able to send Blog updates.\nThe following permissions are missing: {permissions}")
                    except Exception as e:
                        logging.error(f"Error while trying to send permissions notice to {admin.name} from {guild.name}: {e}")
        except discord.NotFound as e:
            announce_updates.delete_channel(channel_id, scope="Blog")
        except Exception as e:
            logging.error(f"Error while trying to send changes to {channel_id}: {e}")
    user_ids = await helpers.load_blog_announcement_users()
    for user_id in user_ids:
        try:
            user = bot.get_user(int(user_id))
            if not user:
                logging.error(f"User {user_id} not found.")
            else:
                await user.send(embed=messages)
                await asyncio.sleep(3)
        except discord.Forbidden as e:
            notify_updates.delete_user(user_id, scope="Blog")
        except discord.NotFound as e:
            notify_updates.delete_user(user_id, scope="Blog")
        except Exception as e:
            logging.error(f"Error while trying to send changes to {user_id}: {e}")
