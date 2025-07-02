from dotenv import load_dotenv
from discord import app_commands
import aiofiles
import json
import os
import pycountry_convert
import sys
import logging

load_dotenv()

def load_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    return logger

logger = load_logging()

async def load_base_dir():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

async def load_dotenv_dir():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')

async def load_dotenv_data():
    load_dotenv()

async def load_token():
    TOKEN = os.getenv('TOKEN')
    return TOKEN

async def load_client_id():
    CLIENT_ID = os.getenv('CLIENT_ID')
    return CLIENT_ID

async def load_setup_status():
    FIRST_SETUP_DONE = os.getenv("FIRST_SETUP_DONE", "False").lower() == "true"
    return FIRST_SETUP_DONE

async def load_default_name():
    CLIENT_DEFAULT_NAME = os.getenv('CLIENT_DEFAULT_NAME')
    return CLIENT_DEFAULT_NAME

async def load_halloween_name():
    CLIENT_HALLOWEEN_NAME = os.getenv('CLIENT_HALLOWEEN_NAME')
    return CLIENT_HALLOWEEN_NAME

async def load_xmas_name():
    CLIENT_CHRISTMAS_NAME = os.getenv('CLIENT_CHRISTMAS_NAME')
    return CLIENT_CHRISTMAS_NAME

async def load_bday_name():
    CLIENT_BIRTHDAY_NAME = os.getenv('CLIENT_BIRTHDAY_NAME')
    return CLIENT_BIRTHDAY_NAME

async def load_bday_month():
    return int(os.getenv('CLIENT_BIRTHDAY_MONTH'))

async def load_bday_day():
    return int(os.getenv('CLIENT_BIRTHDAY_DAY'))

async def load_super_admin():
    SUPER_ADMIN = os.getenv('SUPER_ADMIN')
    return SUPER_ADMIN

async def load_admin_server():
    ADMIN_SERVER = os.getenv('ADMIN_SERVER')
    return ADMIN_SERVER

async def load_log_channels():
    LOG_CHANNEL = os.getenv('LOG_CHANNEL_ID')
    return LOG_CHANNEL

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

def load_command_options_tier():
    return [app_commands.Choice(name="Tier 5 (T5|K5|L5)", value="T5"), app_commands.Choice(name="Tier 4 (T4|K4|L4)", value="T4"), app_commands.Choice(name="Tier 3 (T3|K3|L3)", value="T3"), app_commands.Choice(name="Tier 2 (T2|K2|L2)", value="T2"), app_commands.Choice(name="Tier 1 (T1|K1|L1)", value="T1")]

def load_command_options_rarity():
    return [app_commands.Choice(name="5 Gold Stars", value="G5%"), app_commands.Choice(name="5 Purple Stars", value="P5%"), app_commands.Choice(name="5 Stars", value=f"%5%"), app_commands.Choice(name="4 Gold Stars", value="G4%"), app_commands.Choice(name="4 Purple Stars", value="P4%"), app_commands.Choice(name="4 Stars", value=f"%4%"), app_commands.Choice(name="3 Gold Stars", value="G3%"), app_commands.Choice(name="3 Purple Stars", value="P3%"), app_commands.Choice(name="3 Stars", value=f"%3%"), app_commands.Choice(name="2 Gold Stars", value="G2%"), app_commands.Choice(name="2 Purple Stars", value="P2%"), app_commands.Choice(name="2 Stars", value=f"%2%"), app_commands.Choice(name="1 Gold Stars", value="G1%"), app_commands.Choice(name="1 Purple Stars", value="P1%"), app_commands.Choice(name="1 Stars", value=f"%1%"), app_commands.Choice(name="Gold Star", value="G%"), app_commands.Choice(name="Purple Star", value="P%"), app_commands.Choice(name="Non Star", value="N0%")]

def load_command_options_scope():
    return [app_commands.Choice(name="All (CSR2, CSR3 & Blog)", value="All"), app_commands.Choice(name="CSR2", value="CSR2"), app_commands.Choice(name="CSR3", value="CSR3"), app_commands.Choice(name="Blog", value="Blog")]

async def load_asset_path(asset):
    conversion = {
        "PfP": "PfP.png",
        "PfP_Halloween": "PfP_Halloween.png",
        "PfP_Christmas": "PfP_Christmas.png",
        "PfP_Birthday": "PfP_Birthday.png"
    }

    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", conversion.get(asset))

async def load_file_path(file):
    conversion = {
        "admins": "admins.json",
        "CSR2_announcement_channels": "CSR2_announcement_channels.json",
        "CSR3_announcement_channels": "CSR3_announcement_channels.json",
        "Blog_announcement_channels": "Blog_announcement_channels.json",
        "CSR2_announcement_users": "CSR2_announcement_users.json",
        "CSR3_announcement_users": "CSR3_announcement_users.json",
        "Blog_announcement_users": "Blog_announcement_users.json",
        "CSR2_versions": "CSR2_versions.json",
        "CSR3_versions": "CSR3_versions.json",
        "Blog_versions": "Blog_versions.json",
        "limits": "limits.json",
        "EDB": "EDB.db",
        "tunes": "tunes.db",
        "version": "version.json"
    }
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", conversion.get(file))

async def load_file(file):
    conversion = {
        "Admin file": await load_file_path('admins'),
        "CSR2 announcement channel file": await load_file_path('CSR2_announcement_channels'),
        "CSR3 announcement channel file": await load_file_path('CSR3_announcement_channels'),
        "Blog announcement channel file": await load_file_path('Blog_announcement_channels'),
        "CSR2 announcement user file": await load_file_path('CSR2_announcement_users'),
        "CSR3 announcement user file": await load_file_path('CSR3_announcement_users'),
        "Blog announcement user file": await load_file_path('Blog_announcement_users'),
        "Version": await load_file_path('version')
    }
    FILE = conversion.get(file)

    if os.path.exists(FILE):
        try:
            async with aiofiles.open(FILE, mode='r') as f:
                content = await f.read()
                data = json.loads(content)
                if isinstance(data, list) and all(isinstance(i, str) for i in data):
                    return set(data)
                else:
                    raise ValueError("JSON file is not in the expected format")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {e}")
        except ValueError as e:
            logger.error(f"Value error: {e}")
        except Exception as e:
            logger.error(f"Error loading admin file: {e}")
    else:
        logger.error(f"{file} '{FILE}' not found.")

    return set()

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
        "T1": f"{os.getenv('T1_EMOJI')}",
        "T2": f"{os.getenv('T2_EMOJI')}",
        "T3": f"{os.getenv('T3_EMOJI')}",
        "T4": f"{os.getenv('T4_EMOJI')}",
        "T5": f"{os.getenv('T5_EMOJI')}",
        "T1-T3": f"{os.getenv('T1_EMOJI')}-{os.getenv('T3_EMOJI')}",
        "T4-T5": f"{os.getenv('T4_EMOJI')}-{os.getenv('T5_EMOJI')}"
    }

    emoji = conversion.get(db_value)

    return emoji

async def emojify_rarity(db_value):
    conversion = {
        "": "",
        "N0": f"{os.getenv('NS_EMOJI')}{os.getenv('NS_EMOJI')}{os.getenv('NS_EMOJI')}{os.getenv('NS_EMOJI')}{os.getenv('NS_EMOJI')}",
        "G1": f"{os.getenv('GS_EMOJI')}",
        "G2": f"{os.getenv('GS_EMOJI')}{os.getenv('GS_EMOJI')}",
        "G3": f"{os.getenv('GS_EMOJI')}{os.getenv('GS_EMOJI')}{os.getenv('GS_EMOJI')}",
        "G4": f"{os.getenv('GS_EMOJI')}{os.getenv('GS_EMOJI')}{os.getenv('GS_EMOJI')}{os.getenv('GS_EMOJI')}",
        "G5": f"{os.getenv('GS_EMOJI')}{os.getenv('GS_EMOJI')}{os.getenv('GS_EMOJI')}{os.getenv('GS_EMOJI')}{os.getenv('GS_EMOJI')}",
        "P1": f"{os.getenv('PS1_EMOJI')}",
        "P2": f"{os.getenv('PS1_EMOJI')}{os.getenv('PS2_EMOJI')}",
        "P3": f"{os.getenv('PS1_EMOJI')}{os.getenv('PS2_EMOJI')}{os.getenv('PS3_EMOJI')}",
        "P4": f"{os.getenv('PS1_EMOJI')}{os.getenv('PS2_EMOJI')}{os.getenv('PS3_EMOJI')}{os.getenv('PS4_EMOJI')}",
        "P5": f"{os.getenv('PS1_EMOJI')}{os.getenv('PS2_EMOJI')}{os.getenv('PS3_EMOJI')}{os.getenv('PS4_EMOJI')}{os.getenv('PS5_EMOJI')}",
        "G1-G3": f"{os.getenv('GS_EMOJI')}{os.getenv('ES_EMOJI')}{os.getenv('ES_EMOJI')}",
        "G2_G4": f"{os.getenv('GS_EMOJI')}{os.getenv('GS_EMOJI')}{os.getenv('ES_EMOJI')}{os.getenv('ES_EMOJI')}",
        "G3_G4": f"{os.getenv('GS_EMOJI')}{os.getenv('GS_EMOJI')}{os.getenv('GS_EMOJI')}{os.getenv('ES_EMOJI')}",
        "G3_G5": f"{os.getenv('GS_EMOJI')}{os.getenv('GS_EMOJI')}{os.getenv('GS_EMOJI')}{os.getenv('ES_EMOJI')}{os.getenv('ES_EMOJI')}",
        "G4_G5": f"{os.getenv('GS_EMOJI')}{os.getenv('GS_EMOJI')}{os.getenv('GS_EMOJI')}{os.getenv('GS_EMOJI')}{os.getenv('ES_EMOJI')}",
        "N0_G3": f"{os.getenv('ES_EMOJI')}{os.getenv('ES_EMOJI')}{os.getenv('ES_EMOJI')}",
        "N0_G4": f"{os.getenv('ES_EMOJI')}{os.getenv('ES_EMOJI')}{os.getenv('ES_EMOJI')}{os.getenv('ES_EMOJI')}",
        "N0_G5": f"{os.getenv('ES_EMOJI')}{os.getenv('ES_EMOJI')}{os.getenv('ES_EMOJI')}{os.getenv('ES_EMOJI')}{os.getenv('ES_EMOJI')}",
        "N0_P5": f"{os.getenv('ES_EMOJI')}{os.getenv('ES_EMOJI')}{os.getenv('ES_EMOJI')}{os.getenv('ES_EMOJI')}{os.getenv('ES_EMOJI')}",
        "1": f"{os.getenv('S1_EMOJI')}",
        "2": f"{os.getenv('S2_EMOJI')}",
        "3": f"{os.getenv('S3_EMOJI')}",
        "4": f"{os.getenv('S4_EMOJI')}",
        "5": f"{os.getenv('S5_EMOJI')}"
    }

    emoji = conversion.get(db_value)

    return emoji

async def emojify_store(store):
    conversion = {
        "": "",
        "App Store": f"{os.getenv('APP_STORE_EMOJI')}",
        "Google Play": f"{os.getenv('GOOGLE_PLAY_EMOJI')}"
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

async def restart():
    python = sys.executable
    os.execl(python, python, *sys.argv)
