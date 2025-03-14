import discord
import os
from discord.ext import commands
from discord import app_commands
import helpers
import in_app_logging

logger = helpers.load_logging()

class CommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="csr2_commands", description="List of all available commands")
    @app_commands.choices(command=[app_commands.Choice(name="csr2_wr", value="wr"), app_commands.Choice(name="csr2_wrlist", value="wrlist"), app_commands.Choice(name="csr2_s6_effects", value="s6_effects"), app_commands.Choice(name="csr2_info", value="info"), app_commands.Choice(name="csr2_vision", value="vision"), app_commands.Choice(name="csr2_getlimit", value="getlimit"), app_commands.Choice(name="csr2_share_tune", value="share_tune"), app_commands.Choice(name="csr2_update_tune", value="update_tune"), app_commands.Choice(name="csr2_delete_tune", value="delete_tune"), app_commands.Choice(name="csr2_community_tune", value="community_tune"), app_commands.Choice(name="csr2_customsql", value="customsql"), app_commands.Choice(name="csr2_dbstructure", value="dbstructure"), app_commands.Choice(name="csr2_notify_updates_add", value="notify_updates_add"), app_commands.Choice(name="csr2_notify_updates_delete", value="notify_updates_delete"), app_commands.Choice(name="csr2_version_check", value="csr2_version_check")])
    async def commands(self, interaction: discord.Interaction, command: str = None):
        logger.info(f"COMMANDS - The following command has been used: /csr2_commands command: {command}")
        log = f"COMMANDS - The following command has been used: /csr2_commands command: {command}"
        await interaction.response.defer()

        helpers.load_dotenv

        if command is None:
            command = 'default'

        if command == 'default':
            title_text = 'Available Commands'
        else:
            title_text = 'Command Usage'

        descriptions = {
            'default': f'</csr2_wr:{os.getenv('CSR2_WR_COMMAND')}>\n</csr2_wrlist:{os.getenv('CSR2_WRLIST_COMMAND')}>\n</csr2_s6_effects:{os.getenv('CSR2_S6_EFFECTS_COMMAND')}>\n</csr2_info:{os.getenv('CSR2_INFO_COMMAND')}>\n</csr2_getlimit:{os.getenv('CSR2_GETLIMIT_COMMAND')}>\n</csr2_share_tune:{os.getenv('CSR2_SHARE_TUNE_COMMAND')}>\n</csr2_update_tune:{os.getenv('CSR2_UPDATE_TUNE_COMMAND')}>\n</csr2_delete_tune:{os.getenv('CSR2_DELETE_TUNE_COMMAND')}>\n</csr2_community_tune:{os.getenv('CSR2_COMMUNITY_TUNE_COMMAND')}>\n</csr2_customsql:{os.getenv('CSR2_CUSTOMSQL_COMMAND')}>\n</csr2_dbstructure:{os.getenv('CSR2_DBSTRUCTURE_COMMAND')}>\n</csr2_notify_updates_add:{os.getenv('CSR2_NOTIFY_UPDATES_ADD_COMMAND')}>\n</csr2_notify_updates_delete:{os.getenv('CSR2_NOTIFY_UPDATES_DELETE_COMMAND')}>\n</csr2_version_check:{os.getenv('CSR2_VERSION_CHECK_COMMAND')}>\n',
            'wr': f'## </csr2_wr:{os.getenv('CSR2_WR_COMMAND')}>\nAvailable search operators:\n- car: Accepts in game names, code names and Unique IDs. The later 2 can be found at the bottom of a searched car. (optional)\n- rarity: Dropdown with all imagineable combinations between star count and color (optional)\n- tier: Dropdown with options for T1-T5 (optional)\n- csr2_version: Accepts both OTA versions and game release versions seperate or combined split by a space (optional)\n',
            'wrlist': f'## </csr2_wrlist:{os.getenv('CSR2_WRLIST_COMMAND')}>\nAvailable search operators:\n- car: Accepts in game names, code names and Unique IDs. The later 2 can be found at the bottom of a searched car. (optional)\n- rarity: Dropdown with all imagineable combinations between star count and color (optional)\n- tier: Dropdown with options for T1-T5 (optional)\n- csr2_version: Accepts both OTA versions and game release versions seperate or combined split by a space (optional)\n',
            's6_effects': f'## </csr2_s6_effects:{os.getenv('CSR2_S6_EFFECTS_COMMAND')}>\nAvailable search operators:\n- car: Accepts in game names, code names and Unique IDs. The later 2 can be found at the bottom of a searched car. (optional)\n- rarity: Dropdown with all imagineable combinations between star count and color (optional)\n- tier: Dropdown with options for T1-T5 (optional)\n- csr2_version: Accepts both OTA versions and game release versions seperate or combined split by a space (optional)\n',
            'info': f'## </csr2_info:{os.getenv('CSR2_INFO_COMMAND')}>\nAvailable search operators:\n- car: Accepts in game names, code names and Unique IDs. The later 2 can be found at the bottom of a searched car. (optional)\n- rarity: Dropdown with all imagineable combinations between star count and color (optional)\n- tier: Dropdown with options for T1-T5 (optional)\n- csr2_version: Accepts both OTA versions and game release versions seperate or combined split by a space (optional)\n',
            'vision': f'## </csr2_vision:{os.getenv('CSR2_VISION_COMMAND')}>\nAvailable search operators:\n- car: Accepts in game names, code names and Unique IDs. The later 2 can be found at the bottom of a searched car. (optional)\n- rarity: Dropdown with all imagineable combinations between star count and color (optional)\n- tier: Dropdown with options for T1-T5 (optional)\n- csr2_version: Accepts both OTA versions and game release versions seperate or combined split by a space (optional)\n',
            'getlimit': f'## </csr2_getlimit:{os.getenv('CSR2_GETLIMIT_COMMAND')}>\n- Displays the maximum allowed results that will be posted in the servers channels directly before sending them via direct messages.\n',
            'share_tune': f'## </csr2_share_tune:{os.getenv('CSR2_SHARE_TUNE_COMMAND')}>\nStarts the submission in direct messages for uploading a custom tune to the bot. These uploaded tunes can be for various purposes.\n',
            'update_tune': f'## </csr2_update_tune:{os.getenv('CSR2_UPDATE_TUNE_COMMAND')}>\n- tune_id: An unique identifier integer provided to you when you created your tune to identify the tune you want to edit.\n- pp: the pp rating of your cars tune\n- evo: the evo rating of your cars tune\n- engine_motor: the equipped Engine/Motor upgrade stage for the tune\n- turbo_battery: the equipped Turbo/Battery upgrade stage for the tune\n- intake_inverter: the equipped Intake/Inverter upgrade stage for the tune\n- nitrous_overboost: the equipped Nitrous/Overboost upgrade stage for the tune\n- body: the equipped Body upgrade stage for the tune\n- tires: the equipped Tires upgrade stage for the tune\n- transmission: the equipped Transmission upgrade stage for the tune\n- nitrous: your nitrous tuning setup\n- final_drive: your final drive tuning setup\n- tire_pressure: your tire pressure tuning setup\n- dyno: your tuning setups dyno time\n- purpose: the use case of your tune\n- usage: how to shift your setup\n',
            'delete_tune': f'## </csr2_delete_tune:{os.getenv('CSR2_DELETE_TUNE_COMMAND')}>\n- tune_id: An unique identifier integer provided to you when you created your tune to identify the tune you want to delete.\n',
            'community_tune': f'## </csr2_community_tune:{os.getenv('CSR2_COMMUNITY_TUNE_COMMAND')}>\n- car: Name or DB name of the car you want to search a community tune for\n- tune_id: An unique identifier integer provided to you when you created your tune used to identify the tune\n- tier: Tier of the car you want to search a community tune for\n- rarity: star count and color of the car you want to search a community tune for\n- purpose: the use case you want to search a tune for\n- creator: the creator of the tune you want to search for\n',
            'customsql': f'## </csr2_customsql:{os.getenv('CSR2_CUSTOMSQL_COMMAND')}>\n- database: Defines which database you want to access\n- select: optional variable to define a SELECT prompt of an SQL statement\n- update: optional variable to define a UPDATE prompt of an SQL statement\n- create_table: optional variable to define a CREATE TABLE prompt of an SQL statement (requires Bot admin perms)\n- insert_into: optional variable to define a INSERT INTO prompt of an SQL statement (requires Bot admin perms)\n- from_: optional variable to define a FROM prompt of an SQL statement\n- set_: optional variable to define a SET prompt of an SQL statement (requires Bot admin perms)\n- where: optional variable to define a WHERE prompt of an SQL statement\n',
            'dbstructure': f'## </csr2_dbstructure:{os.getenv('CSR2_DBSTRUCTURE_COMMAND')}>\n- Displays a schematic to show the user the internal database structure\n',
            'notify_updates_add': f'## </csr2_notify_updates_add:{os.getenv('CSR2_NOTIFY_UPDATES_ADD_COMMAND')}>\n- scope: Defaults to "All". Available: CSR2, CSR3, Blog & All (optional)\n',
            'notify_updates_delete': f'## </csr2_notify_updates_delete:{os.getenv('CSR2_NOTIFY_UPDATES_DELETE_COMMAND')}>\n- scope: Defaults to "All". Available: CSR2, CSR3, Blog & All (optional)\n',
            'version_check': f'## </csr2_version_check:{os.getenv('CSR2_VERSION_CHECK_COMMAND')}>\n- app: Select CSR2 or CSR3 to filter the search (optional)\n- store: select Google Play Store or Apple App Store to filter the search (optional)\n- version: type out a specific you search for to filter the search\n- country: use 2 letter country codes (ISO 3166-1 alpha-2) to filter the search'
        }

        description_text = descriptions[command]

        embed = discord.Embed(
            title=title_text,
            description=description_text,
            color=discord.Color(0xff00ff)
        )
        embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')

        await interaction.followup.send(embed=embed)
        await in_app_logging.send_log(self.bot, log, 2, 1, interaction)

async def setup(bot):
    await bot.add_cog(CommandsCog(bot))
