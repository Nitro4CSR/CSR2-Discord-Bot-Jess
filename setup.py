import sys
import subprocess
import zipfile
import io
from pathlib import Path

REQUIREMENTS_URL = "https://raw.githubusercontent.com/Nitro4CSR/CSR2-Discord-Bot-Jess/main/requirements.txt"
ZIP_URL = "https://github.com/Nitro4CSR/CSR2-Discord-Bot-Jess/archive/refs/heads/main.zip"
ENV_URL = "https://raw.githubusercontent.com/Nitro4CSR/CSR2-Discord-Bot-Jess/refs/heads/main/.env"

REQUIREMENTS_PATH = Path("requirements.txt")
ENV_PATH = Path(".env")
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
    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
        for member in zip_ref.infolist():
            if member.filename.endswith(".env"):
                continue
            zip_ref.extract(member)
    print(f"[✓] Bot source extracted to ./{SOURCE_DIR}")

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
    with open(ENV_PATH, "r") as f:
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

def main():
    ensure_requests_installed()
    download_requirements()
    install_requirements()
    download_source()
    download_env()
    configure_env()
    print("\n[✓] Setup complete. Your bot is ready to run!")

if __name__ == "__main__":
    main()
