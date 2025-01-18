import aiofiles
import discord
import json
from discord.ext import commands
from discord import app_commands
import logging
import in_app_logging
import helpers

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CSR2_DATA_FILE = helpers.load_CSR2versions_json()
CSR3_DATA_FILE = helpers.load_CSR3versions_json()

class VersionCheckCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="csr2_version_check", description="Check if a specific game version is available in various ways")
    @app_commands.describe(app="Choose between CSR2 and CSR3", store="Choose between the Google Play Store and the Apple App Store", version="filter for a specific version", country="filter for a specific country by using its 2 letter country code (ISO 3166-1 alpha-2)")
    @app_commands.choices(app=[app_commands.Choice(name="CSR2", value="CSR2"), app_commands.Choice(name="CSR3", value="CSR3")])
    @app_commands.choices(store=[app_commands.Choice(name="Google Play Store", value="Google Play"), app_commands.Choice(name="Apple App Store", value="App Store")])
    async def version_check(self, interaction: discord.Interaction, app: str = None, store: str = None, version: str = None, country: str = None):
        logger.info(f"The following command has been used: /csr2_version_check app: {app} store: {store} version: {version} country: {country}")
        log = f"The following command has been used: /csr2_version_check app: {app} store: {store} version: {version} country: {country}"

        await interaction.response.defer()

        # Load data for both CSR2 and CSR3 if no app is specified
        data_sources = []
        if app == "CSR2" or not app:
            async with aiofiles.open(CSR2_DATA_FILE, mode="r") as f:
                csr2_data = json.loads(await f.read())
                data_sources.append(("CSR2", csr2_data))
        if app == "CSR3" or not app:
            async with aiofiles.open(CSR3_DATA_FILE, mode="r") as f:
                csr3_data = json.loads(await f.read())
                data_sources.append(("CSR3", csr3_data))

        # Aggregate results by grouping countries
        grouped_results = []
        for app_name, data in data_sources:
            stores = [store] if store else data.keys()  # Check specific store or all stores
            for store_name in stores:
                entries = data.get(store_name, [])
                if version:
                    entries = [entry for entry in entries if entry.get("version") == version]
                if country:
                    entries = [entry for entry in entries if entry.get("country") == country.lower()]

                # Group by version and collect countries, including last updated
                version_group = {}
                for entry in entries:
                    version_key = entry.get("version")
                    last_updated = entry.get("last_updated", "N/A")
                    if version_key not in version_group:
                        version_group[version_key] = {"countries": [], "last_updated": last_updated}
                    version_group[version_key]["countries"].append(entry.get("country").upper())

                for version_found, details in version_group.items():
                    grouped_results.append(
                        {
                            "app": app_name,
                            "store": store_name,
                            "version": version_found,
                            "last_updated": details["last_updated"],
                            "countries": sorted(details["countries"]),  # Sort countries alphabetically
                        }
                    )

        logger.info(f"Query found {len(grouped_results)} results.")
        log += f"\nQuery found {len(grouped_results)} results."

        # Prepare the response
        batch = []
        embeds = []

        logger.info("Constructing Results")
        log += "\nConstructing Results"
        if grouped_results:
            for result in grouped_results:
                game_icon = (
                    "https://i.imgur.com/1VWi2Di.png" if result["app"] == "CSR2" else "https://imgur.com/szUv2T5.png"
                )

                embed = discord.Embed(
                    title=f"Query Result",
                    description=(
                        f"Store: {result['store']}      App: {result['app']}\n"
                        f"Version: {result['version']}\n"
                        f"Last Updated: <t:{result['last_updated']}:F>\n"
                        f"Countries: {', '.join(result['countries'])}"
                    ),
                    color=discord.Color(0xFF00FF),
                )
                embed.set_thumbnail(url=game_icon)

                embeds.append(embed)
                if len(embeds) == 10:
                    batch.append(embeds)
                    embeds = []
        else:
            embed = discord.Embed(
                title=f"No results found matching the given filters.",
                description="",
                color=discord.Color(0xFF00FF),
            )

            embeds.append(embed)

        # Send response
        batch.append(embeds)

        for embeds in batch:
            await interaction.followup.send(embeds=embeds)

        logger.info("Results sent in Channel.")
        log += "\nResults sent in Channel."
        await in_app_logging.send_log(self.bot, log, interaction)


async def setup(bot):
    await bot.add_cog(VersionCheckCog(bot))
