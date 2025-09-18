import os
import requests
import zipfile
import shutil
import json
import logging

repo_zip_url = "https://github.com/Nitro4CSR/CSR2-Discord-Bot-Jess/archive/refs/heads/2025-Rewrite.zip"
repo_commit_url = "https://api.github.com/repos/Nitro4CSR/CSR2-Discord-Bot-Jess/commits/2025-Rewrite"
zip_path = "CSR2-Discord-Bot-Jess-2025-Rewrite.zip"
base_dir = os.path.dirname(os.path.abspath(__file__))
extract_folder = os.path.join(base_dir, "update_temp")
excluded_folders = ['config', 'resources']
excluded_files = ['.env', '.gitattributes', 'LICENSE', 'README.md', 'config.json']
version_file_path = os.path.join(base_dir, 'resources', 'version.json')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Updater")

def load_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, mode='r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_file(file_path, data):
    with open(file_path, mode="w", encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def main():
    try:
        logger.info("Downloading update...")
        r = requests.get(repo_zip_url)
        if r.status_code != 200:
            logger.error(f"Failed to download ZIP: HTTP {r.status_code}")
            return
        with open(zip_path, "wb") as f:
            f.write(r.content)
        logger.info("Download complete.")

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_folder)

        extracted_name = os.listdir(extract_folder)[0]
        extracted_path = os.path.join(extract_folder, extracted_name)

        for item in os.listdir(extracted_path):
            if item in excluded_folders or item in excluded_files:
                logger.info(f"Skipping {item}")
                continue
            src = os.path.join(extracted_path, item)
            dest = os.path.join(base_dir, item)
            logger.info(f"Updating {src} -> {dest}")
            if os.path.isdir(src):
                if os.path.exists(dest):
                    shutil.rmtree(dest)
                shutil.copytree(src, dest)
            else:
                shutil.copy2(src, dest)

        os.remove(zip_path)
        shutil.rmtree(extract_folder)
        logger.info("Update applied successfully.")

        r = requests.get(repo_commit_url)
        if r.status_code == 200:
            response = r.json()
            commit_id = response['sha'][:7]
            versions = load_file(version_file_path)
            if not isinstance(versions, list):
                versions = []
            versions_new = [commit_id] + versions[:1]
            save_file(version_file_path, versions_new)
            logger.info(f"Updated version file to commit {commit_id}")
        else:
            logger.warning(f"Failed to fetch commit info: HTTP {r.status_code}")

    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
