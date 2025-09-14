import aiofiles
import asyncio
import json
import os
import discord
import pycountry
from cogs import announceupdates, notifyupdates
from discord.ext import commands
from datetime import datetime
from google_play_scraper import app as google_play_app
from itunes_app_scraper.scraper import AppStoreScraper
from asyncio import Semaphore, to_thread
import helpers
import in_app_logging

logger = helpers.load_logging()

semaphore = Semaphore(10)

async def version_check_task(bot: commands.Bot):
    header = bot.localisation.get('VERSION_CHECK_LOG_APP_HEADER')
    status = 2
    APP_DATA = await helpers.load_app_data()
    for app in APP_DATA:
        previous_data = await load_previous_data(app)
        logger.info(f"{app[2]}{header}{bot.localisation.get('VERSION_CHECK_LOG_START')}")
        log = f"{app[2]}{header}{bot.localisation.get('VERSION_CHECK_LOG_START')}"
        new_data = await fetch_data(app)
        logger.info(f"{app[2]}{header}{bot.localisation.get('VERSION_CHECK_LOG_COMPARE')}")
        log += f"\n{app[2]}{header}{bot.localisation.get('VERSION_CHECK_LOG_COMPARE')}"
        changes, new_data, case = await detect_changes(previous_data, new_data)

        logger.info(f"{app[2]}{header}{bot.localisation.get('VERSION_CHECK_LOG_OVERWRITING')}")
        log += f"\n{app[2]}{header}{bot.localisation.get('VERSION_CHECK_LOG_OVERWRITING')}"
        await save_data(app, new_data)

        if changes:
            logger.info(f"{app[2]}{header}{bot.localisation.get('VERSION_CHECK_LOG_SEND_CHANGES')}")
            log += f"\n{app[2]}{header}{bot.localisation.get('VERSION_CHECK_LOG_SEND_CHANGES')}"
            messages, log, status = await construct_changes(app, changes, case, log, status)
            log, status = await send_changes(bot, app, messages, log, status)
        else:
            logger.info(f"{app[2]}{header}{bot.localisation.get('VERSION_CHECK_LOG_NO_CHANGES')}")
            log += f"\n{app[2]}{header}{bot.localisation.get('VERSION_CHECK_LOG_NO_CHANGES')}"
        logger.info(f"{app[2]}{header}{app[2]} {bot.localisation.get('VERSION_CHECK_LOG_DONE')}")
        log += f"\n{app[2]}{header}{app[2]} {bot.localisation.get('VERSION_CHECK_LOG_DONE')}"
        await in_app_logging.send_log(bot, log, status, 2)
        previous_data = None
        new_data = None

async def load_previous_data(APP_DATA: list):
    DATA_FILE = await helpers.load_file_path(f'{APP_DATA[2]}_versions')
    if os.path.exists(DATA_FILE):
        async with aiofiles.open(DATA_FILE, mode="r") as file:
            return json.loads(await file.read())
    return {"Google Play": [],"App Store": []}

async def save_data(APP_DATA, data):
    DATA_FILE = await helpers.load_file_path(f'{APP_DATA[2]}_versions')
    async with aiofiles.open(DATA_FILE, mode="w") as file:
        await file.write(json.dumps(data, indent=4))

async def fetch_data(APP_DATA):
    GP_COUNTRIES, AS_COUNTRIES = await helpers.load_store_countries()
    google_play_tasks = [fetch_google_play_data(APP_DATA[0], country) for country in GP_COUNTRIES]
    app_store_tasks = [async_fetch_app_store_data(APP_DATA[1], country) for country in AS_COUNTRIES]

    google_play_results = await asyncio.gather(*google_play_tasks)
    app_store_results = await asyncio.gather(*app_store_tasks)

    return {"Google Play": google_play_results, "App Store": app_store_results}

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

async def async_fetch_app_store_data(app_id, country):
    return await to_thread(fetch_app_store_data, app_id, country)

def fetch_app_store_data(app_id, country):
    try:
        scraper = AppStoreScraper()
        result = scraper.get_app_details(app_id, country)
        dt = datetime.strptime(result.get("currentVersionReleaseDate", "N/A"), "%Y-%m-%dT%H:%M:%SZ")
        currentVersionReleaseDateEpoch = int(dt.timestamp())
        return {
            "country": country,
            "version": result.get("version", "N/A"),
            "last_updated": currentVersionReleaseDateEpoch,
        }
    except Exception as e:
        return {"country": country, "error": str(e)}

async def detect_changes(old_data, new_data):
    changes = []
    case = None

    for platform in new_data:
        for new_entry in new_data[platform]:
            country = new_entry.get("country")
            new_version = new_entry.get("version")
            new_last_updated = new_entry.get("last_updated")
            new_error = new_entry.get("error")

            old_entry = next((entry for entry in old_data[platform] if entry["country"] == country), None)

            if old_entry:
                old_version = old_entry.get("version")
                old_last_updated = old_entry.get("last_updated")
                old_error = old_entry.get("error")
                if old_error and new_error:
                    if old_error == new_error:
                        continue
                    if "No app found with ID " in new_error:
                        changes.append([platform, country, new_error, "The app might've been delisted from the countries store page."])
                        case = 1
                    continue
                if old_error and "No app found with ID " in old_error:
                    changes.append([platform, country, old_error, new_version, new_last_updated, "A new version has been released."])
                    case = 2
                    continue
                if new_error and "No app found with ID " in new_error:
                    changes.append([platform, country, old_version, old_last_updated, new_error, "The app might've been delisted from the countries store page."])
                    case = 3
                    continue
                if old_error or new_error:
                    continue
                if new_last_updated is None:
                    new_last_updated = old_last_updated
                if all([old_version, new_version, old_last_updated, new_last_updated]):
                    if old_version >= new_version and old_last_updated >= new_last_updated:
                        new_entry["version"] = old_version
                        new_entry["last_updated"] = old_last_updated
                    if old_version < new_version or old_last_updated < new_last_updated:
                        changes.append([platform, country, old_version, new_version, old_last_updated, new_last_updated, "A new version has been released."])
                        case = 4
                    continue
            if new_error and "No app found with ID " in new_error:
                changes.append([platform, country, new_error, "The app might've been delisted from the countries store page."])
                case = 1
                continue
            if not new_error:
                changes.append([platform, country, new_version, new_last_updated, "A new version has been released."])
                case = 5
            continue

    return changes, new_data, case

async def construct_changes(APP_DATA: list, changes: list, case: int, log: str, status: int):
    messages = []
    batch = []
    grouped_updates = {}

    for change in changes:
        change[0] = await helpers.emojify_store(change[0])
        country_obj = pycountry.countries.get(alpha_2=change[1].upper())
        country_name = country_obj.name
        country_code = country_obj.alpha_2.upper()
        continent = await helpers.get_continent(country_code)

        update, log, status = await helpers.get_update_case(case, change, log, status)

        key = (change[0], update)
        if key not in grouped_updates:
            grouped_updates[key] = {"platform": change[0], "update": update, "continents": {}}

        if continent not in grouped_updates[key]["continents"]:
            grouped_updates[key]["continents"][continent] = []

        grouped_updates[key]["continents"][continent].append(f"{country_name} ({country_code.lower()})")

    for update_key, update in grouped_updates.items():
        platform, desc = update_key
        description = f"## Platform: {platform}\n{desc}\n\n"

        for continent, country_list in update["continents"].items():
            description += f"**{continent}**\n" + ", ".join(sorted(country_list)) + "\n\n"

        embed = discord.Embed(
            title="New Store Update Found",
            description=description,
            color=discord.Color(0xff00ff)
        )
        embed.set_thumbnail(url=f'{APP_DATA[3]}')

        batch.append(embed)

        if len(batch) == 10:
            messages.append(batch)
            batch = []

    if batch:
        messages.append(batch)

    return messages, log, status

async def send_changes(bot: commands.Bot, APP_DATA: list, messages: list, log: str, status: int):
    header = bot.localisation.get('VERSION_CHECK_LOG_APP_HEADER')
    status = 2
    channel_ids = await helpers.load_file(f'{APP_DATA[2]} announcement channel file')
    for channel_id in channel_ids:
        try:
            channel = bot.get_channel(int(channel_id))
            if not channel:
                logger.error(f"{APP_DATA[2]}{header}{bot.localisation.get('LOG_UPDATE_CHECK_ERROR_NO_CHANNEL')} {channel_id}")
                log += f"\n{APP_DATA[2]}{header}{bot.localisation.get('LOG_UPDATE_CHECK_ERROR_NO_CHANNEL')} {channel_id}"
                status = 1
            else:
                for message in messages:
                    await channel.send(embeds=message)
                    await asyncio.sleep(3)
        except discord.Forbidden as e:
            logger.error(f"{APP_DATA[2]}{header}{bot.localisation.get('LOG_UPDATE_CHECK_ERROR_FORBIDDEN')} {channel_id}: {e}")
            log += f"\n{APP_DATA[2]}{header}{bot.localisation.get('LOG_UPDATE_CHECK_ERROR_FORBIDDEN')} {channel_id}: {e}"
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
                        logger.error(f"{APP_DATA[2]}{header}{bot.localisation.get('LOG_UPDATE_CHECK_ERROR_SEND')} {admin.name} 🏠{channel.guild.name}: {e}")
                        log += f"\n{APP_DATA[2]}{header}{bot.localisation.get('LOG_UPDATE_CHECK_ERROR_SEND')} {admin.name} 🏠{channel.guild.name}: {e}"
                        status = 0
        except discord.NotFound as e:
            check, log, status = await announceupdates.process_request(channel_id, str(APP_DATA[2]), 0, log)
        except Exception as e:
            logger.error(f"{APP_DATA[2]}{header}{bot.localisation.get('LOG_UPDATE_CHECK_ERROR_SEND_CHANNEL')} {channel_id}: {e}")
            log += f"\n{APP_DATA[2]}{header}{bot.localisation.get('LOG_UPDATE_CHECK_ERROR_SEND_CHANNEL')} {channel_id}: {e}"
            status = 0
    user_ids = await helpers.load_file(f'{APP_DATA[2]} announcement user file')
    for user_id in user_ids:
        try:
            user = bot.get_user(int(user_id))
            if not user:
                logger.error(f"{APP_DATA[2]}{header}User {user_id} not found.")
                log += f"\n{APP_DATA[2]}{header}User {user_id} not found."
                status = 1
            else:
                for i,message in enumerate(messages):
                    if i == 0:
                        await user.send(embeds=message)
                    else:
                        await user.send(embeds=message, silent=True)
                    await asyncio.sleep(3)
        except discord.Forbidden as e:
            await notifyupdates.process_request(user_id, str(APP_DATA[2]), 0, log)
        except discord.NotFound as e:
            await notifyupdates.process_request(user_id, str(APP_DATA[2]), 0, log)
        except Exception as e:
            logger.error(f"{APP_DATA[2]}{header}{bot.localisation.get('LOG_UPDATE_CHECK_ERROR_SEND_USER')} {user_id}: {e}")
            log += f"\n{APP_DATA[2]}{header}{bot.localisation.get('LOG_UPDATE_CHECK_ERROR_SEND_USER')} {user_id}: {e}"
            status = 0

    return log, status
