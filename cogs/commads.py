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
    async def commands(self, interaction: discord.Interaction):
        # Log the command usage and parameters
        logger.info(f"The following command has been used: /csr2_commands")
        log = f"The following command has been used: /csr2_commands"

        await interaction.response.defer()

        embed = discord.Embed(
            title="Available Commands",
            description=(
                f"## </csr2_wr:1265025856539983889>\nAvailable search operators:\n- car: Accepts Ingame names, code names and Unique IDs. The later 2 can be found at the bottom of a searched car. (optional)\n- rarity: Accepts star counts and/or star color. Star count goes before star color seperated by a space. (optional)\n- tier: Accepts value as just number and also `T1/2/3/4/5` (optional)\n- csr2_version: Accepts both OTA versions and game release versions seperate or combined split by a space (optional)\n"
                f"## </csr2_wrlist:1265025856539983890>\nAvailable search operators:\n- car: Accepts Ingame names, code names and Unique IDs. The later 2 can be found at the bottom of a searched car. (optional)\n- rarity: Defaults to T5. Accepts star counts and/or star color. Star count goes before star color seperated by a space. (optional)\n- tier: Accepts value as just number and also `T1/2/3/4/5` (optional)\n- csr2_version: Accepts both OTA versions and game release versions seperate or combined split by a space (optional)\n"
                f"## </csr2_s6_effects:1265323078884266098>\nAvailable search operators:\n- car: Accepts Ingame names, code names and Unique IDs. The later 2 can be found at the bottom of a searched car. (optional)\n- rarity: Defaults to T5. Accepts star counts and/or star color. Star count goes before star color seperated by a space. (optional)\n- tier: Accepts value as just number and also `T1/2/3/4/5` (optional)\n- csr2_version: Accepts both OTA versions and game release versions seperate or combined split by a space (optional)\n"
                f"## </csr2_info:1266821832519192696>\nAvailable search operators:\n- car: Accepts Ingame names, code names and Unique IDs. The later 2 can be found at the bottom of a searched car. (optional)\n- rarity: Defaults to T5. Accepts star counts and/or star color. Star count goes before star color seperated by a space. (optional)\n- tier: Accepts value as just number and also `T1/2/3/4/5` (optional)\n- csr2_version: Accepts both OTA versions and game release versions seperate or combined split by a space (optional)\n"
                f"## </csr2_getlimit:1271416779469750389>\n- Displays the maximum allowed results that will be posted in the servers channels directly\n"
                f"## </csr2_share_tune:1277195388532559925>\nStarts a submission loop in your DMs so you can share your custom tunes for various purposes.\n"
                f"## </csr2_update_tune:1277195388532559926>\n- tune_id: An unique identifier integer provided to you when you created your tune and needed to point at the tune you want to edit\n- pp: the pp rating of your cars tune\n- evo: the evo rating of your cars tune\n- engine_motor: the equipped upgrade stage in the category Engine/Motor\n- turbo_battery: the equipped upgrade stage in the category Turbo/Battery\n- intake_inverter: the equipped upgrade stage in the category Intake/Inverter\n- nitrous_overboost: the equipped upgrade stage in the category Nitrous/Overboost\n- body: the equipped upgrade stage in the category Body\n- tires: the equipped upgrade stage in the category Tires\n- transmission: the equipped upgrade stage in the category Transmission\n- nitrous: your nitrous tuning setup\n- final_drive: your final drive tuning setup\n- tire_pressure: your tire pressure tuning setup\n- dyno: your tuning setups dyno time\n- purpose: the use case of your tune\n- usage: how to shift your setup"
                f"## </csr2_delete_tune:1277195388532559927>\n- tune_id: An unique identifier integer provided to you when you created your tune and needed to point at the tune you want to edit"
                f"## </csr2_community_tune:1277195388532559928>\n- car: Name or DB name of the car you want to search a community tune for\n- tune_id: An unique identifier integer provided to you when you created your tune and needed to point at the tune you want to edit\n- tier: Tier of the car you want to search a community tune for\n- rarity: star count and color of the car you want to search a community tune for\n- purpose: the use case you want to search a tune for\n- creator: the creator of the tune you want to search for"
            ),
            color=discord.Color(0xff00ff)
        )
        embed.add_field(name="", value=f"## </csr2_customsql:1266755136114659370>\n- database: defines which database you want to access\n- select: optional variable to define a SELECT prompt of an SQL statement\n- update: optional variable to define a UPDATE prompt of an SQL statement\n- create_table: optional variable to define a CREATE TABLE prompt of an SQL statement (requires Bot admin perms)\n- insert_into: optional variable to define a INSERT INTO prompt of an SQL statement (requires Bot admin perms)\n- from_: optional variable to define a FROM prompt of an SQL statement\n- set_: optional variable to define a SET prompt of an SQL statement (requires Bot admin perms)\n- where: optional variable to define a WHERE prompt of an SQL statement\n## </csr2_dbstructure:1278376907364241501>/n- displays a schematic to show the user the internal database structure")
        embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')
        
        await interaction.followup.send(embed=embed)
        await in_app_logging.send_log(self.bot, log, interaction)

async def setup(bot):
    await bot.add_cog(CommandsCog(bot))
