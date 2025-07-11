import aiofiles
import discord
import json
from discord.ext import commands
from discord import app_commands
import in_app_logging
import helpers
import aiohttp
import asyncio
import os
import shutil
import zipfile

logger = helpers.load_logging()

class UpdateCodeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="csr2_updatecode", description="Manually update the Bot's Source Code")
    @app_commands.describe(restart_in="Delay time in hours until the bot auto restarts after the code update; format: X.XX...")
    async def update_code(self, interaction: discord.Interaction, restart_in: str = None):
        logger.info(f"UPDATECODE - The following command has been used: /csr2_updatecode restart_in: {restart_in}")
        log = f"UPDATECODE - The following command has been used: /csr2_updatecode restart_in: {restart_in}"
        await interaction.response.defer(ephemeral=True)

        admins = await helpers.load_file('Admin file')
        if str(interaction.user.id) not in admins or str(interaction.user.id) != str(await helpers.load_super_admin()):
            logger.info(f"UPDATECODE - Interaction canceled, user lacks permissions...")
            log += "\nUPDATECODE - Interaction canceled, user lacks permissions..."
            await interaction.followup.send("You do not have permission to use this command.", ephemeral=True)
            await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
            return
        
        if restart_in and (await helpers.is_float(restart_in) or "," in restart_in):
            restart_in = float(restart_in.replace(",", "."))
        else:
            restart_in = 0.0
        if await helpers.is_float(restart_in) == False:
            await interaction.followup.send("The value you input for `restart_in` is not a valid float can can't be converted to one. Please rerun the command and Input a valid float.\nFormat: `X.XX...`", ephemeral=True)
            logger.info(f"restart_in ({restart_in}) is not a valid float")
            log += f"restart_in ({restart_in}) is not a valid float"
            await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
            return

        logger.info(f"UPDATECODE - User has permission to run command")
        log += "\nUPDATECODE - User has permission to run command"

        await interaction.followup.send("⬇️ Downloading and applying update from GitHub...", ephemeral=True)
        logger.info(f"UPDATECODE - ⬇️ Downloading and applying update from GitHub...")
        log += "\nUPDATECODE - ⬇️ Downloading and applying update from GitHub..."

        repo_zip_url = "https://github.com/Nitro4CSR/CSR2-Discord-Bot-Jess/archive/refs/heads/main.zip"
        repo_commit_url = "https://api.github.com/repos/Nitro4CSR/CSR2-Discord-Bot-Jess/commits/main"
        zip_path = "CSR2-Discord-Bot-Jess-main.zip"
        extract_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "update_temp")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(repo_zip_url) as resp:
                    if resp.status != 200:
                        logger.info(f"UPDATECODE - ❌ Failed to download ZIP: HTTP {resp.status}")
                        log += f"\nUPDATECODE - ❌ Failed to download ZIP: HTTP {resp.status}"
                        await interaction.followup.send(f"UPDATECODE - ❌ Failed to download ZIP: HTTP {resp.status}", ephemeral=True)
                        await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
                        return
                    with open(zip_path, "wb") as f:
                        f.write(await resp.read())

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), extract_folder))

            extracted_name = os.listdir(extract_folder)[0]
            extracted_path = os.path.join(extract_folder, extracted_name)

            excluded_folders = ['resources']
            excluded_files = ['.env', 'README.md', 'LICENSE', '.gitattributes']

            for item in os.listdir(extracted_path):
                if item in excluded_folders or item in excluded_files:
                    logger.info(f"UPDATECODE - Skipping excluded file: {item}")
                    continue

                src = os.path.join(extracted_path, item)
                dest = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), item)
                logger.info(f"Source: {src}\nDestination: {dest}")
                log += f"\nSource: {src}\nDestination: {dest}"

                if os.path.isdir(src):
                    if os.path.exists(dest):
                        shutil.rmtree(dest)
                    shutil.copytree(src, dest)
                else:
                    shutil.copy2(src, dest)

            os.remove(zip_path)
            shutil.rmtree(extract_folder)

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(repo_commit_url) as response:
                        if response.status == 200:
                            response = await response.json()
                            commit_id = response['sha'][:7]
                            versions = await helpers.load_file('Version')
                            versions_new = [commit_id, next(iter(versions))]
                            logger.info(f"UPDATECODE - Downloaded Verion: {commit_id}")
                            log += f"\nUPDATECODE - Downloaded Verion: {commit_id}"
                            await interaction.followup.send(f"Downloaded Verion: {commit_id}", ephemeral=True)

                            VERSION_FILE = await helpers.load_file_path(f'Version')
                            async with aiofiles.open(VERSION_FILE, mode="w") as file:
                                await file.write(json.dumps(versions_new))
                        else:
                            raise Exception
            except:
                logger.info(f"UPDATECODE - ❌ Failed to get latest commitID: HTTP {response.status}")
                log += f"\nUPDATECODE - ❌ Failed to get latest commitID: HTTP {response.status}"

            log += "\nUPDATECODE - ✅ Code update complete."
            logger.info("UPDATECODE - Code update completed successfully.")
            await interaction.followup.send("✅ Update complete. Restarting bot...", ephemeral=True)

        except Exception as e:
            log += f"UPDATECODE - ❗ Update failed: {str(e)}"
            logger.error(f"UPDATECODE - Error during update: {e}")
            await interaction.followup.send(f"UPDATECODE - ❗ Update failed: {str(e)}", ephemeral=True)
            await in_app_logging.send_log(self.bot, log, 0, 1, interaction)

        if restart_in is not None:
            logger.info(f"Delaying restart for {int(round(float(restart_in) * 3600, 0))} second(s)")
            log += f"Delaying restart for {int(round(float(restart_in) * 3600, 0))} second(s)"
            await asyncio.sleep(round(float(restart_in) * 3600, 0))
        logger.info("UPDATECODE - Restarting bot...")
        log += "\nUPDATECODE - Restarting bot..."
        await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
        await helpers.restart()

async def setup(bot):
    ADMIN_SERVER = await helpers.load_admin_server()
    await bot.add_cog(UpdateCodeCog(bot), guilds=[discord.Object(id=int(ADMIN_SERVER))], override=True)
