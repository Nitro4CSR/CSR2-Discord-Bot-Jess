import aiofiles
import aiohttp
import discord
import json
import logging
import os
from discord.ext import commands
from bs4 import BeautifulSoup
import helpers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# File to store the last scraped data
BLOG_DATA_FILE = helpers.load_blogversions_json()

async def fetch_latest_blog_post():
    """Fetch the latest blog post's URL and title from the CSR2 news page asynchronously."""
    url = "https://www.csr-racing.com/csr2/csr-news"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception(f"Failed to fetch page: {response.status}")

            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')

            # Iterate through all <a> tags until one with '/news/' in href is found
            for link in soup.find_all('a', href=True):
                if "/news/" in link['href']:
                    # Look for the <header> tag inside the <a> tag
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
        return json.loads(content)

async def save_current_scrape(data):
    """Save the current scrape data to the JSON file asynchronously."""
    async with aiofiles.open(BLOG_DATA_FILE, "w") as file:
        await file.write(json.dumps(data, indent=4))

async def version_check_task(bot: commands.Bot):
    """Main function to check for changes and update the JSON file asynchronously."""
    try:
        last_data = await load_last_scrape()
        logging.info("Blog - Starting Blog check")
        latest_data = await fetch_latest_blog_post()
        logging.info("Blog - Comparing data")

        if last_data != latest_data:
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
    except Exception as e:
        logging.info(f"An error occurred: {e}")

async def announce_changes(changes: list):
    embed = discord.Embed(
        title="A new Blog Post was posted!",
        description=f"{changes['title']}\nhttps://www.csr-racing.com{changes['url']}",
        color=discord.Color(0xff00ff)
    )
    return embed

async def send_changes(bot: commands.Bot, messages: discord.Embed):
    channel_ids = helpers.load_blog_announcement_channels()
    for channel_id in channel_ids:
        try:
            channel = bot.get_channel(int(channel_id))
            if not channel:
                logging.error(f"Channel {channel_id} not found.")
            else:
                await channel.send(embed=messages)
        except Exception as e:
            logging.error(f"Error while trying to send changes to {channel_id}: {e}")
    user_ids = helpers.load_blog_announcement_users()
    for user_id in user_ids:
        try:
            user = bot.get_user(int(user_id))
            if not user:
                logging.error(f"User {user_id} not found.")
            else:
                await user.send(embed=messages)
        except Exception as e:
            logging.error(f"Error while trying to send changes to {user_id}: {e}")
