from dotenv import load_dotenv
import json
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

def load_base_dir():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_dotenv_dir():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')

def load_dotenv_data():
    load_dotenv()

def load_token():
    TOKEN = os.getenv('TOKEN')
    return TOKEN

def load_client_id():
    CLIENT_ID = os.getenv('CLIENT_ID')
    return CLIENT_ID

def load_setup_status():
    FIRST_SETUP_DONE = os.getenv("FIRST_SETUP_DONE", "False").lower() == "true"
    return FIRST_SETUP_DONE

def load_default_pfp():
     return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets/PfP.png')

def load_halloween_pfp():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets/PfP_Halloween.png')

def load_xmas_pfp():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets/PfP_Christmas.png')

def load_bday_pfp():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets/PfP_Birthday.png')

def load_default_name():
    CLIENT_DEFAULT_NAME = os.getenv('CLIENT_DEFAULT_NAME')
    return CLIENT_DEFAULT_NAME

def load_halloween_name():
    CLIENT_HALLOWEEN_NAME = os.getenv('CLIENT_HALLOWEEN_NAME')
    return CLIENT_HALLOWEEN_NAME

def load_xmas_name():
    CLIENT_CHRISTMAS_NAME = os.getenv('CLIENT_CHRISTMAS_NAME')
    return CLIENT_CHRISTMAS_NAME

def load_bday_name():
    CLIENT_BIRTHDAY_NAME = os.getenv('CLIENT_BIRTHDAY_NAME')
    return CLIENT_BIRTHDAY_NAME

def load_bday_month():
    return int(os.getenv('CLIENT_BIRTHDAY_MONTH'))

def load_bday_day():
    return int(os.getenv('CLIENT_BIRTHDAY_DAY'))

def load_super_admin():
    SUPER_ADMIN = os.getenv('SUPER_ADMIN')
    return SUPER_ADMIN

def load_admin_server():
    ADMIN_SERVER = os.getenv('ADMIN_SERVER')
    return ADMIN_SERVER

def load_log_channel():
    LOG_CHANNEL = os.getenv('LOG_CHANNEL_ID')
    return LOG_CHANNEL

def load_admin_file():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources/admins.json')

def load_CSR2_announcement_channel_file():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources/CSR2_announcement_channels.json')

def load_CSR3_announcement_channel_file():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources/CSR3_announcement_channels.json')

def load_blog_announcement_channel_file():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources/Blog_announcement_channels.json')

def load_CSR2_announcement_user_file():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources/CSR2_announcement_users.json')

def load_CSR3_announcement_user_file():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources/CSR3_announcement_users.json')

def load_blog_announcement_user_file():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources/Blog_announcement_users.json')

def load_CSR2versions_json():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources/CSR2_versions.json')

def load_CSR3versions_json():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources/CSR3_versions.json')

def load_blogversions_json():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources/Blog_versions.json')

def load_server_limits():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources/limits.json')

def load_external_db():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources/EDB.db')

def load_community_db():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources/tunes.db')

# File to store admin list
ADMIN_FILE = load_admin_file()

async def load_admins():
    # Load admin user IDs from a JSON file.
    if os.path.exists(ADMIN_FILE):
        try:
            with open(ADMIN_FILE, 'r') as f:
                data = json.load(f)
                # Ensure data is a list of strings
                if isinstance(data, list) and all(isinstance(i, str) for i in data):
                    return set(data)  # Use a set to handle uniqueness
                else:
                    raise ValueError("JSON file is not in the expected format")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {e}")
        except ValueError as e:
            logger.error(f"Value error: {e}")
        except Exception as e:
            logger.error(f"Error loading admin file: {e}")
    else:
        logger.error(f"Admin file '{ADMIN_FILE}' not found.")
    return set()

CSR2_ANNOUNCEMENT_CHANNEL_FILE = load_CSR2_announcement_channel_file()

async def load_CSR2_announcement_channels():
    # Load Channels to announce CSR2 Updates from a json file.
    if os.path.exists(CSR2_ANNOUNCEMENT_CHANNEL_FILE):
        try:
            with open(CSR2_ANNOUNCEMENT_CHANNEL_FILE, 'r') as f:
                data = json.load(f)
                # Ensure data is a list of strings
                if isinstance(data, list) and all(isinstance(i, str) for i in data):
                    return set(data)  # Use a set to handle uniqueness
                else:
                    raise ValueError("JSON file is not in the expected format")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {e}")
        except ValueError as e:
            logger.error(f"Value error: {e}")
        except Exception as e:
            logger.error(f"Error loading CSR2 announcement channel file: {e}")
    else:
        logger.error(f"CSR2 announcement channel file '{CSR2_ANNOUNCEMENT_CHANNEL_FILE}' not found.")
    return set()

CSR3_ANNOUNCEMENT_CHANNEL_FILE = load_CSR3_announcement_channel_file()

async def load_CSR3_announcement_channels():
    # Load Channels to announce CSR2 Updates from a json file.
    if os.path.exists(CSR3_ANNOUNCEMENT_CHANNEL_FILE):
        try:
            with open(CSR3_ANNOUNCEMENT_CHANNEL_FILE, 'r') as f:
                data = json.load(f)
                # Ensure data is a list of strings
                if isinstance(data, list) and all(isinstance(i, str) for i in data):
                    return set(data)  # Use a set to handle uniqueness
                else:
                    raise ValueError("JSON file is not in the expected format")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {e}")
        except ValueError as e:
            logger.error(f"Value error: {e}")
        except Exception as e:
            logger.error(f"Error loading CSR3 announcement channel file: {e}")
    else:
        logger.error(f"CSR3 announcement channel file '{CSR3_ANNOUNCEMENT_CHANNEL_FILE}' not found.")
    return set()

BLOG_ANNOUNCEMENT_CHANNEL_FILE = load_blog_announcement_channel_file()

async def load_blog_announcement_channels():
    # Load Channels to announce CSR2 Updates from a json file.
    if os.path.exists(BLOG_ANNOUNCEMENT_CHANNEL_FILE):
        try:
            with open(BLOG_ANNOUNCEMENT_CHANNEL_FILE, 'r') as f:
                data = json.load(f)
                # Ensure data is a list of strings
                if isinstance(data, list) and all(isinstance(i, str) for i in data):
                    return set(data)  # Use a set to handle uniqueness
                else:
                    raise ValueError("JSON file is not in the expected format")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {e}")
        except ValueError as e:
            logger.error(f"Value error: {e}")
        except Exception as e:
            logger.error(f"Error loading CSR3 announcement channel file: {e}")
    else:
        logger.error(f"CSR3 announcement channel file '{BLOG_ANNOUNCEMENT_CHANNEL_FILE}' not found.")
    return set()

CSR2_ANNOUNCEMENT_USER_FILE = load_CSR2_announcement_user_file()

async def load_CSR2_announcement_users():
    # Load Channels to announce CSR2 Updates from a json file.
    if os.path.exists(CSR2_ANNOUNCEMENT_USER_FILE):
        try:
            with open(CSR2_ANNOUNCEMENT_USER_FILE, 'r') as f:
                data = json.load(f)
                # Ensure data is a list of strings
                if isinstance(data, list) and all(isinstance(i, str) for i in data):
                    return set(data)  # Use a set to handle uniqueness
                else:
                    raise ValueError("JSON file is not in the expected format")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {e}")
        except ValueError as e:
            logger.error(f"Value error: {e}")
        except Exception as e:
            logger.error(f"Error loading CSR2 announcement user file: {e}")
    else:
        logger.error(f"CSR2 announcement user file '{CSR2_ANNOUNCEMENT_USER_FILE}' not found.")
    return set()

CSR3_ANNOUNCEMENT_USER_FILE = load_CSR3_announcement_user_file()

async def load_CSR3_announcement_users():
    # Load Channels to announce CSR2 Updates from a json file.
    if os.path.exists(CSR3_ANNOUNCEMENT_USER_FILE):
        try:
            with open(CSR3_ANNOUNCEMENT_USER_FILE, 'r') as f:
                data = json.load(f)
                # Ensure data is a list of strings
                if isinstance(data, list) and all(isinstance(i, str) for i in data):
                    return set(data)  # Use a set to handle uniqueness
                else:
                    raise ValueError("JSON file is not in the expected format")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {e}")
        except ValueError as e:
            logger.error(f"Value error: {e}")
        except Exception as e:
            logger.error(f"Error loading CSR3 announcement user file: {e}")
    else:
        logger.error(f"Admin CSR3 announcement user '{CSR3_ANNOUNCEMENT_USER_FILE}' not found.")
    return set()

BLOG_ANNOUNCEMENT_USER_FILE = load_blog_announcement_user_file()

async def load_blog_announcement_users():
    # Load Channels to announce CSR2 Updates from a json file.
    if os.path.exists(BLOG_ANNOUNCEMENT_USER_FILE):
        try:
            with open(BLOG_ANNOUNCEMENT_USER_FILE, 'r') as f:
                data = json.load(f)
                # Ensure data is a list of strings
                if isinstance(data, list) and all(isinstance(i, str) for i in data):
                    return set(data)  # Use a set to handle uniqueness
                else:
                    raise ValueError("JSON file is not in the expected format")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {e}")
        except ValueError as e:
            logger.error(f"Value error: {e}")
        except Exception as e:
            logger.error(f"Error loading CSR3 announcement user file: {e}")
    else:
        logger.error(f"Admin CSR3 announcement user '{BLOG_ANNOUNCEMENT_USER_FILE}' not found.")
    return set()

async def emojify_tier(db_value):
    conversion = {
        '': '',
        'T1': f'{os.getenv('T1_EMOJI')}',
        'T2': f'{os.getenv('T2_EMOJI')}',
        'T3': f'{os.getenv('T3_EMOJI')}',
        'T4': f'{os.getenv('T4_EMOJI')}',
        'T5': f'{os.getenv('T5_EMOJI')}'
    }

    emoji = conversion.get(db_value)

    return emoji

async def emojify_rarity(db_value):
    conversion = {
        '': '',
        '0': f'{os.getenv('NS_EMOJI')}{os.getenv('NS_EMOJI')}{os.getenv('NS_EMOJI')}{os.getenv('NS_EMOJI')}{os.getenv('NS_EMOJI')}',
        'G1': f'{os.getenv('GS_EMOJI')}',
        'G2': f'{os.getenv('GS_EMOJI')}{os.getenv('GS_EMOJI')}',
        'G3': f'{os.getenv('GS_EMOJI')}{os.getenv('GS_EMOJI')}{os.getenv('GS_EMOJI')}',
        'G4': f'{os.getenv('GS_EMOJI')}{os.getenv('GS_EMOJI')}{os.getenv('GS_EMOJI')}{os.getenv('GS_EMOJI')}',
        'G5': f'{os.getenv('GS_EMOJI')}{os.getenv('GS_EMOJI')}{os.getenv('GS_EMOJI')}{os.getenv('GS_EMOJI')}{os.getenv('GS_EMOJI')}',
        'P1': f'{os.getenv('PS1_EMOJI')}',
        'P2': f'{os.getenv('PS1_EMOJI')}{os.getenv('PS2_EMOJI')}',
        'P3': f'{os.getenv('PS1_EMOJI')}{os.getenv('PS2_EMOJI')}{os.getenv('PS3_EMOJI')}',
        'P4': f'{os.getenv('PS1_EMOJI')}{os.getenv('PS2_EMOJI')}{os.getenv('PS3_EMOJI')}{os.getenv('PS4_EMOJI')}',
        'P5': f'{os.getenv('PS1_EMOJI')}{os.getenv('PS2_EMOJI')}{os.getenv('PS3_EMOJI')}{os.getenv('PS4_EMOJI')}{os.getenv('PS5_EMOJI')}',
    }

    emoji = conversion.get(db_value)

    return emoji

async def emojify_store(store):
    conversion = {
        '': '',
        'App Store': f'{os.getenv('APP_STORE_EMOJI')}',
        'Google Play': f'{os.getenv('GOOGLE_PLAY_EMOJI')}'
    }

    emoji = conversion.get(store)

    return emoji
