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

    async def cog_load(self):

        @app_commands.command(name=self.bot.localisation.get('UPDATECODE_CMD_NAME'), description=self.bot.localisation.get('UPDATECODE_CMD_DESC'))
        @app_commands.describe(restart_in=self.bot.localisation.get('UPDATECODE_CMD_RESTART_IN'))
        async def updatecode(interaction: discord.Interaction, restart_in: str = None):
            await interaction.response.defer(ephemeral=True)
            try:
                header = self.bot.localisation.get('UPDATECODE_LOG_HEADER')
                logger.info(f"{header}{self.bot.localisation.get('LOG_CMD_TRIGGERED')} /{self.bot.localisation.get('UPDATECODE_CMD_NAME')} restart_in: {restart_in}")
                log = f"{header}{self.bot.localisation.get('LOG_CMD_TRIGGERED')} /{self.bot.localisation.get('UPDATECODE_CMD_NAME')} restart_in: {restart_in}"
	    
                admins = await helpers.load_file('Admin file')
                if str(interaction.user.id) not in admins or int(interaction.user.id) not in await helpers.load_json_key("config", "ClientAdminIDs"):
                    logger.info(f"{header}{self.bot.localisation.get('ADMIN_LOG_NOT_ADMIN')}")
                    log += f"\n{header}{self.bot.localisation.get('ADMIN_LOG_NOT_ADMIN')}"
                    await interaction.followup.send(f"{self.bot.localisation.get('ADMIN_MSG_NO_PERMISSION')}", ephemeral=True)
                    await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
                    return
	    
                if restart_in and (await helpers.is_float(restart_in) or "," in restart_in):
                    restart_in = float(restart_in.replace(",", "."))
                else:
                    restart_in = 0.0
                if await helpers.is_float(restart_in) == False:
                    await interaction.followup.send(f"{self.bot.localisation.get('UPDATE_CODE_MSG_ERROR_NOT_FLOAT')}", ephemeral=True)
                    logger.info(f"restart_in ({restart_in}) {self.bot.localisation.get('UPDATECODE_LOG_ERROR_FLOAT')}")
                    log += f"restart_in ({restart_in}) {self.bot.localisation.get('UPDATECODE_LOG_ERROR_FLOAT')}"
                    await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
                    return
	    
                logger.info(f"{header}{self.bot.localisation.get('ADMIN_LOG_IS_ADMIN')}")
                log += f"\n{header}{self.bot.localisation.get('ADMIN_LOG_IS_ADMIN')}"
	    
                await interaction.followup.send(f"{self.bot.localisation.get('UPDATE_CODE_MSG_DOWNLOAD')}", ephemeral=True)
                logger.info(f"{header}{self.bot.localisation.get('UPDATECODE_LOG_DOWNLOAD')}")
                log += f"\n{header}{self.bot.localisation.get('UPDATECODE_LOG_DOWNLOAD')}"
	    
                repo_zip_url = "https://github.com/Nitro4CSR/CSR2-Discord-Bot-Jess/archive/refs/heads/Rewrite.zip"
                repo_commit_url = "https://api.github.com/repos/Nitro4CSR/CSR2-Discord-Bot-Jess/commits/Rewrite"
                zip_path = "CSR2-Discord-Bot-Jess-Rewrite.zip"
                extract_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "update_temp")
	    
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(repo_zip_url) as resp:
                            if resp.status != 200:
                                logger.info(f"{header}{self.bot.localisation.get('UPDATECODE_LOG_ERROR_HTTP')} {resp.status}")
                                log += f"\n{header}{self.bot.localisation.get('UPDATECODE_LOG_ERROR_HTTP')} {resp.status}"
                                await interaction.followup.send(f"{self.bot.localisation.get('UPDATE_CODE_MSG_ERROR_DOWNLOAD')} HTTP {resp.status}", ephemeral=True)
                                await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
                                return
                            with open(zip_path, "wb") as f:
                                f.write(await resp.read())
	    
                    if restart_in is not None:
                        logger.info(f"{header}{self.bot.localisation.get('UPDATECODE_LOG_DELAY')} {int(round(float(restart_in) * 3600, 0))}s")
                        log += f"{header}{self.bot.localisation.get('UPDATECODE_LOG_DELAY')} {int(round(float(restart_in) * 3600, 0))}s"
                        await asyncio.sleep(round(float(restart_in) * 3600, 0))
	    
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), extract_folder))
	    
                    extracted_name = os.listdir(extract_folder)[0]
                    extracted_path = os.path.join(extract_folder, extracted_name)
	    
                    excluded_folders = ['config', 'resources']
                    excluded_files = ['.env', '.gitattributes', 'LICENSE', 'README.md', 'setup.py', 'update.py']
	    
                    for item in os.listdir(extracted_path):
                        if item in excluded_folders or item in excluded_files:
                            logger.info(f"{header}{self.bot.localisation.get('UPDATECODE_LOG_SKIP_FILE')} {item}")
                            log += f"{header}{self.bot.localisation.get('UPDATECODE_LOG_SKIP_FILE')} {item}"
                            continue
	    
                        src = os.path.join(extracted_path, item)
                        dest = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), item)
                        logger.info(f"{self.bot.localisation.get('UPDATECODE_LOG_SOURCE')} {src}\n{self.bot.localisation.get('UPDATECODE_LOG_DESTINATION')} {dest}")
                        log += f"\n{self.bot.localisation.get('UPDATECODE_LOG_SOURCE')} {src}\n{self.bot.localisation.get('UPDATECODE_LOG_DESTINATION')} {dest}"
	    
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
                                    logger.info(f"{header}{self.bot.localisation.get('UPDATECODE_LOG_DOWNLOAD_VERSION')} {commit_id}")
                                    log += f"\n{header}{self.bot.localisation.get('UPDATECODE_LOG_DOWNLOAD_VERSION')} {commit_id}"
                                    await interaction.followup.send(f"{self.bot.localisation.get('UPDATE_CODE_MSG_VERSION')} {commit_id}", ephemeral=True)
	    
                                    VERSION_FILE = await helpers.load_file_path(f'Version')
                                    async with aiofiles.open(VERSION_FILE, mode="w") as file:
                                        await file.write(json.dumps(versions_new))
                                else:
                                    raise Exception
                    except:
                        logger.info(f"{header}{self.bot.localisation.get('UPDATECODE_LOG_ERROR_COMMIT_ID')} {response.status}")
                        log += f"\n{header}{self.bot.localisation.get('UPDATECODE_LOG_ERROR_COMMIT_ID')} {response.status}"
	    
                    logger.info(f"{header}{self.bot.localisation.get('UPDATECODE_LOG_DONE')}")
                    log += f"\n{header}{self.bot.localisation.get('UPDATECODE_LOG_DONE')}"
                    await interaction.followup.send(f"{self.bot.localisation.get('UPDATE_CODE_MSG_DONE')}", ephemeral=True)
	    
                except Exception as e:
                    logger.error(f"{header}{self.bot.localisation.get('UPDATECODE_LOG_ERROR')} {str(e)}")
                    log += f"{header}{self.bot.localisation.get('UPDATECODE_LOG_ERROR')} {str(e)}"
                    await interaction.followup.send(f"{header}{self.bot.localisation.get('UPDATE_CODE_MSG_ERROR')} {str(e)}", ephemeral=True)
                    await in_app_logging.send_log(self.bot, log, 0, 1, interaction)
                logger.info(f"{header}{self.bot.localisation.get('UPDATECODE_LOG_RESTART')}")
                log += f"\n{header}{self.bot.localisation.get('UPDATECODE_LOG_RESTART')}"
                await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
                await helpers.restart()
            except Exception as e:
                await interaction.followup.send(f"{self.bot.localisation.get('MSG_ERROR_FETCH')} {e}")
                logger.info(f"{self.bot.localisation.get('LOG_ERROR_FETCH')} {e}")
                log += f"{self.bot.localisation.get('LOG_ERROR_FETCH')} {e}"
                await in_app_logging.send_log(self.bot, log, 0, 1, interaction)

        self.bot.tree.add_command(updatecode, guilds=[discord.Object(id=int(server)) for server in await helpers.load_json_key("config", "ClientAdminServers")])

async def setup(bot):
    ADMIN_SERVERS = await helpers.load_json_key("config", "ClientAdminServers")
    for server in ADMIN_SERVERS:
        await bot.add_cog(UpdateCodeCog(bot), guilds=[discord.Object(id=int(server))], override=True)
