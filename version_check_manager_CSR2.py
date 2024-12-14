import asyncio
import json
import logging
import os
import discord
from discord.ext import commands
from datetime import datetime
from google_play_scraper import app as google_play_app
from itunes_app_scraper.scraper import AppStoreScraper  # Correct import for AppStoreScraper
from concurrent.futures import ThreadPoolExecutor
import pycountry
import helpers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Define a list of country codes
GP_COUNTRIES = ["us", "gb", "de", "fr", "jp", "in", "br", "ca", "au", "ru", "es", "it", "nl", "se", "no", "dk", "fi", "kr", "cn", "za", "mx", "ar", "cl", "co", "id", "ph", "th", "vn", "my", "sg", "hk", "tw"]
AS_COUNTRIES = ["ae", "ag", "ai", "al", "am", "ar", "at", "au", "az", "bb", "be", "bf", "bg", "bh", "bj", "bm", "bn", "bo", "br", "bs", "bt", "bw", "bz", "ca", "cg", "ch", "ci", "cl", "cm", "co", "cr", "cv", "cy", "cz", "de", "dk", "dm", "do", "dz", "ec", "ee", "eg", "es", "fi", "fj", "fr", "ga", "gb", "gd", "gh", "gm", "gr", "gt", "gw", "gy", "hk", "hn", "hr", "hu", "id", "ie", "il", "in", "is", "it", "jm", "jo", "jp", "ke", "kg", "kn", "kr", "kw", "ky", "kz", "lb", "lc", "lk", "lr", "lt", "lu", "lv", "md", "mg", "mk", "ml", "mn", "mo", "mr", "ms", "mt", "mu", "mw", "mx", "my", "mz", "na", "ne", "ng", "ni", "nl", "no", "np", "nz", "om", "pa", "pe", "pg", "ph", "pk", "pl", "pt", "pw", "py", "qa", "ro", "rs", "sa", "sb", "sc", "se", "sg", "si", "sk", "sn", "sr", "st", "sv", "sz", "tc", "td", "th", "tj", "tm", "tn", "tr", "tt", "tw", "tz", "ug", "us", "uy", "uz", "vc", "ve", "vg", "vn", "ye", "za", "zw"]

# Define the app's details
PACKAGE_NAME = "com.naturalmotion.customstreetracer2"  # App Package Name
APP_STORE_APP_ID = "887947640"  # App AppStore ID

# File paths for storing data
CSR2_DATA_FILE = helpers.load_CSR2versions_json()

# Initialize the ThreadPoolExecutor for async computation
executor = ThreadPoolExecutor(max_workers=10)

# Function for fetching App Store data using `itunes_app_scraper`
def fetch_app_store_data(app_id, country):
    try:
        scraper = AppStoreScraper()  # Create an instance without arguments
        result = scraper.get_app_details(app_id, country)  # Use the fetch method to retrieve app details
        dt = datetime.strptime(result.get("currentVersionReleaseDate", "N/A"), "%Y-%m-%dT%H:%M:%SZ")
        currentVersionReleaseDateEpoch = int(dt.timestamp())
        return {
            "country": country,
            "version": result.get("version", "N/A"),
            "last_updated": currentVersionReleaseDateEpoch,
        }
    except Exception as e:
        return {"country": country, "error": str(e)}

# Function to run blocking `fetch_app_store_data` in a separate thread
def async_fetch_app_store_data(app_id, country):
    loop = asyncio.get_event_loop()
    return loop.run_in_executor(executor, fetch_app_store_data, app_id, country)

# Google Play scraping logic (unchanged)
async def fetch_google_play_data(package_name, country):
    try:
        result = google_play_app(package_name, lang="en", country=country)
        return {
            "country": country,
            "version": result.get("version", "N/A"),
            "last_updated": result.get("updated", "N/A"),
        }
    except Exception as e:
        return {"country": country, "error": str(e)}

# Fetch all data
async def fetch_data():
    google_play_tasks = [fetch_google_play_data(PACKAGE_NAME, country) for country in GP_COUNTRIES]
    app_store_tasks = [async_fetch_app_store_data(APP_STORE_APP_ID, country) for country in AS_COUNTRIES]
    
    google_play_results = await asyncio.gather(*google_play_tasks)
    app_store_results = await asyncio.gather(*app_store_tasks)  # Use async fetch for App Store

    return {"Google Play": google_play_results, "App Store": app_store_results}

# Helper functions for loading and saving data
def load_previous_data():
    """Load the previous data from the JSON file."""
    if os.path.exists(CSR2_DATA_FILE):
        with open(CSR2_DATA_FILE, "r") as file:
            return json.load(file)
    return {}

def save_data(data):
    """Save the current data to the JSON file."""
    with open(CSR2_DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Detect changes between old and new data
def detect_changes(old_data, new_data):
    """Compare old data with new data and detect changes."""
    changes = []
    
    for platform in new_data:
        for new_entry in new_data[platform]:
            country = new_entry.get("country")
            new_version = new_entry.get("version")
            new_last_updated = new_entry.get("last_updated")
            
            # Find the corresponding old entry
            old_entry = next((entry for entry in old_data.get(platform, []) if entry.get("country") == country), {})
            old_version = old_entry.get("version")
            old_last_updated = old_entry.get("last_updated")
            
            # Check for changes
            if new_version != old_version or new_last_updated != old_last_updated:
                # Store compactly as a list
                changes.append([
                    platform,       # Platform (e.g., google_play, app_store)
                    country,        # Country code
                    old_version,    # Old version
                    new_version,    # New version
                    old_last_updated,  # Old last updated date
                    new_last_updated,  # New last updated date
                ])
    
    return changes

# Version check task
async def version_check_task(bot: commands.Bot):
    # Load previous data
    previous_data = load_previous_data()
    logging.info("Starting CSR2 version check")
    new_data = await fetch_data()
    # Detect changes
    logging.info("Comparing data")
    changes = detect_changes(previous_data, new_data)

    logging.info("Overwriting old data with the new data")
    save_data(new_data)

    # Log or return detected changes
    if changes:
        logging.info("Sending detected Changes")
        messages = announce_changes(changes)
        await send_changes(bot, messages)
    else:
        logging.info("No changes detected. Exiting...")
    logging.info("CSR2 version check completed")

# Generate announcement messages
def announce_changes(changes: list):
    messages = []
    batch = []

    for change in changes:
        change[1] = pycountry.countries.get(alpha_2=change[1].upper())
        embed = discord.Embed(
            title="New Store Update Found",
            description=f"Platform: {change[0]}\nCountry: {change[1].name}\n\nOld Version: {change[2]}\nNew Version: {change[3]}\n\nOld Last Updated: <t:{change[4]}:F>\n New Last Updated: <t:{change[5]}:F>",
            color=discord.Color(0xff00ff)
        )
        embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')

        batch.append(embed)

        if len(batch) == 10:
            messages.append(batch)
            batch = []

    # Add remaining embeds if there are any
    if batch:
        messages.append(batch)
    return messages

# Send announcements to Discord
async def send_changes(bot: commands.Bot, messages: list):
    channel_ids = helpers.load_CSR2_announcement_channels()
    for channel_id in channel_ids:
        try:
            channel = bot.get_channel(int(channel_id))
            if not channel:
                logging.error(f"Channel {channel_id} not found.")
                continue

            for message in messages:
                await channel.send(embeds=message)
        except Exception as e:
            logging.error(f"Error while trying to send changes to {channel_id}: {e}")
    user_ids = helpers.load_CSR2_announcement_users()
    for user_id in user_ids:
        try:
            user = bot.get_user(int(user_id))
            if not user:
                logging.error(f"User {user_id} not found.")
                continue
            for message in messages:
                await user.send(embeds=message)
        except Exception as e:
            logging.error(f"Error while trying to send changes to {user_id}: {e}")
