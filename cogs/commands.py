import discord
from discord.ext import commands
from discord import app_commands
import logging
import in_app_logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="csr2_commands", description="List of all available commands")
    @app_commands.choices(command=[app_commands.Choice(name="csr2_wr", value="wr"), app_commands.Choice(name="csr2_wrlist", value="wrlist"), app_commands.Choice(name="csr2_s6_effects", value="s6_effects"), app_commands.Choice(name="csr2_info", value="info"), app_commands.Choice(name="csr2_getlimit", value="getlimit"), app_commands.Choice(name="csr2_share_tune", value="share_tune"), app_commands.Choice(name="csr2_update_tune", value="update_tune"), app_commands.Choice(name="csr2_delete_tune", value="delete_tune"), app_commands.Choice(name="csr2_community_tune", value="community_tune"), app_commands.Choice(name="csr2_customsql", value="customsql"), app_commands.Choice(name="csr2_dbstructure", value="dbstructure"), app_commands.Choice(name="csr2_notify_updates_add", value="notify_updates_add"), app_commands.Choice(name="csr2_notify_updates_delete", value="notify_updates_delete"), app_commands.Choice(name="csr2_version_search", value="csr2_version_search")])
    async def commands(self, interaction: discord.Interaction, command: str = None):
        # Log the command usage and parameters
        logger.info(f"The following command has been used: /csr2_commands command: {command}")
        log = f"The following command has been used: /csr2_commands command: {command}"
        await interaction.response.defer()

        if command is None:
            command = 'default'

        if command == 'default':
            title_text = 'Available Commands'
        else:
            title_text = 'Command Usage'

        descriptions = {
            'default': '</csr2_wr:1265025856539983889>\n</csr2_wrlist:1265025856539983890>\n</csr2_s6_effects:1265323078884266098>\n</csr2_info:1266821832519192696>\n</csr2_getlimit:1271416779469750389>\n</csr2_share_tune:1281314860952715285>\n</csr2_update_tune:1281314860952715286>\n</csr2_delete_tune:1281314860952715287>\n</csr2_community_tune:1281314860952715288>\n</csr2_customsql:1279346701986955296>\n</csr2_dbstructure:1279346701986955297>\n</csr2_notify_updates_add:1312451900288794668>\n</csr2_notify_updates_delete:1312451900288794669>\n</csr2_version_check:1330272687779610756>\n',
            'wr': '## </csr2_wr:1265025856539983889>\nAvailable search operators:\n- car: Accepts Ingame names, code names and Unique IDs. The later 2 can be found at the bottom of a searched car. (optional)\n- rarity: Dropdown with all imagineable combinations between star count and color (optional)\n- tier: Dropdown with options for T1-T5 (optional)\n- csr2_version: Accepts both OTA versions and game release versions seperate or combined split by a space (optional)\n',
            'wrlist': '## </csr2_wrlist:1265025856539983890>\nAvailable search operators:\n- car: Accepts Ingame names, code names and Unique IDs. The later 2 can be found at the bottom of a searched car. (optional)\n- rarity: Dropdown with all imagineable combinations between star count and color (optional)\n- tier: Dropdown with options for T1-T5 (optional)\n- csr2_version: Accepts both OTA versions and game release versions seperate or combined split by a space (optional)\n',
            's6_effects': '## </csr2_s6_effects:1265323078884266098>\nAvailable search operators:\n- car: Accepts Ingame names, code names and Unique IDs. The later 2 can be found at the bottom of a searched car. (optional)\n- rarity: Dropdown with all imagineable combinations between star count and color (optional)\n- tier: Dropdown with options for T1-T5 (optional)\n- csr2_version: Accepts both OTA versions and game release versions seperate or combined split by a space (optional)\n',
            'info': '## </csr2_info:1266821832519192696>\nAvailable search operators:\n- car: Accepts Ingame names, code names and Unique IDs. The later 2 can be found at the bottom of a searched car. (optional)\n- rarity: Dropdown with all imagineable combinations between star count and color (optional)\n- tier: Dropdown with options for T1-T5 (optional)\n- csr2_version: Accepts both OTA versions and game release versions seperate or combined split by a space (optional)\n',
            'getlimit': '## </csr2_getlimit:1271416779469750389>\n- Displays the maximum allowed results that will be posted in the servers channels directly\n',
            'share_tune': '## </csr2_share_tune:1281314860952715285>\nStarts a submission loop in your DMs so you can share your custom tunes for various purposes.\n',
            'update_tune': '## </csr2_update_tune:1281314860952715286>\n- tune_id: An unique identifier integer provided to you when you created your tune and needed to point at the tune you want to edit\n- pp: the pp rating of your cars tune\n- evo: the evo rating of your cars tune\n- engine_motor: the equipped upgrade stage in the category Engine/Motor\n- turbo_battery: the equipped upgrade stage in the category Turbo/Battery\n- intake_inverter: the equipped upgrade stage in the category Intake/Inverter\n- nitrous_overboost: the equipped upgrade stage in the category Nitrous/Overboost\n- body: the equipped upgrade stage in the category Body\n- tires: the equipped upgrade stage in the category Tires\n- transmission: the equipped upgrade stage in the category Transmission\n- nitrous: your nitrous tuning setup\n- final_drive: your final drive tuning setup\n- tire_pressure: your tire pressure tuning setup\n- dyno: your tuning setups dyno time\n- purpose: the use case of your tune\n- usage: how to shift your setup\n',
            'delete_tune': '## </csr2_delete_tune:1281314860952715287>\n- tune_id: An unique identifier integer provided to you when you created your tune and needed to point at the tune you want to edit\n',
            'community_tune': '## </csr2_community_tune:1281314860952715288>\n- car: Name or DB name of the car you want to search a community tune for\n- tune_id: An unique identifier integer provided to you when you created your tune and needed to point at the tune you want to edit\n- tier: Tier of the car you want to search a community tune for\n- rarity: star count and color of the car you want to search a community tune for\n- purpose: the use case you want to search a tune for\n- creator: the creator of the tune you want to search for\n',
            'customsql': '## </csr2_customsql:1279346701986955296>\n- database: defines which database you want to access\n- select: optional variable to define a SELECT prompt of an SQL statement\n- update: optional variable to define a UPDATE prompt of an SQL statement\n- create_table: optional variable to define a CREATE TABLE prompt of an SQL statement (requires Bot admin perms)\n- insert_into: optional variable to define a INSERT INTO prompt of an SQL statement (requires Bot admin perms)\n- from_: optional variable to define a FROM prompt of an SQL statement\n- set_: optional variable to define a SET prompt of an SQL statement (requires Bot admin perms)\n- where: optional variable to define a WHERE prompt of an SQL statement\n',
            'dbstructure': '## </csr2_dbstructure:1279346701986955297>\n- displays a schematic to show the user the internal database structure\n',
            'notify_updates_add': '## </csr2_notify_updates_add:1312451900288794668>\n- scope: Defaults to "All". Available: CSR2, CSR3, Blog & All (optional)\n',
            'notify_updates_delete': '## </csr2_notify_updates_delete:1312451900288794669>\n- scope: Defaults to "All". Available: CSR2, CSR3, Blog & All (optional)\n',
            'version_check': '## </csr2_version_check:1330241205673529476>\n- app: select CSR2 or CSR3 to filter the search (optional)\n- store: select Google Play Store or Apple App Store to filter the search (optional)\n- version: type out a specific you search for to filter the search\n- country: use 2 letter country codes (ISO 3166-1 alpha-2) to filter the search'
        }

        description_text = descriptions[command]

        embed = discord.Embed(
            title=title_text,
            description=description_text,
            color=discord.Color(0xff00ff)
        )
        embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')
        
        await interaction.followup.send(embed=embed)
        await in_app_logging.send_log(self.bot, log, interaction)

async def setup(bot):
    await bot.add_cog(CommandsCog(bot))
