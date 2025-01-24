import aiofiles
import asyncio
import json
import logging
import os
import discord
import pycountry
from discord.ext import commands
from datetime import datetime
from google_play_scraper import app as google_play_app
from itunes_app_scraper.scraper import AppStoreScraper
from asyncio import Semaphore, to_thread
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

# Semaphore to limit concurrency
semaphore = Semaphore(10)

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
async def async_fetch_app_store_data(app_id, country):
    return await to_thread(fetch_app_store_data, app_id, country)

# Google Play scraping logic
async def fetch_google_play_data(package_name, country):
    try:
        async with semaphore:
            result = await to_thread(google_play_app, package_name, lang="en", country=country)
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
async def load_previous_data():
    """Load the previous data from the JSON file."""
    if os.path.exists(CSR2_DATA_FILE):
        async with aiofiles.open(CSR2_DATA_FILE, mode="r") as file:
            return json.loads(await file.read())
    return {"Google Play": [],"App Store": []}

async def save_data(data):
    """Save the current data to the JSON file."""
    async with aiofiles.open(CSR2_DATA_FILE, mode="w") as file:
        await file.write(json.dumps(data, indent=4))

# Detect changes between old and new data
async def detect_changes(old_data, new_data):
    """Compare old data with new data and detect changes."""
    changes = []
    case = None

    for platform in new_data:
        for new_entry in new_data[platform]:
            country = new_entry.get("country")
            new_version = new_entry.get("version")
            new_last_updated = new_entry.get("last_updated")
            new_error = new_entry.get("error")

            # Find the corresponding old entry
            old_entry = next((entry for entry in old_data[platform] if entry["country"] == country), None)

            if old_entry:
                old_version = old_entry.get("version")
                old_last_updated = old_entry.get("last_updated")
                old_error = old_entry.get("error")
                if old_error and new_error:
                    if old_error == new_error:
                        continue
                    if "No app found with ID " in new_error:
                        changes.append([platform, country, new_error]) # 3
                        case = 1
                    continue
                if old_error and "No app found with ID " in old_error:
                    changes.append([platform, country, old_error, new_version, new_last_updated]) # 5
                    case = 2
                    continue
                if new_error and "No app found with ID " in new_error:
                    changes.append([platform, country, old_version, old_last_updated, new_error]) # 5
                    case = 3
                    continue
                if old_error or new_error:
                    continue
                if old_version >= new_version and old_last_updated >= new_last_updated:
                    new_entry["version"] = old_version
                    new_entry["last_updated"] = old_last_updated
                if old_version < new_version or old_last_updated < new_last_updated:
                    changes.append([platform, country, old_version, new_version, old_last_updated, new_last_updated]) # 6
                    case = 4
                continue
            if new_error and "No app found with ID " in new_error:
                changes.append([platform, country, new_error]) # 3
                case = 1
                continue
            if not new_error:
                changes.append([platform, country, new_version, new_last_updated]) # 4
                case = 5
            continue

    return changes, new_data, case

# Version check task
async def version_check_task(bot: commands.Bot):
    previous_data = await load_previous_data()
    logging.info("CSR2 - Starting CSR2 version check")
    new_data = await fetch_data()
    logging.info("CSR2 - Comparing data")
    changes, new_data, case = await detect_changes(previous_data, new_data)

    logging.info("CSR2 - Overwriting old data with the new data")
    await save_data(new_data)

    if changes:
        logging.info("CSR2 - Sending detected Changes")
        messages = await announce_changes(changes, case)
        await send_changes(bot, messages)
    else:
        logging.info("CSR2 - No changes detected. Exiting...")
    logging.info("CSR2 - CSR2 version check completed")

# Generate announcement messages
async def announce_changes(changes: list, case: int):
    messages = []
    batch = []

    for change in changes:
        if change[0] == "Google Play":
            change[0] == "<:Google_Play:1332367175121502279> Google Play"
        else:
            change[0] == "<:App_Store:1332367186031018004> App Store"

        change[1] = pycountry.countries.get(alpha_2=change[1].upper())

        description=f"Platform: {change[0]}\nCountry: {change[1].name}\n\n"
        if case == 1:
            description+=f"New:\nScrape Error: {change[2]}"
        elif case == 2:
            description+=f"Old:\nScrape Error: {change[2]}\n\nNew Version: {change[3]}\nNew Last Updated: <t:{change[4]}:F>"
        elif case == 3:
            description+=f"Old Version: {change[2]}\nOld Last Updated: <t:{change[3]}:F>\n\nNew:\nScrape Error: {change[4]}"
        elif case == 4:
            description+=f"Old Version: {change[2]}\nNew Version: {change[3]}\n\nOld Last Updated: <t:{change[4]}:F>\nNew Last Updated: <t:{change[5]}:F>"
        elif case == 5:
            description+=f"New Version: {change[2]}\nNew Last Updated: <t:{change[3]}:F>"
        else:
            description=f"There was an error processing the detected changes."

        embed = discord.Embed(
            title="New Store Update Found",
            description=description,
            color=discord.Color(0xff00ff)
        )
        embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')

        batch.append(embed)

        if len(batch) == 10:
            messages.append(batch)
            batch = []

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
            else:
                for message in messages:
                    await channel.send(embeds=message)
                    await asyncio.sleep(3)
        except Exception as e:
            logging.error(f"Error while trying to send changes to {channel_id}: {e}")
    user_ids = helpers.load_CSR2_announcement_users()
    for user_id in user_ids:
        try:
            user = bot.get_user(int(user_id))
            print(f"{int(user_id)}")
            if not user:
                logging.error(f"User {user_id} not found.")
            else:
                for message in messages:
                    await user.send(embeds=message)
        except Exception as e:
            logging.error(f"Error while trying to send changes to {user_id}: {e}")
