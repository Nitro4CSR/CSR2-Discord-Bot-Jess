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

def load_token():
    TOKEN = os.getenv('TOKEN')
    return TOKEN

def load_client_id():
    CLIENT_ID = os.getenv('CLIENT_ID')
    return CLIENT_ID

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
    return os.path.join('resources/admins.json')

def load_external_db():
    return os.path.join('resources/EDB.db')

def load_community_db():
    return os.path.join('resources/tunes.db')

def load_server_limits():
    return os.path.join('resources/limits.json')

# File to store admin list
ADMIN_FILE = load_admin_file()

def load_admins():
    """Load admin user IDs from a JSON file."""
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
