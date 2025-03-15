import aiofiles
import asyncio
import json
import os
import pycountry
import discord
from discord.ext import commands
from discord import app_commands
import in_app_logging
import helpers

logger = helpers.load_logging()

class VersionCheckCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="csr2_version_check", description="Check if a specific game version is available in various ways")
    @app_commands.describe(app="Choose between CSR2 and CSR3", store="Choose between the Google Play Store and the Apple App Store", version="filter for a specific version", country="filter for a specific country by using its 2 letter country code (ISO 3166-1 alpha-2)")
    @app_commands.choices(app=[app_commands.Choice(name="CSR2", value="CSR2"), app_commands.Choice(name="CSR3", value="CSR3")])
    @app_commands.choices(store=[app_commands.Choice(name="Google Play Store", value="Google Play"), app_commands.Choice(name="Apple App Store", value="App Store")])
    async def version_check(self, interaction: discord.Interaction, app: str = None, store: str = None, version: str = None, country: str = None):
        logger.info(f"VERSION_CHECK - The following command has been used: /csr2_version_check app: {app} store: {store} version: {version} country: {country}")
        log = f"VERSION_CHECK - The following command has been used: /csr2_version_check app: {app} store: {store} version: {version} country: {country}"
        await interaction.response.defer()

        CSR2_DATA_FILE = await helpers.load_file_path('CSR2_versions')
        CSR3_DATA_FILE = await helpers.load_file_path('CSR3_versions')
        data_sources = []
        if app == "CSR2" or not app:
            while not os.path.exists(CSR2_DATA_FILE):
                asyncio.sleep(0.2)
            async with aiofiles.open(CSR2_DATA_FILE, mode="r") as f:
                csr2_data = json.loads(await f.read())
                data_sources.append(("CSR2", csr2_data))
        if app == "CSR3" or not app:
            while not os.path.exists(CSR3_DATA_FILE):
                asyncio.sleep(0.2)
            async with aiofiles.open(CSR3_DATA_FILE, mode="r") as f:
                csr3_data = json.loads(await f.read())
                data_sources.append(("CSR3", csr3_data))

        grouped_results = []
        for app_name, data in data_sources:
            stores = [store] if store else data.keys()
            for store_name in stores:
                entries = data.get(store_name, [])
                if version:
                    entries = [entry for entry in entries if entry.get("version") == version]
                if country:
                    entries = [entry for entry in entries if entry.get("country") == country.lower()]

                version_group = {}
                for entry in entries:
                    version_key = entry.get("version")
                    last_updated = entry.get("last_updated", "N/A")
                    country_code = entry.get("country").upper()
                    continent = await helpers.get_continent(country_code)

                    if version_key not in version_group:
                        version_group[version_key] = {"continents": {}, "last_updated": last_updated}

                    if continent not in version_group[version_key]["continents"]:
                        version_group[version_key]["continents"][continent] = []

                    version_group[version_key]["continents"][continent].append(country_code)

                for version_found, details in version_group.items():
                    if version_found is not None:
                        grouped_results.append(
                            {
                                "app": app_name,
                                "store": store_name,
                                "version": version_found,
                                "last_updated": details["last_updated"],
                                "continents": details["continents"],
                            }
                        )

        logger.info(f"VERSION_CHECK - Query found {len(grouped_results)} results.")
        log += f"\nVERSION_CHECK - Query found {len(grouped_results)} results."

        batch = []
        embeds = []

        logger.info("VERSION_CHECK - Constructing Results")
        log += "\nVERSION_CHECK - Constructing Results"
        if grouped_results:
            for result in grouped_results:
                game_icon = (
                    "https://imgur.com/1VWi2Di.png" if result["app"] == "CSR2" else "https://imgur.com/szUv2T5.png"
                )
                result['store'] = await helpers.emojify_store(result['store'])

                continent_info = ""
                for continent, countries in result["continents"].items():
                    countries = [f"{pycountry.countries.get(alpha_2=country).name} ({country.lower()})" for country in countries]
                    continent_info += f"**{continent}:**\n {', '.join(sorted(countries))}\n\n"
                len(continent_info)


                embed = discord.Embed(
                    title=f"Query Result",
                    description=(
                        f"## Store: {result['store']}\nVersion: {result['version']}\nLast Updated: <t:{result['last_updated']}:F>\n\n{continent_info}"
                    ),
                    color=discord.Color(0xFF00FF),
                )
                embed.set_thumbnail(url=game_icon)
                embeds.append(embed)
                if len(embeds) == 2:
                    batch.append(embeds)
                    embeds = []
        else:
            embed = discord.Embed(
                title=f"No results found matching the given filters.",
                description="",
                color=discord.Color(0xFF00FF),
            )
            embeds.append(embed)

        if embeds:
            batch.append(embeds)

        for i, embeds in enumerate(batch):
            await interaction.followup.send(embeds=batch, silent=True if i != 0 else None)

        logger.info("VERSION_CHECK - Results sent in Channel.")
        log += "\nVERSION_CHECK - Results sent in Channel."
        await in_app_logging.send_log(self.bot, log, 2, 1, interaction)

async def setup(bot):
    await bot.add_cog(VersionCheckCog(bot))
