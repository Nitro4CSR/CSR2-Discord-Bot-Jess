import pycountry
import discord
from discord.ext import commands
from discord import app_commands
import in_app_logging
import helpers

logger = helpers.load_logging()
localisation = dict(helpers.load_localisation())

class VersionCheckCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name=localisation.get('VERSION_CHECK_CMD_NAME'), description=localisation.get('VERSION_CHECK_CMD_DESC'))
    @app_commands.describe(app=localisation.get('VERSION_CHECK_CMD_APP'), store=localisation.get('VERSION_CHECK_CMD_STORE'), version=localisation.get('VERSION_CHECK_CMD_VERSION'), country=localisation.get('VERSION_CHECK_CMD_COUNTRY'))
    @app_commands.choices(app=[app_commands.Choice(name=localisation.get('VERSION_CHECK_CMD_APP_OPTION_CSR2'), value="CSR2"), app_commands.Choice(name=localisation.get('VERSION_CHECK_CMD_APP_OPTION_CSR3'), value="CSR3")])
    @app_commands.choices(store=[app_commands.Choice(name=localisation.get('VERSION_CHECK_CMD_STORE_OPTION_GP'), value="Google Play"), app_commands.Choice(name=localisation.get('VERSION_CHECK_CMD_STORE_OPTION_AS'), value="App Store")])
    async def versioncheck(self, interaction: discord.Interaction, app: str = None, store: str = None, version: str = None, country: str = None):
        await interaction.response.defer()
        try:
            header = localisation.get('VERSION_CHECK_LOG_HEADER')
            logger.info(f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('VERSIONCHECK_CMD_NAME')} app: {app} store: {store} version: {version} country: {country}")
            log = f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('VERSIONCHECK_CMD_NAME')} app: {app} store: {store} version: {version} country: {country}"
            data_sources = []
            csr2_data = await helpers.load_file('CSR2_versions')
            csr3_data = await helpers.load_file('CSR3_versions')
            if app is None or app == "CSR2":
                data_sources.append(("CSR2", csr2_data))
            if app is None or app == "CSR3":
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
            logger.info(f"{header}{len(grouped_results)} {localisation.get('LOG_RESULTS_FOUND')}")
            log += f"\n{header}{len(grouped_results)} {localisation.get('LOG_RESULTS_FOUND')}."
            batch = []
            embeds = []
            logger.info(f"{header}{localisation.get('LOG_BUILD_EMBEDS')}")
            log += f"\n{header}{localisation.get('LOG_BUILD_EMBEDS')}"
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
                        title=f"{localisation.get('VERSION_CHECK_MSG_EMBED_TITLE')}",
                        description=(
                            f"## {localisation.get('VERSION_CHECK_MSG_EMBED_DESC_STORE')} {result['store']}\n{localisation.get('VERSION_CHECK_MSG_EMBED_DESC_VERSION')} {result['version']}\n{localisation.get('VERSION_CHECK_MSG_EMBED_DESC_LAST_UPDATED')} <t:{result['last_updated']}:F>\n\n{continent_info}"
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
                    title=f"{localisation.get('VERSION_CHECK_MSG_EMBED_TITLE_NO_RESULTS')}",
                    description="",
                    color=discord.Color(0xFF00FF),
                )
                embeds.append(embed)
            if embeds:
                batch.append(embeds)
            for i, embeds in enumerate(batch):
                await interaction.followup.send(embeds=embeds, silent=True if i != 0 else None)
            logger.info(f"{header}{localisation.get('LOG_DONE_CHANNEL')}")
            log += f"\n{header}{localisation.get('LOG_DONE_CHANNEL')}"
            await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
        except Exception as e:
            await interaction.followup.send(f"{localisation.get('MSG_ERROR_FETCH')} {e}")
            logger.info(f"{localisation.get('LOG_ERROR_FETCH')} {e}")
            log += f"{localisation.get('LOG_ERROR_FETCH')} {e}"
            await in_app_logging.send_log(self.bot, log, 0, 1, interaction)

async def setup(bot):
    await bot.add_cog(VersionCheckCog(bot))
