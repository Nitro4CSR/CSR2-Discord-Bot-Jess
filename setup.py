import sys
import subprocess
import zipfile
import io
import json
from pathlib import Path

REQUIREMENTS_URL = "https://raw.githubusercontent.com/Nitro4CSR/CSR2-Discord-Bot-Jess/2025-Rewrite/requirements.txt"
ZIP_URL = "https://github.com/Nitro4CSR/CSR2-Discord-Bot-Jess/archive/refs/heads/2025-Rewrite.zip"
ENV_URL = "https://github.com/Nitro4CSR/CSR2-Discord-Bot-Jess/blob/2025-Rewrite/.env"

REQUIREMENTS_PATH = Path("requirements.txt")
ENV_PATH = Path(".env")
CONFIG_PATH = Path("config/config.json")
SOURCE_DIR = Path("CSR2-Discord-Bot-Jess-main")

def ensure_requests_installed():
    global requests
    try:
        import requests
        print("[✓] 'requests' already installed.")
    except ImportError:
        print("[*] Installing 'requests'...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        print("[✓] 'requests' installed.")
        import requests

def download_requirements():
    if REQUIREMENTS_PATH.exists():
        print("[!] requirements.txt already exists. Skipping download.")
        return
    print("[*] Downloading requirements.txt...")
    response = requests.get(REQUIREMENTS_URL)
    response.raise_for_status()
    REQUIREMENTS_PATH.write_text(response.text)
    print("[✓] requirements.txt downloaded.")

def install_requirements():
    print("[*] Installing dependencies from requirements.txt...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(REQUIREMENTS_PATH)])
    print("[✓] All requirements installed.")

def download_source():
    if SOURCE_DIR.exists():
        print(f"[!] Source folder '{SOURCE_DIR}' already exists. Skipping download.")
        return
    print("[*] Downloading and extracting bot source code...")
    response = requests.get(ZIP_URL)
    response.raise_for_status()
    excluded_files = ['.env', 'setup.py']

    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
        for member in zip_ref.infolist():
            filename = member.filename
            if filename in excluded_files:
                continue
            parts = Path(filename).parts
            if len(parts) > 1:
                target_path = Path(*parts[1:])
                if member.is_dir():
                    target_path.mkdir(parents=True, exist_ok=True)
                else:
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    with zip_ref.open(member) as source_file:
                        with open(target_path, "wb") as target_file:
                            target_file.write(source_file.read())
    print("[✓] Bot source extracted to current directory.")

def download_env():
    if ENV_PATH.exists():
        print("[!] .env file already exists. Skipping download.")
        return
    print("[*] Downloading .env template...")
    response = requests.get(ENV_URL)
    response.raise_for_status()
    ENV_PATH.write_text(response.text)
    print("[✓] .env template downloaded.")

def configure_env():
    print("[*] Configuring .env file...")

    updated_lines = []
    with open(ENV_PATH, "r", encoding='utf-8') as f:
        for line in f:
            if "=" not in line or line.strip().startswith("#"):
                updated_lines.append(line)
                continue
            key, value = line.strip().split("=", 1)
            if key == "FIRST_SETUP_DONE":
                updated_lines.append(line)
                continue
            if "YOUR_" in value or "DISCORD_" in value or "DEFAULT" in value or "DAY_INTEGER" in value or "MONTH_INTEGER" in value:
                user_input = input(f"Enter value for {key} [{value}]: ").strip()
                updated_lines.append(f"{key}={user_input or value}\n")
            else:
                updated_lines.append(line + "\n")
    with open(ENV_PATH, "w") as f:
        f.writelines(updated_lines)
    print("[✓] .env file configured.")

def configure_config():
    print("[*] Configuring config.json file...")
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    def prompt_for_value(key, current_value):
        if current_value is None:
            user_input = input(f"Enter a value for '{key}' [leave blank to keep null]: ").strip()
            return user_input if user_input else None
        if isinstance(current_value, list) and len(current_value) == 0:
            while True:
                if key in ["ClientAdminIDs", "ClientAdminServers"]:
                    user_input = input(f"Enter comma-separated integers for '{key}' (not advised to leave empty): ").strip()
                else:
                    user_input = input(f"Enter comma-separated integers for '{key}' or leave blank to keep empty: ").strip()
                if not user_input:
                    return []
                try:
                    return [int(x.strip()) for x in user_input.split(",")]
                except ValueError:
                    print(f"[!] Invalid input for '{key}'. Please enter only integers separated by commas.")
        return current_value

    for key, value in data.items():
        if key == "DynamicStatusList":
            continue
        if value is None or (isinstance(value, list) and len(value) == 0):
            data[key] = prompt_for_value(key, value)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print("[✓] config.json configured.")

def main():
    ensure_requests_installed()
    download_requirements()
    install_requirements()
    download_source()
    download_env()
    configure_env()
    configure_config()
    print("\n[✓] Setup complete. Your bot is ready to run!")

if __name__ == "__main__":
    main()
