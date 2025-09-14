# CSR2 Discord Bot Jess
Epic Open Source Discord Bot for scraping CSR2 World Records and other Info about the game from inside Discord!<br>
This Bot is brought to you by TheMaintainers.<br>

## Requirements
1. Python
2. Python packages
 - discord.py
 - aiofiles
 - aiohttp
 - aiosignal
 - aiosqlite
 - bs4
 - discord
 - discord-py-interactions
 - discord-py-slash-command
 - discord.py
 - google_play_scraper
 - itunes-app-scraper-dmi
 - pycountry
 - pycountry_convert
 - pypresence
 - python-dotenv
 - requests
 - schedule
 - six
 - urllib3
---
## Data Sources
1. [Project Vision Spreadsheet](https://docs.google.com/spreadsheets/d/1nZ8pGqd5ZmNgc0jcEv-pMcOznzLjdq7eRLHSbgTq9CE) (car data)
2. [CSR Racing Community Discord](https://discord.gg/csr-racing) (car specs only)
 - This is not the official CSR Racing Discord but the one created by the community itself
---
## Installation
You can download the `setup.py` file to a user-defined directory using the following commands.<br>
**Always inspect the file before you run it. You can do so [here](https://github.com/Nitro4CSR/CSR2-Discord-Bot-Jess/blob/2025-Rewrite/setup.py)**<br>

### Windows (PowerShell)
Open Windows Powershell and paste the command from below.<br>
```powershell
Read-Host "Enter the directory to save the file" | ForEach-Object { $d=$_; New-Item -ItemType Directory -Force -Path $d; Invoke-WebRequest "https://raw.githubusercontent.com/Nitro4CSR/CSR2-Discord-Bot-Jess/2025-Rewrite/setup.py" -OutFile "$d\setup.py"; python "$d\setup.py" }
```
### Linux (Bash)
Open a Linux terminal and paste the command from below.<br>
```bash
read -p "Enter the directory to save the file: " d; mkdir -p "$d"; curl -o "$d/setup.py" "https://raw.githubusercontent.com/Nitro4CSR/CSR2-Discord-Bot-Jess/2025-Rewrite/setup.py"; python3 "$d/setup.py"
```
