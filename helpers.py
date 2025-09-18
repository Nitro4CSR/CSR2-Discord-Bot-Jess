from dotenv import load_dotenv
from discord import app_commands
from discord.ext import commands
import discord
import aiofiles
import aiosqlite
import json
import os
import pycountry_convert
import random
import sys
import logging

load_dotenv()

def load_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    return logger

logger = load_logging()

def load_localisation():
    base = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base, "config", "config.json"), "r", encoding="utf-8") as f:
        cfg = json.load(f)
    with open(os.path.join(base, "localisation", f"{cfg.get('Localisation', 'en')}.json"), "r", encoding="utf-8") as f:
        loc = json.load(f)
    return {k: k for k in loc} if cfg.get("DebugMode") else loc

async def load_token():
    return os.getenv('TOKEN')

async def set_dynamic_status(bot: commands.Bot):
    statuses = await load_json_key("config", "DynamicStatusList")
    num = random.randint(0, (len(statuses)-1))
    if await load_json_key("status", "IsStaticStatusActive") == False:
        await change_presence(bot, statuses[num]["Activity"], statuses[num]["Text"], statuses[num]["url"])
    return

async def change_presence(bot: commands.Bot, activity: str, text: str, url: str = None):
    if activity:
        if activity == "playing":
            await bot.change_presence(activity=discord.Game(name=text))
        if activity == "watching":
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=text))
        if activity == "streaming":
            if url:
                await bot.change_presence(activity=discord.Streaming(name=text, url=url))
            else:
                await bot.change_presence(activity=discord.Game(name=text))
        if activity == "listening":
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=text))
        if activity == "competing":
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.competing, name=text))
    else:
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.custom, name=text))
    return

async def load_app_data():
    PACKAGE_NAME = ["com.naturalmotion.customstreetracer2", "com.zynga.csr3"]
    APP_STORE_APP_ID = ["887947640", "1572295868"]
    APP_NAME = ["CSR2", "CSR3"]
    ICON_URL = ["https://imgur.com/1VWi2Di.png", "https://imgur.com/szUv2T5.png"]

    return list(zip(PACKAGE_NAME, APP_STORE_APP_ID, APP_NAME, ICON_URL))

async def load_store_countries():
    GP_COUNTRIES = ["ae", "ag", "al", "am", "ao", "ar", "at", "au", "aw", "az", "ba", "bd", "be", "bf", "bg", "bh", "bj", "bo", "br", "bs", "bw", "by", "bz", "ca", "ch", "ci", "cl", "cm", "cn", "co", "cr", "cv", "cy", "cz", "de", "dk", "do", "dz", "ec", "ee", "eg", "es", "fi", "fj", "fr", "ga", "gb", "gh", "gr", "gt", "gw", "hk", "hn", "hr", "ht", "hu", "id", "ie", "il", "in", "is", "it", "jm", "jo", "jp", "ke", "kg", "kh", "kr", "kw", "kz", "la", "lb", "li", "lk", "lt", "lu", "lv", "ma", "md", "mk", "ml", "mt", "mu", "mx", "my", "mz", "na", "ne", "ng", "ni", "nl", "no", "np", "nz", "om", "pa", "pe", "pg", "ph", "pk", "pl", "pt", "py", "qa", "ro", "rs", "ru", "rw", "sa", "se", "sg", "si", "sk", "sn", "sv", "tg", "th", "tj", "tm", "tn", "tr", "tt", "tw", "tz", "ua", "ug", "us", "uy", "uz", "ve", "vn", "ye", "za", "zm", "zw"]
    AS_COUNTRIES = ["ae", "ag", "ai", "al", "am", "ar", "at", "au", "az", "ba", "bb", "be", "bf", "bg", "bh", "bj", "bm", "bn", "bo", "br", "bs", "bt", "bw", "bz", "ca", "cg", "ch", "ci", "cl", "cm", "co", "cr", "cv", "cy", "cz", "de", "dk", "dm", "do", "dz", "ec", "ee", "eg", "es", "fi", "fj", "fr", "ga", "gb", "gd", "gh", "gm", "gr", "gt", "gw", "gy", "hk", "hn", "hr", "hu", "id", "ie", "il", "in", "is", "it", "jm", "jo", "jp", "ke", "kg", "kn", "kr", "kw", "ky", "kz", "lb", "lc", "lk", "lr", "lt", "lu", "lv", "ma", "md", "mg", "mk", "ml", "mn", "mo", "mr", "ms", "mt", "mu", "mw", "mx", "my", "mz", "na", "ne", "ng", "ni", "nl", "no", "np", "nz", "om", "pa", "pe", "pg", "ph", "pk", "pl", "pt", "pw", "py", "qa", "ro", "rs", "rw", "sa", "sb", "sc", "se", "sg", "si", "sk", "sn", "sr", "st", "sv", "sz", "tc", "td", "th", "tj", "tm", "tn", "tr", "tt", "tw", "tz", "ug", "us", "uy", "uz", "vc", "ve", "vg", "vn", "ye", "za", "zm", "zw"]

    return GP_COUNTRIES, AS_COUNTRIES

def load_command_options_tier(localisation: dict):
    return [app_commands.Choice(name=localisation.get('ANY_CMD_TIER_OPTION_T5'), value="T5"), app_commands.Choice(name=localisation.get('ANY_CMD_TIER_OPTION_T4'), value="T4"), app_commands.Choice(name="localisation.get('ANY_CMD_TIER_OPTION_T3')", value="T3"), app_commands.Choice(name="localisation.get('ANY_CMD_TIER_OPTION_T2')", value="T2"), app_commands.Choice(name="localisation.get('ANY_CMD_TIER_OPTION_T1')", value="T1")]

def load_command_options_rarity(localisation: dict):
    return [app_commands.Choice(name=localisation.get('ANY_CMD_RARITY_OPTION_5GS'), value="G5%"), app_commands.Choice(name=localisation.get('ANY_CMD_RARITY_OPTION_5PS'), value="P5%"), app_commands.Choice(name=localisation.get('ANY_CMD_RARITY_OPTION_5S'), value=f"%5%"), app_commands.Choice(name=localisation.get('ANY_CMD_RARITY_OPTION_4GS'), value="G4%"), app_commands.Choice(name=localisation.get('ANY_CMD_RARITY_OPTION_4PS'), value="P4%"), app_commands.Choice(name=localisation.get('ANY_CMD_RARITY_OPTION_4S'), value=f"%4%"), app_commands.Choice(name=localisation.get('ANY_CMD_RARITY_OPTION_3GS'), value="G3%"), app_commands.Choice(name=localisation.get('ANY_CMD_RARITY_OPTION_3PS'), value="P3%"), app_commands.Choice(name=localisation.get('ANY_CMD_RARITY_OPTION_3S'), value=f"%3%"), app_commands.Choice(name=localisation.get('ANY_CMD_RARITY_OPTION_2GS'), value="G2%"), app_commands.Choice(name=localisation.get('ANY_CMD_RARITY_OPTION_2PS'), value="P2%"), app_commands.Choice(name=localisation.get('ANY_CMD_RARITY_OPTION_2S'), value=f"%2%"), app_commands.Choice(name=localisation.get('ANY_CMD_RARITY_OPTION_1GS'), value="G1%"), app_commands.Choice(name=localisation.get('ANY_CMD_RARITY_OPTION_1PS'), value="P1%"), app_commands.Choice(name=localisation.get('ANY_CMD_RARITY_OPTION_1S'), value=f"%1%"), app_commands.Choice(name=localisation.get('ANY_CMD_RARITY_OPTION_GS'), value="G%"), app_commands.Choice(name=localisation.get('ANY_CMD_RARITY_OPTION_PS'), value="P%"), app_commands.Choice(name=localisation.get('ANY_CMD_RARITY_OPTION_NS'), value="N0%")]

def load_command_options_scope(localisation: dict):
    return [app_commands.Choice(name=localisation.get('ANY_CMD_SCOPE_OPTION_ALL'), value="All"), app_commands.Choice(name=localisation.get('ANY_CMD_SCOPE_OPTION_CSR2'), value="CSR2"), app_commands.Choice(name=localisation.get('ANY_CMD_SCOPE_OPTION_CSR3'), value="CSR3"), app_commands.Choice(name=localisation.get('ANY_CMD_SCOPE_OPTION_BLOG'), value="Blog")]

def load_command_options_upgrade_stages(localisation: dict):
    return [app_commands.Choice(name=localisation.get('UPDATE_TUNE_UPGRADES_OPTION_S6'), value="6"), app_commands.Choice(name=localisation.get('UPDATE_TUNE_UPGRADES_OPTION_S5'), value="5"), app_commands.Choice(name=localisation.get('UPDATE_TUNE_UPGRADES_OPTION_S4'), value="4"), app_commands.Choice(name=localisation.get('UPDATE_TUNE_UPGRADES_OPTION_S3'), value="3"), app_commands.Choice(name=localisation.get('UPDATE_TUNE_UPGRADES_OPTION_S2'), value="2"), app_commands.Choice(name=localisation.get('UPDATE_TUNE_UPGRADES_OPTION_S1'), value="1")]

async def load_file_path(file):
    conversion = {
        "admins": "resources/admins.json",
        "global_list_admins": "resources/global_list_admins.json",
        "CSR2_announcement_channels": "resources/CSR2_announcement_channels.json",
        "CSR3_announcement_channels": "resources/CSR3_announcement_channels.json",
        "Blog_announcement_channels": "resources/Blog_announcement_channels.json",
        "CSR2_announcement_users": "resources/CSR2_announcement_users.json",
        "CSR3_announcement_users": "resources/CSR3_announcement_users.json",
        "Blog_announcement_users": "resources/Blog_announcement_users.json",
        "CSR2_versions": "resources/CSR2_versions.json",
        "CSR3_versions": "resources/CSR3_versions.json",
        "Blog_versions": "resources/Blog_versions.json",
        "server_limits": "resources/server_limits.json",
        "user_limits": "resources/user_limits.json",
        "EDB": "resources/EDB.db",
        "WRs": "resources/EDB.db",
        "tunes": "resources/tunes.db",
        "version": "resources/version.json",
        "custom_lists": "resources/custom_lists.json",
        "config": "config/config.json",
        "status": "config/status.json",
        "session": "config/session_variables.json",
        "PfP": "assets/PfP.png",
        "PfP_Halloween": "assets/PfP_Halloween.png",
        "PfP_Christmas": "assets/PfP_Christmas.png",
        "PfP_Birthday": "assets/PfP_Birthday.png",
        "customlist_template": "assets/CustomList_Template.json"
    }
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), conversion.get(file))

async def load_localisation_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "localisation", f"{await load_json_key("config", "Localisation")}.json")

async def load_file(file):
    conversion = {
        "Admin file": await load_file_path('admins'),
        "global_list_admins": await load_file_path('global_list_admins'),
        "CSR2 announcement channel file": await load_file_path('CSR2_announcement_channels'),
        "CSR3 announcement channel file": await load_file_path('CSR3_announcement_channels'),
        "Blog announcement channel file": await load_file_path('Blog_announcement_channels'),
        "CSR2 announcement user file": await load_file_path('CSR2_announcement_users'),
        "CSR3 announcement user file": await load_file_path('CSR3_announcement_users'),
        "Blog announcement user file": await load_file_path('Blog_announcement_users'),
        "CSR2_versions": await load_file_path('CSR2_versions'),
        "CSR3_versions": await load_file_path('CSR3_versions'),
        "Blog_versions": await load_file_path('Blog_versions'),
        "server_limits": await load_file_path('server_limits'),
        "user_limits": await load_file_path('user_limits'),
        "custom_lists": await load_file_path('custom_lists'),
        "status": await load_file_path('status'),
        "version": await load_file_path('version'),
        "config": await load_file_path('config'),
        "session": await load_file_path('session'),
        "customlist_template": await load_file_path('customlist_template')
    }
    if file == "localisation":
        FILE = await load_localisation_path()
    else:
        FILE = conversion.get(file)

    if os.path.exists(FILE):
        try:
            async with aiofiles.open(FILE, mode='r', encoding='utf-8') as f:
                content = await f.read()
            data = json.loads(content)
            return data
        except Exception as e:
            logger.error(f"There was an error opening the {file}\n{e}")
    else:
        logger.error(f"{file} '{FILE}' not found.")
    return {}

async def save_file(file: str, data: dict):
    FILE = await load_file_path(file)
    async with aiofiles.open(FILE, mode="w", encoding='utf-8') as file:
            await file.write(json.dumps(data, indent=4))

async def load_json_key(file, key):
    data = await load_file(file)
    if data is not None:
        val = data.get(key)
        return val
    else:
        return key

async def execute_sql_statement(database: str, sql_statement: str, values: list = None):
    database_paths = {
        "WRs": await load_file_path('EDB'),
        "tunes": await load_file_path('tunes')
    }
    db_path = database_paths[database]
    async with aiosqlite.connect(db_path) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(sql_statement, values) if values else await cursor.execute(sql_statement)
            if sql_statement.strip().lower().startswith("select"):
                output = await cursor.fetchall()
            else:
                await conn.commit()
                output = None
    return output

async def get_send_route(results: int, user: str, server: str = None):
    if server:
        server_data = await load_json_key("server_limits", str(server))
        server_limit = server_data["PostLimit"] if server_data and "PostLimit" in server_data else await load_json_key("config", "DefaultServerLimit")
        if server_limit >= results or server_limit == 0:
            return 0
    user_data = await load_json_key("user_limits", str(user))
    user_limit = user_data["PostLimit"] if user_data and "PostLimit" in user_data else await load_json_key("config", "DefaultUserLimit")
    return 1 if user_limit >= results or user_limit == 0 else 2

async def load_perms_dic():
    discord_permissions = {
        "send_messages": "Send Messages",
        "embed_links": "Embed Links",
        "attach_files": "Attach Files",
        "add_reactions": "Add Reactions"
    }
    return discord_permissions

async def emojify_tier(db_value):
    conversion = {
        "": "",
        "T1": f"{await load_json_key("session", "T1_EMOJI")}",
        "T2": f"{await load_json_key("session", "T2_EMOJI")}",
        "T3": f"{await load_json_key("session", "T3_EMOJI")}",
        "T4": f"{await load_json_key("session", "T4_EMOJI")}",
        "T5": f"{await load_json_key("session", "T5_EMOJI")}",
        "T1-T3": f"{await load_json_key("session", "T1_EMOJI")}-{await load_json_key("session", "T2_EMOJI")}",
        "T4-T5": f"{await load_json_key("session", "T4_EMOJI")}-{await load_json_key("session", "T5_EMOJI")}"
    }
    emoji = conversion.get(db_value)
    return emoji

async def emojify_rarity(db_value):
    conversion = {
        "": "",
        "N0": f"{await load_json_key("session", "0S_EMOJI")}{await load_json_key("session", "0S_EMOJI")}{await load_json_key("session", "0S_EMOJI")}{await load_json_key("session", "0S_EMOJI")}{await load_json_key("session", "0S_EMOJI")}",
        "G1": f"{await load_json_key("session", "GS_EMOJI")}",
        "G2": f"{await load_json_key("session", "GS_EMOJI")}{await load_json_key("session", "GS_EMOJI")}",
        "G3": f"{await load_json_key("session", "GS_EMOJI")}{await load_json_key("session", "GS_EMOJI")}{await load_json_key("session", "GS_EMOJI")}",
        "G4": f"{await load_json_key("session", "GS_EMOJI")}{await load_json_key("session", "GS_EMOJI")}{await load_json_key("session", "GS_EMOJI")}{await load_json_key("session", "GS_EMOJI")}",
        "G5": f"{await load_json_key("session", "GS_EMOJI")}{await load_json_key("session", "GS_EMOJI")}{await load_json_key("session", "GS_EMOJI")}{await load_json_key("session", "GS_EMOJI")}{await load_json_key("session", "GS_EMOJI")}",
        "P1": f"{await load_json_key("session", "PS1_EMOJI")}",
        "P2": f"{await load_json_key("session", "PS1_EMOJI")}{await load_json_key("session", "PS2_EMOJI")}",
        "P3": f"{await load_json_key("session", "PS1_EMOJI")}{await load_json_key("session", "PS2_EMOJI")}{await load_json_key("session", "PS3_EMOJI")}",
        "P4": f"{await load_json_key("session", "PS1_EMOJI")}{await load_json_key("session", "PS2_EMOJI")}{await load_json_key("session", "PS3_EMOJI")}{await load_json_key("session", "PS4_EMOJI")}",
        "P5": f"{await load_json_key("session", "PS1_EMOJI")}{await load_json_key("session", "PS2_EMOJI")}{await load_json_key("session", "PS3_EMOJI")}{await load_json_key("session", "PS4_EMOJI")}{await load_json_key("session", "PS5_EMOJI")}",
        "G1-G3": f"{await load_json_key("session", "GS_EMOJI")}{await load_json_key("session", "EMPTYSTAR_EMOJI")}{await load_json_key("session", "EMPTYSTAR_EMOJI")}",
        "G2_G4": f"{await load_json_key("session", "GS_EMOJI")}{await load_json_key("session", "GS_EMOJI")}{await load_json_key("session", "EMPTYSTAR_EMOJI")}{await load_json_key("session", "EMPTYSTAR_EMOJI")}",
        "G3_G4": f"{await load_json_key("session", "GS_EMOJI")}{await load_json_key("session", "GS_EMOJI")}{await load_json_key("session", "GS_EMOJI")}{await load_json_key("session", "EMPTYSTAR_EMOJI")}",
        "G3_G5": f"{await load_json_key("session", "GS_EMOJI")}{await load_json_key("session", "GS_EMOJI")}{await load_json_key("session", "GS_EMOJI")}{await load_json_key("session", "EMPTYSTAR_EMOJI")}{await load_json_key("session", "EMPTYSTAR_EMOJI")}",
        "G4_G5": f"{await load_json_key("session", "GS_EMOJI")}{await load_json_key("session", "GS_EMOJI")}{await load_json_key("session", "GS_EMOJI")}{await load_json_key("session", "GS_EMOJI")}{await load_json_key("session", "EMPTYSTAR_EMOJI")}",
        "N0_G3": f"{await load_json_key("session", "EMPTYSTAR_EMOJI")}{await load_json_key("session", "EMPTYSTAR_EMOJI")}{await load_json_key("session", "EMPTYSTAR_EMOJI")}",
        "N0_G4": f"{await load_json_key("session", "EMPTYSTAR_EMOJI")}{await load_json_key("session", "EMPTYSTAR_EMOJI")}{await load_json_key("session", "EMPTYSTAR_EMOJI")}{await load_json_key("session", "EMPTYSTAR_EMOJI")}",
        "N0_G5": f"{await load_json_key("session", "EMPTYSTAR_EMOJI")}{await load_json_key("session", "EMPTYSTAR_EMOJI")}{await load_json_key("session", "EMPTYSTAR_EMOJI")}{await load_json_key("session", "EMPTYSTAR_EMOJI")}{await load_json_key("session", "EMPTYSTAR_EMOJI")}",
        "N0_P5": f"{await load_json_key("session", "EMPTYSTAR_EMOJI")}{await load_json_key("session", "EMPTYSTAR_EMOJI")}{await load_json_key("session", "EMPTYSTAR_EMOJI")}{await load_json_key("session", "EMPTYSTAR_EMOJI")}{await load_json_key("session", "EMPTYSTAR_EMOJI")}",
        "N0_NP5": f"{await load_json_key("session", "EMPTYSTAR_EMOJI")}{await load_json_key("session", "EMPTYSTAR_EMOJI")}{await load_json_key("session", "EMPTYSTAR_EMOJI")}{await load_json_key("session", "EMPTYSTAR_EMOJI")}{await load_json_key("session", "EMPTYSTAR_EMOJI")}",
        "1": f"{await load_json_key("session", "S1_EMOJI")}",
        "2": f"{await load_json_key("session", "S2_EMOJI")}",
        "3": f"{await load_json_key("session", "S3_EMOJI")}",
        "4": f"{await load_json_key("session", "S4_EMOJI")}",
        "5": f"{await load_json_key("session", "S5_EMOJI")}"
    }
    emoji = conversion.get(db_value)
    return emoji

async def emojify_store(store):
    conversion = {
        "": "",
        "App Store": f"{await load_json_key("session", "APP_STORE_EMOJI")}",
        "Google Play": f"{await load_json_key("session", "GOOGLE_PLAY_EMOJI")}"
    }

    emoji = conversion.get(store)

    return emoji

async def get_update_case(case: int, change: list, log: str, status: int):
    try:
        change += [""] * (6 - len(change))
        conversion = {
            "": "",
            1: f"New:\nScrape Error: {change[2]}",
            2: f"Old:\nScrape Error: {change[2]}\n\nNew Version: {change[3]}\nNew Last Updated: <t:{change[4]}:F>",
            3: f"Old Version: {change[2]}\nOld Last Updated: <t:{change[3]}:F>\n\nNew:\nScrape Error: {change[4]}",
            4: f"Old Version: {change[2]}\nNew Version: {change[3]}\n\nOld Last Updated: <t:{change[4]}:F>\nNew Last Updated: <t:{change[5]}:F>",
            5: f"New Version: {change[2]}\nNew Last Updated: <t:{change[3]}:F>"
        }
        description = conversion.get(case)
    except Exception as e:
        description=f"There was an error processing the detected changes."
        logger.error(f"An unhandeled case was detected: {e}")
        log += f"An unhandeled case was detected: {e}"
        status = 0
    return description, log, status

async def get_change_key(case: int, change: list, log: str, status: int):
    try:
        change += [""] * (6 - len(change))
        conversion = {
            1: (change[2]),
            2: (change[2], change[3], change[4]),
            3: (change[2], change[3], change[4]),
            4: (change[2], change[3], change[4], change[5]),
            5: (change[2], change[3])
        }
        key = conversion.get(case)
    except Exception as e:
        key = (change)
        logger.error(f"An unhandeled case was detected: {e}")
        log += f"An unhandeled case was detected: {e}"
        status = 0
    return key, log, status

async def get_continent(cc):
    try:
        continent_code = pycountry_convert.country_alpha2_to_continent_code(cc)
        continent_names = {
            "AF": "Africa",
            "AS": "Asia",
            "EU": "Europe",
            "NA": "North America",
            "SA": "South America",
            "OC": "Oceania",
            "AN": "Antarctica",
        }
        return continent_names.get(continent_code, "Unknown")
    except Exception:
        return "Unknown"

async def is_float(v):
    try:
        float(v)
        return True
    except ValueError:
        return False

async def is_list(v):
    try:
        val = json.loads(v)
        if isinstance(val, list):
            return True
        else:
            return False
    except:
        return False

async def restart():
    python = sys.executable
    os.execl(python, python, *sys.argv)
