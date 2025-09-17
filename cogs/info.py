import discord
from discord.ext import commands
from discord import app_commands, InteractionType
from difflib import get_close_matches
import asyncio
import in_app_logging
import helpers

logger = helpers.load_logging()
localisation = dict(helpers.load_localisation())

class InfoCommandCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name=localisation.get('INFO_CMD_NAME'), description=localisation.get('INFO_CMD_DESC'))
    @app_commands.describe(car=localisation.get('ANY_CMD_CAR'), rarity=localisation.get('ANY_CMD_RARITY'), tier=localisation.get('ANY_CMD_TIER'), csr2_version=localisation.get('ANY_CMD_CSR2_VERSION'))
    @app_commands.choices(rarity=helpers.load_command_options_rarity(localisation))
    @app_commands.choices(tier=helpers.load_command_options_tier(localisation))
    async def info(self, interaction: discord.Interaction, car: str = None, rarity: str = None, tier: str = None, csr2_version: str = None):
        await interaction.response.defer()
        try:
            header = localisation.get('INFO_LOG_HEADER')
            logger.info(f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('INFO_CMD_NAME')} car: {car} rarity: {rarity} tier: {tier} csr2_version: {csr2_version}")
            log = f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('INFO_CMD_NAME')} car: {car} rarity: {rarity} tier: {tier} csr2_version: {csr2_version}"
            if any([car, rarity, tier, csr2_version]):
                parameters = []
                query = """\nSELECT "UniqueID", "DB Name", "Ingame Name", Un, ★, IMG, "Vision Info", "is EV?", "thread"\nFROM info\nWHERE"""
                if car:
                    if car.startswith('T') and len(car) > 1 and car[1] in "12345":
                        query += """ UniqueID COLLATE NOCASE LIKE ?"""
                    elif "_" in car:
                        query += """ "DB Name" COLLATE NOCASE LIKE ?"""
                    else:
                        query += """ "Ingame Name" COLLATE NOCASE LIKE ?"""
                    parameters.append(f"%{car}%")
                if rarity:
                    if car:
                        query += """ AND"""
                    query += """ ★ LIKE ?"""
                    parameters.append(rarity)
                if tier:
                    if any([car, rarity]):
                        query += """ AND"""
                    query += """ Un == ?"""
                    parameters.append(tier)
                if csr2_version:
                    if "OTA" in csr2_version:
                        game_version, ota_version = csr2_version.split(maxsplit=1)
                        if "OTA" in game_version:
                            csr2_version = f"{ota_version} {game_version}"
                            game_version, ota_version = csr2_version.split(maxsplit=1)
                        csr2_version = f"""Added into the game in {ota_version}% Update {game_version}%"""
                    else:
                        csr2_version = f"""Added into the game in %Update {csr2_version}%"""
                    if any([car, rarity, tier]):
                        query += """ AND"""
                    query += """ info."Vision Info" LIKE ?"""
                    parameters.append(f"{csr2_version}")
                logger.info(f"{header}{localisation.get('LOG_QUERY')} {query}\n{localisation.get('LOG_PARAMETERS')} {parameters}")
                log += f"\n{header}{localisation.get('LOG_QUERY')} ```{query}```\n{localisation.get('LOG_PARAMETERS')} {parameters}"
                results = await helpers.execute_sql_statement("WRs", query, parameters)
                if results:
                    logger.info(f"{header}{len(results)} {localisation.get('LOG_RESULTS_FOUND')}")
                    log += f"\n{header}{len(results)} {localisation.get('LOG_RESULTS_FOUND')}"
                    route = await helpers.get_send_route(len(results), interaction.user.id, interaction.guild.id if interaction.guild else None)
                    if route == 2:
                        await self.handle_over_limit(interaction, results, log)
                        return
                    else:
                        messages, log = await self.create_embeds(results, log)
                        log = await self.send_channel(interaction, messages, log) if route == 0 else await self.send_dms(interaction, messages, log)
                else:
                    similar_entries, all_unique_ids, log = await self.get_similar_entries(car, rarity, tier, csr2_version, log)
                    if similar_entries:
                        logger.info(f"{header}{localisation.get('LOG_RECOVERY_DONE')} {len(similar_entries)} {localisation.get('LOG_RESULTS_FOUND')}")
                        log += f"\n{header}{localisation.get('LOG_RECOVERY_DONE')} {len(similar_entries)} {localisation.get('LOG_RESULTS_FOUND')}"
                        if len(similar_entries) > 1:
                            view = discord.ui.View(timeout=300)
                            for i, entry in enumerate(similar_entries):
                                button = discord.ui.Button(label=str(i + 1), style=discord.ButtonStyle.primary)
                                async def button_callback(interaction: discord.Interaction, e = entry, log = log):
                                    await interaction.response.defer()
                                    try:
                                        selected_unique_id = all_unique_ids[e][0]
                                        logger.info(f"{header}{localisation.get('LOG_QUERY_UNID')}")
                                        log += f"{header}{localisation.get('LOG_QUERY_UNID')}"
                                        results, log = await self.query_by_unique_id(selected_unique_id, log)
                                        if results:
                                            logger.info(f"{header}{localisation.get('LOG_QUERY_DONE')}")
                                            log += f"\n{header}{localisation.get('LOG_QUERY_DONE')}"
                                            messages, log = await self.create_embeds(results, log)
                                            log = await self.send_channel(interaction, messages, log)
                                        else:
                                            logger.info(f"{header}{localisation.get('LOG_ERROR_NO_ENTRY')}")
                                            log += f"\n{header}{localisation.get('LOG_ERROR_NO_ENTRY')}"
                                    except discord.errors.NotFound:
                                        await interaction.response.send_message(f"{localisation.get('MSG_ERROR_EXPIRED')}", ephemeral=True)
                                button.callback = button_callback
                                view.add_item(button)
                            description_list = [
                                f"{i+1}. {entry} {await helpers.emojify_tier(all_unique_ids[entry][1])} {await helpers.emojify_rarity(all_unique_ids[entry][2])}"
                                for i, entry in enumerate(similar_entries)
                            ]
                            embed = discord.Embed(
                                title=f"{localisation.get('MSG_SIMILAR_RESULTS_EMBED_TITLE')}",
                                description="\n".join(description_list),
                                color=discord.Color(0xff00ff)
                            )
                            embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')
                            await interaction.followup.send(embed=embed, view=view)
                        else:
                            route = await helpers.get_send_route(len(results), interaction.user.id, interaction.guild.id if interaction.guild else None)
                            if route == 2:
                                log = await self.handle_over_limit(interaction, results, log)
                            else:
                                messages, log = await self.create_embeds(results, log)
                                log = await self.send_channel(interaction, messages, log) if route == 0 else await self.send_dms(interaction, messages, log)
                    else:
                        await interaction.followup.send(f"{localisation.get('MSG_NOTICE_NO_SIMILAR_RESULTS')}", ephemeral=True)
                        logger.info(f"{header}{localisation.get('LOG_RECOVERY_FAIL')}")
                        log += f"\n{header}{localisation.get('LOG_RECOVERY_FAIL')}"
            else:
                await interaction.followup.send(f"{localisation.get('MSG_ERROR_NO_VARIABLE')}", ephemeral=True)
                logger.info(f"{header}{localisation.get('LOG_ERROR_NO_VARIABLE')}")
                log += f"\n{header}{localisation.get('LOG_ERROR_NO_VARIABLE')}"
            await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
        except Exception as e:
            await interaction.followup.send(f"{localisation.get('MSG_ERROR_FETCH')} {e}")
            logger.info(f"{localisation.get('LOG_ERROR_FETCH')} {e}")
            log += f"{localisation.get('LOG_ERROR_FETCH')} {e}"
            await in_app_logging.send_log(self.bot, log, 0, 1, interaction)

    async def get_similar_entries(self, car: str, rarity: str, tier: str, csr2_version: str, log: str):
        header = localisation.get('LOG_HEADER')
        logger.info(f"{header}{localisation.get('LOG_RECOVER')}")
        log += f"\n{header}{localisation.get('LOG_RECOVER')}"
        parameters = []
        similar_entries_query = ("""\nSELECT "Ingame Name", UniqueID, Un, ★\nFROM info""")
        if any([rarity, tier, csr2_version]):
            similar_entries_query += """\nWHERE"""
        if rarity:
            similar_entries_query += """ ★ LIKE ?"""
            parameters.append(rarity)
        if tier:
            if rarity:
                similar_entries_query += " AND"
                similar_entries_query += """ Un == ?"""
                parameters.append(tier)
        if csr2_version:
            if rarity or tier:
                similar_entries_query += " AND"
            similar_entries_query += """ "Vision Info" LIKE ?"""
            parameters.append(f"{csr2_version}")
        logger.info(f"{header}{localisation.get('LOG_QUERY')} {similar_entries_query}\n{localisation.get('LOG_PARAMETERS')} {parameters}")
        log += f"\n{header}{localisation.get('LOG_QUERY')} ```{similar_entries_query}```\n{localisation.get('LOG_PARAMETERS')} {parameters}"
        all_entries = await helpers.execute_sql_statement("WRs", similar_entries_query, parameters)
        all_unique_ids = {entry[0]: (entry[1], entry[2], entry[3]) for entry in all_entries}
        cutoff = 0.3 if car else 1.0
        car = car if car else " "
        similar_entries = get_close_matches(car.strip('%'), list(all_unique_ids.keys()), n=10, cutoff=cutoff)
        return similar_entries if similar_entries else None, all_unique_ids, log

    async def query_by_unique_id(self, unique_id: str, log: str):
        header = localisation.get('LOG_HEADER')
        query = """\nSELECT UniqueID, "DB Name", "Ingame Name", Un, ★, IMG, "Vision Info", "is EV?", thread\nFROM info\nWHERE UniqueID = ?"""
        logger.info(f"{header}{localisation.get('LOG_QUERY')} {query}\n{localisation.get('LOG_PARAMETERS')} {(unique_id,)}")
        log += f"\n{header}{localisation.get('LOG_QUERY')} ```{query}```\n{localisation.get('LOG_PARAMETERS')} {(unique_id,)}"
        results = await helpers.execute_sql_statement("WRs", query, (unique_id,))
        return results, log

    async def create_embeds(self, results: list, log: str):
        header = localisation.get('LOG_HEADER')
        logger.info(f"{header}{localisation.get('LOG_BUILD_EMBEDS')}")
        log += f"\n{header}{localisation.get('LOG_BUILD_EMBEDS')}"
        messages = []
        batch = []
        for row in results:
            result = list(row)
            result[3] = await helpers.emojify_tier(result[3])
            result[4] = await helpers.emojify_rarity(result[4])
            if result[7] == "false":
                result[7] = f"{localisation.get('INFO_MSG_CAR_TYPE_COMBUSTION')}"
            else:
                result[7] = f"{localisation.get('INFO_MSG_CAR_TYPE_EV')}"

            embed = discord.Embed(
                title=result[2],
                description=f"# {result[3]}   {result[4]}",
                color=discord.Color(0xff00ff)
            )
            embed.add_field(name=f"{localisation.get('INFO_MSG_EMBED_DESC_CAT_INFO_TITLE')}", value=f"**{result[7]}**\n{result[6]}\n\n**[{localisation.get('INFO_MSG_EMBED_DESC_CAT_INFO_DESC')}](https://discord.com/channels/683998568305917970/{result[8]})**", inline=False)
            embed.set_footer(text=f"{result[0]} - {result[1]}")
            embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')
            embed.set_image(url=f"https://raw.githubusercontent.com/Nitro4CSR/{result[5]}")

            batch.append(embed)

            if len(batch) == 10:
                messages.append(batch)
                batch = []

        if batch:
            messages.append(batch)

        logger.info(f"{header}{localisation.get('LOG_EMBEDS_BUILD')}")
        log += f"\n{header}{localisation.get('LOG_EMBEDS_BUILD')}"
        return messages, log

    async def handle_over_limit(self, interaction: discord.Interaction, results: list, log: str):
        header = localisation.get('LOG_HEADER')
        logger.info(f"{header}{localisation.get('LOG_MADE_EXCEPTION')}")
        log += f"\n{header}{localisation.get('LOG_MADE_EXCEPTION')}"
        await interaction.followup.send(f"{localisation.get('MSG_WARNING_OVER_LIMITS')}" if interaction.guild else f"{localisation.get('MSG_WARNING_OVER_LIMIT')}")
        class ForceSendView(discord.ui.View):
            def __init__(self, log, bot, cog, timeout=180):
                super().__init__(timeout=timeout)
                self.log = log
                self.bot = bot
                self.cog = cog

            @discord.ui.button(label=localisation.get('MSG_BUTTON_NAME_EXCEPTION'), style=discord.ButtonStyle.primary)
            async def exception_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                logger.info(f"{header}{localisation.get('LOG_SEND_EXCEPTION')}")
                self.log += f"\n{header}{localisation.get('LOG_SEND_EXCEPTION')}"
                await interaction.response.defer(ephemeral=True)
                messages, self.log = await self.cog.create_embeds(results, self.log)
                self.log = await self.cog.send_dms(interaction, messages, self.log)
                await in_app_logging.send_log(self.bot, self.log, 2, 1, interaction)

        user_limits = await helpers.load_json_key("user_limits", str(interaction.user.id))
        default_limit = await helpers.load_json_key("config", "DefaultUserLimit")
        post_limit = user_limits.get("PostLimit") if user_limits and "PostLimit" in user_limits else default_limit
        message_text = (
            f"{localisation.get('MSG_AMOUNT_SEARCH_RESULTS')} **{len(results)}**\n"
            f"{localisation.get('MSG_PERSONAL_LIMIT')} **{post_limit}**\n"
            f"-# {localisation.get('MSG_NOTICE_INCREASE_LIMIT_1')} </{localisation.get('LIMITRESULTS_CMD_NAME')}:{await helpers.load_json_key('session', 'CSR2_LIMITRESULTS_CMD')}>{localisation.get('MSG_NOTICE_INCREASE_LIMIT_2')}"
        )
        await interaction.followup.send(message_text, ephemeral=True, view=ForceSendView(log, self.bot, self))

    async def send_channel(self, interaction: discord.Interaction, messages: list, log: str):
        header = localisation.get('LOG_HEADER')
        await interaction.followup.send(f"{localisation.get('MSG_NOTICE_FETCH')}")
        for message in messages:
            await interaction.followup.send(embeds=message)
            await asyncio.sleep(0.5)
        logger.info(f"{header}{localisation.get('LOG_DONE_CHANNEL')}")
        log += f"\n{header}{localisation.get('LOG_DONE_CHANNEL')}"
        return log

    async def send_dms(self, interaction: discord.Interaction, messages: list, log: str):
        header = localisation.get('LOG_HEADER')
        if interaction.guild and interaction.type != InteractionType.component:
            await interaction.followup.send(f"{localisation.get('MSG_NOTICE_OVER_SERVER_LIMIT')}")
        try:
            await interaction.user.send(f"{localisation.get('MSG_NOTICE_FETCH')}") if interaction.guild else await interaction.followup.send(f"{localisation.get('MSG_NOTICE_FETCH')}")
        except discord.Forbidden:
            await interaction.followup.send(f"{localisation.get('MSG_WARNING_DMS_CLOSED')}", ephemeral=True)
            logger.info(f"{header}{localisation.get('LOG_ERROR_CLOSED')}")
            log += f"\n{header}{localisation.get('LOG_ERROR_CLOSED')}"
            return log
        for message in messages:
            await interaction.user.send(embeds=message)
            await asyncio.sleep(0.5)
        logger.info(f"{header}{localisation.get('LOG_DONE_DM')}")
        log += f"\n{header}{localisation.get('LOG_DONE_DM')}"
        if interaction.guild:
            await interaction.followup.send(f"{localisation.get('MSG_NOTICE_SENT_DMS')}", ephemeral=True)
        return log

async def setup(bot):
    await bot.add_cog(InfoCommandCog(bot))
