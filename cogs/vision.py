import discord
from discord.ext import commands
from discord import app_commands, InteractionType
from difflib import get_close_matches
import asyncio
import in_app_logging
import helpers

logger = helpers.load_logging()

class VisionCommandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):

        @app_commands.command(name=self.bot.localisation.get('VISION_CMD_NAME'), description=self.bot.localisation.get('VISION_CMD_DESC'))
        @app_commands.describe(car=self.bot.localisation.get('ANY_CMD_CAR'), rarity=self.bot.localisation.get('ANY_CMD_RARITY'), tier=self.bot.localisation.get('ANY_CMD_TIER'), csr2_version=self.bot.localisation.get('ANY_CMD_CSR2_VERSION'))
        @app_commands.choices(rarity=helpers.load_command_options_rarity(self.bot.localisation))
        @app_commands.choices(tier=helpers.load_command_options_tier(self.bot.localisation))
        async def vision(interaction: discord.Interaction, car: str = None, rarity: str = None, tier: str = None, csr2_version: str = None):
            await interaction.response.defer()
            try:
                header = self.bot.localisation.get('VISION_LOG_HEADER')
                logger.info(f"{header}{self.bot.localisation.get('LOG_CMD_TRIGGERED')} /{self.bot.localisation.get('VISION_CMD_NAME')} car: {car} rarity: {rarity} tier: {tier} csr2_version: {csr2_version}")
                log = f"{header}{self.bot.localisation.get('LOG_CMD_TRIGGERED')} /{self.bot.localisation.get('VISION_CMD_NAME')} car: {car} rarity: {rarity} tier: {tier} csr2_version: {csr2_version}"
                if any([car, rarity, tier, csr2_version]):
                    parameters = []
                    query = """\nSELECT records.UniqueID, records."DB Name", records."Ingame Name Clarification", records.Un, records.★, records."WR-PP", records."WR-EVO", records."WR-NITRO", records."WR-FD", records."WR-TIRE", records."WR-DYNO", records."WR-BEST ET", records."WR Addon", records."SHIFT Links", records."WR-DRIVER", info.IMG, info."Vision Info", info."is EV?", info.thread, s6_effects."S5 - PP", s6_effects."S5 - EVO", s6_effects."S5 - Nos", s6_effects."S5 - FD", s6_effects."S5 - TIRES", s6_effects."S5 - DYNO", s6_effects.Engine, s6_effects.Turbo, s6_effects.Intake, s6_effects.NOS, s6_effects.Body, s6_effects.Tires, s6_effects.Trans\nFROM records\nLEFT JOIN info ON records.UniqueID = info.UniqueID\nLEFT JOIN s6_effects ON records.UniqueID = s6_effects.UniqueID\nWHERE"""
                    if car:
                        if car.startswith('T') and len(car) > 1 and car[1] in "12345":
                            query += """ records.UniqueID COLLATE NOCASE LIKE ?"""
                        elif "_" in car:
                            query += """ records."DB Name" COLLATE NOCASE LIKE ?"""
                        else:
                            query += """ records."Ingame Name Clarification" COLLATE NOCASE LIKE ?"""
                        parameters.append(f"%{car}%")
                    if rarity:
                        if car:
                            query += """ AND"""
                        query += """ records.★ LIKE ?"""
                        parameters.append(rarity)
                    if tier:
                        if any([car, rarity]):
                            query += """ AND"""
                        query += """ records.Un == ?"""
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
                    logger.info(f"{header}{self.bot.localisation.get('LOG_QUERY')} {query}\n{self.bot.localisation.get('LOG_PARAMETERS')} {parameters}")
                    log += f"\n{header}{self.bot.localisation.get('LOG_QUERY')} ```{query}```\n{self.bot.localisation.get('LOG_PARAMETERS')} {parameters}"
                    results = await helpers.execute_sql_statement("WRs", query, parameters)
                    if results:
                        logger.info(f"{header}{len(results)} {self.bot.localisation.get('LOG_RESULTS_FOUND')}")
                        log += f"\n{header}{len(results)} {self.bot.localisation.get('LOG_RESULTS_FOUND')}"
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
                            logger.info(f"{header}{self.bot.localisation.get('LOG_RECOVERY_DONE')} {len(similar_entries)} {self.bot.localisation.get('LOG_RESULTS_FOUND')}")
                            log += f"\n{header}{self.bot.localisation.get('LOG_RECOVERY_DONE')} {len(similar_entries)} {self.bot.localisation.get('LOG_RESULTS_FOUND')}"
                            if len(similar_entries) > 1:
                                view = discord.ui.View(timeout=300)
                                for i, entry in enumerate(similar_entries):
                                    button = discord.ui.Button(label=str(i + 1), style=discord.ButtonStyle.primary)
                                    async def button_callback(interaction: discord.Interaction, e = entry, log = log):
                                        await interaction.response.defer()
                                        try:
                                            selected_unique_id = all_unique_ids[e][0]
                                            results, log = await self.query_by_unique_id(selected_unique_id, log)
                                            if results:
                                                logger.info(f"{header}{self.bot.localisation.get('LOG_QUERY_DONE')}")
                                                log += f"\n{header}{self.bot.localisation.get('LOG_QUERY_DONE')}"
                                                messages, log = await self.create_embeds(results, log)
                                                log = await self.send_channel(interaction, messages, log)
                                            else:
                                                logger.info(f"{header}{self.bot.localisation.get('LOG_ERROR_NO_ENTRY')}")
                                                log += f"\n{header}{self.bot.localisation.get('LOG_ERROR_NO_ENTRY')}"
                                        except discord.errors.NotFound:
                                            await interaction.response.send_message(f"{self.bot.localisation.get('MSG_ERROR_EXPIRED')}", ephemeral=True)
                                    button.callback = button_callback
                                    view.add_item(button)
                                description_list = [
                                    f"{i+1}. {entry} {await helpers.emojify_tier(all_unique_ids[entry][1])} {await helpers.emojify_rarity(all_unique_ids[entry][2])}" 
                                    for i, entry in enumerate(similar_entries)
                                ]
                                embed = discord.Embed(
                                    title=f"{self.bot.localisation.get('MSG_SIMILAR_RESULTS_EMBED_TITLE')}",
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
                            await interaction.followup.send(f"{self.bot.localisation.get('MSG_NOTICE_NO_SIMILAR_RESULTS')}", ephemeral=True)
                            logger.info(f"{header}{self.bot.localisation.get('LOG_RECOVERY_FAIL')}")
                            log += f"\n{header}{self.bot.localisation.get('LOG_RECOVERY_FAIL')}"
                else:
                    await interaction.followup.send(f"{self.bot.localisation.get('MSG_ERROR_NO_VARIABLE')}", ephemeral=True)
                    logger.info(f"{header}{self.bot.localisation.get('LOG_ERROR_NO_VARIABLE')}")
                    log += f"\n{header}{self.bot.localisation.get('LOG_ERROR_NO_VARIABLE')}"
                await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
            except Exception as e:
                await interaction.followup.send(f"{self.bot.localisation.get('MSG_ERROR_FETCH')} {e}")
                logger.info(f"{self.bot.localisation.get('LOG_ERROR_FETCH')} {e}")
                log += f"{self.bot.localisation.get('LOG_ERROR_FETCH')} {e}"
                await in_app_logging.send_log(self.bot, log, 0, 1, interaction)

        self.bot.tree.add_command(vision)

    async def get_similar_entries(self, car: str, rarity: str, tier: str, csr2_version: str, log: str):
        header = self.bot.localisation.get('VISION_LOG_HEADER')
        logger.info(f"{header}{self.bot.localisation.get('LOG_RECOVER')}")
        log += f"\n{header}{self.bot.localisation.get('LOG_RECOVER')}"
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
        logger.info(f"{header}{self.bot.localisation.get('LOG_QUERY')} {similar_entries_query}\n{self.bot.localisation.get('LOG_PARAMETERS')} {parameters}")
        log += f"\n{header}{self.bot.localisation.get('LOG_QUERY')} ```{similar_entries_query}```\n{self.bot.localisation.get('LOG_PARAMETERS')} {parameters}"
        all_entries = await helpers.execute_sql_statement("WRs", similar_entries_query, parameters)
        all_unique_ids = {entry[0]: (entry[1], entry[2], entry[3]) for entry in all_entries}
        cutoff = 0.3 if car else 1.0
        car = car if car else " "
        similar_entries = get_close_matches(car.strip('%'), list(all_unique_ids.keys()), n=10, cutoff=cutoff)
        return similar_entries if similar_entries else None, all_unique_ids, log
    
    async def query_by_unique_id(self, unique_id: str, log: str):
        header = self.bot.localisation.get('VISION_LOG_HEADER')
        query = """\nSELECT records.UniqueID, records."DB Name", records."Ingame Name Clarification", records.Un, records.★, records."WR-PP", records."WR-EVO", records."WR-NITRO", records."WR-FD", records."WR-TIRE", records."WR-DYNO", records."WR-BEST ET", records."WR Addon", records."SHIFT Links", records."WR-DRIVER", info.IMG, info."Vision Info", info."is EV?", info.thread, s6_effects."S5 - PP", s6_effects."S5 - EVO", s6_effects."S5 - Nos", s6_effects."S5 - FD", s6_effects."S5 - TIRES", s6_effects."S5 - DYNO", s6_effects.Engine, s6_effects.Turbo, s6_effects.Intake, s6_effects.NOS, s6_effects.Body, s6_effects.Tires, s6_effects.Trans\nFROM records\nLEFT JOIN info ON records.UniqueID = info.UniqueID\nLEFT JOIN s6_effects ON records.UniqueID = s6_effects.UniqueID\nWHERE UniqueID = ?"""
        logger.info(f"{header}{self.bot.localisation.get('LOG_QUERY')} {query}\n{self.bot.localisation.get('LOG_PARAMETERS')} {(unique_id,)}")
        log += f"\n{header}{self.bot.localisation.get('LOG_QUERY')} ```{query}```\n{self.bot.localisation.get('LOG_PARAMETERS')} {(unique_id,)}"
        results = await helpers.execute_sql_statement("WRs", query, (unique_id,))
        return results, log
    
    async def create_embeds(self, results: list, log: str):
        header = self.bot.localisation.get('VISION_LOG_HEADER')
        logger.info(f"{header}{self.bot.localisation.get('LOG_BUILD_EMBEDS')}")
        log += f"\n{header}{self.bot.localisation.get('LOG_BUILD_EMBEDS')}"
        messages = []
        batch = []
        for row in results:
            result = list(row)
            result[3] = await helpers.emojify_tier(result[3])
            result[4] = await helpers.emojify_rarity(result[4])
            markdown_characters = ['*', '_', '~', '#']
            escaped_text = ''
            if result[14][0] in markdown_characters:
                escaped_text = '\\'
            if result[22] == None:
                result[22] = 0
            if result[17] == 'false':
                spacing = max([len(f"{self.bot.localisation.get('PART_ENGINE')}"), len(f"{self.bot.localisation.get('PART_TURBO')}"), len(f"{self.bot.localisation.get('PART_INTAKE')}"), len(f"{self.bot.localisation.get('PART_NITROUS')}"), len(f"{self.bot.localisation.get('PART_BODY')}"), len(f"{self.bot.localisation.get('PART_TIRES')}"), len(f"{self.bot.localisation.get('PART_TRANSMISSION')}"), len(f"{self.bot.localisation.get('S6_EFFECTS_MSG_EMBED_DESC_PART')}")])
                categories = [f"{self.bot.localisation.get('PART_ENGINE'):<{spacing}}", f"{self.bot.localisation.get('PART_TURBO'):<{spacing}}", f"{self.bot.localisation.get('PART_INTAKE'):<{spacing}}", f"{self.bot.localisation.get('PART_NITROUS'):<{spacing}}", f"{self.bot.localisation.get('PART_BODY'):<{spacing}}", f"{self.bot.localisation.get('PART_TIRES'):<{spacing}}", f"{self.bot.localisation.get('PART_TRANSMISSION'):<{spacing}}"]
                result[17] = f"{self.bot.localisation.get('INFO_MSG_CAR_TYPE_CUMBUSTION')}"
            else:
                spacing = max([len(f"{self.bot.localisation.get('PART_MOTOR')}"), len(f"{self.bot.localisation.get('PART_BATTERY')}"), len(f"{self.bot.localisation.get('PART_INVERTER')}"), len(f"{self.bot.localisation.get('PART_OVERBOOST')}"), len(f"{self.bot.localisation.get('PART_BODY')}"), len(f"{self.bot.localisation.get('PART_TIRES')}"), len(f"{self.bot.localisation.get('PART_TRANSMISSION')}"), len(f"{self.bot.localisation.get('S6_EFFECTS_MSG_EMBED_DESC_PART')}")])
                categories = [f"{self.bot.localisation.get('PART_MOTOR'):<{spacing}}", f"{self.bot.localisation.get('PART_BATTERY'):<{spacing}}", f"{self.bot.localisation.get('PART_INVERTER'):<{spacing}}", f"{self.bot.localisation.get('PART_OVERBOOST'):<{spacing}}", f"{self.bot.localisation.get('PART_BODY'):<{spacing}}", f"{self.bot.localisation.get('PART_TIRES'):<{spacing}}", f"{self.bot.localisation.get('PART_TRANSMISSION'):<{spacing}}"]
                result[17] = f"{self.bot.localisation.get('INFO_MSG_CAR_TYPE_EV')}"
            if not any(x is None for x in result[24:31]) or result[27] == "-":
                values = result[24:31]
                offsets = [round(float(values[i]) - float(result[24]), 3) for i in range(7)]
                combined = sorted(zip(values, categories, offsets))
                sorted_values, sorted_categories, sorted_offsets = zip(*combined)
                chart_lines = [f"{category}   {f"{offset:+.3f}" if await helpers.is_float(offset) else offset}          {f"{value:6.3f}" if await helpers.is_float(value) else value}" for category, offset, value in zip(sorted_categories, sorted_offsets, sorted_values)]
                chart = "\n".join(chart_lines)
                value = f"{self.bot.localisation.get('S6_EFFECTS_MSG_EMBED_DESC_S5PP')} {result[19]}\n{self.bot.localisation.get('S6_EFFECTS_MSG_EMBED_DESC_S5EVO')} {result[20]}\n\n{self.bot.localisation.get('S6_EFFECTS_MSG_EMBED_DESC_S5NOS')} {result[21]}\n{self.bot.localisation.get('S6_EFFECTS_MSG_EMBED_DESC_S5FD')} {f"{float(result[22]):.2f}" if await helpers.is_float(result[22]) else result[22]}\n{self.bot.localisation.get('S6_EFFECTS_MSG_EMBED_DESC_S5TP')} {result[23]}\n{self.bot.localisation.get('S6_EFFECTS_MSG_EMBED_DESC_S5DYYO')} {f"{float(result[24]):.3f}" if await helpers.is_float(result[24]) else result[24]}\n\n**{self.bot.localisation.get('S6_EFFECTS_MSG_EMBED_DESC_TOPS6')}** {sorted_categories[0]} ({f"{float(sorted_offsets[0]):+.3f}" if await helpers.is_float(sorted_offsets[0]) else sorted_offsets[0]}) ({f"{float(sorted_values[0]):.3f}" if await helpers.is_float(sorted_values[0]) else sorted_values[0]})"+f"​\n`"+f"{self.bot.localisation.get('S6_EFFECTS_MSG_EMBED_DESC_PART'):<{spacing+3}}"+f"{self.bot.localisation.get('S6_EFFECTS_MSG_EMBED_DESC_OFFSET'):<16}"[:16]+f"{self.bot.localisation.get('S6_EFFECTS_MSG_EMBED_DESC_TIME'):>6}"+f"\n{chart}`"
            else:
                value = f"{self.bot.localisation.get('S6_EFFECTS_MSG_WARNING_CAR_NOT_FOUND')} [{self.bot.localisation.get('S6_EFFECTS_MSG_CONTRIBUTE')}](https://docs.google.com/spreadsheets/d/1pBamDQTOcWyJoUowrXM05Tj567UVAti1VA8zWsSlrhM/edit)"
            embed = discord.Embed(
                title=result[2],
                description=f"# {result[3]}   {result[4]}",
                color=discord.Color(0xff00ff)
            )
            embed.add_field(name=f"{self.bot.localisation.get('VISION_MSG_EMBED_DESC_CAR_INFO')}", value=f"{result[17]}\n{result[16]}\n\n[{self.bot.localisation.get('INFO_MSG_EMBED_DESC_CAT_INFO_DESC')}](https://discord.com/channels/683998568305917970/1122543660282695780/threads/{result[18]})")
            embed.add_field(name=f"{self.bot.localisation.get('VISION_MSG_EMBED_DESC_WR_TUNE')}", value=f"{self.bot.localisation.get('WR_MSG_EMBED_DESC_PP')} {result[5]}\n{self.bot.localisation.get('WR_MSG_EMBED_DESC_EVO')} {result[6]}\n\n{self.bot.localisation.get('WR_MSG_EMBED_DESC_NOS')} {result[7]}\n{self.bot.localisation.get('WR_MSG_EMBED_DESC_FD')}: {f"{float(result[8]):.2f}" if await helpers.is_float(result[8]) else result[8]}\n{self.bot.localisation.get('WR_MSG_EMBED_DESC_TP')} {result[9]}\n{self.bot.localisation.get('WR_MSG_EMBED_DESC_DYNO')} {f"{float(result[10]):.3f}" if await helpers.is_float(result[10]) else result[10]}\n\n{self.bot.localisation.get('WR_MSG_EMBED_DESC_WR')} {f"{float(result[11]):.3f}" if await helpers.is_float(result[11]) else result[11]}\n{self.bot.localisation.get('WR_MSG_EMBED_DESC_DRIVER')} {escaped_text}{result[14]}\n\n{self.bot.localisation.get('WR_MSG_EMBED_DESC_UPGRADES')} {result[12]}\n[{self.bot.localisation.get('WR_MSG_EMBED_DESC_SHIFT')}]({result[13]})", inline=False)
            embed.add_field(name=f"{self.bot.localisation.get('VISION_MSG_EMBED_DESC_S6_EFFECTS')}", value=value)
            embed.set_footer(text=f"{result[0]} - {result[1]}")
            embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')
            embed.set_image(url=f"https://raw.githubusercontent.com/Nitro4CSR/{result[15]}")
    
            batch.append(embed)
    
            if len(batch) == 10:
                messages.append(batch)
                batch = []
    
        if batch:
            messages.append(batch)
    
        logger.info(f"{header}{self.bot.localisation.get('LOG_EMBEDS_BUILD')}")
        log += f"\n{header}{self.bot.localisation.get('LOG_EMBEDS_BUILD')}"
        return messages, log
    
    async def handle_over_limit(self, interaction: discord.Interaction, results: list, log: str):
        header = self.bot.localisation.get('VISION_LOG_HEADER')
        logger.info(f"{header}{self.bot.localisation.get('LOG_MADE_EXCEPTION')}")
        log += f"\n{header}{self.bot.localisation.get('LOG_MADE_EXCEPTION')}"
        await interaction.followup.send(f"{self.bot.localisation.get('MSG_WARNING_OVER_LIMITS')}" if interaction.guild else f"{self.bot.localisation.get('MSG_WARNING_OVER_LIMIT')}")
        class ForceSendView(discord.ui.View):
            def __init__(self, log, bot, cog, timeout=180):
                super().__init__(timeout=timeout)
                self.log = log
                self.bot = bot
                self.cog = cog
    
            @discord.ui.button(label=self.bot.localisation.get('MSG_BUTTON_NAME_EXCEPTION'), style=discord.ButtonStyle.primary)
            async def exception_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                logger.info(f"{header}{self.bot.localisation.get('LOG_SEND_EXCEPTION')}")
                self.log += f"\n{header}{self.bot.localisation.get('LOG_SEND_EXCEPTION')}"
                await interaction.response.defer(ephemeral=True)
                messages, self.log = await self.cog.create_embeds(results, self.log)
                self.log = await self.cog.send_dms(interaction, messages, self.log)
                await in_app_logging.send_log(self.bot, self.log, 2, 1, interaction)
    
        user_limits = await helpers.load_json_key("user_limits", str(interaction.user.id))
        default_limit = await helpers.load_json_key("config", "DefaultUserLimit")
        post_limit = user_limits.get("PostLimit") if user_limits and "PostLimit" in user_limits else default_limit
        message_text = (
            f"{self.bot.localisation.get('MSG_AMOUNT_SEARCH_RESULTS')} **{len(results)}**\n"
            f"{self.bot.localisation.get('MSG_PERSONAL_LIMIT')} **{post_limit}**\n"
            f"-# {self.bot.localisation.get('MSG_NOTICE_INCREASE_LIMIT_1')} </{self.bot.localisation.get('LIMITRESULTS_CMD_NAME')}:{await helpers.load_json_key('session', 'CSR2_LIMITRESULTS_CMD')}>{self.bot.localisation.get('MSG_NOTICE_INCREASE_LIMIT_2')}"
        )
        await interaction.followup.send(message_text, ephemeral=True, view=ForceSendView(log, self.bot, self))
    
    async def send_channel(self, interaction: discord.Interaction, messages: list, log: str):
        header = self.bot.localisation.get('VISION_LOG_HEADER')
        await interaction.followup.send(f"{self.bot.localisation.get('MSG_NOTICE_FETCH')}")
        for message in messages:
            await interaction.followup.send(embeds=message)
            await asyncio.sleep(0.5)
        logger.info(f"{header}{self.bot.localisation.get('LOG_DONE_CHANNEL')}")
        log += f"\n{header}{self.bot.localisation.get('LOG_DONE_CHANNEL')}"
        return log
    
    async def send_dms(self, interaction: discord.Interaction, messages: list, log: str):
        header = self.bot.localisation.get('VISION_LOG_HEADER')
        if interaction.guild and interaction.type != InteractionType.component:
            await interaction.followup.send(f"{self.bot.localisation.get('MSG_NOTICE_OVER_SERVER_LIMIT')}")
        try:
            await interaction.user.send(f"{self.bot.localisation.get('MSG_NOTICE_FETCH')}") if interaction.guild else await interaction.followup.send(f"{self.bot.localisation.get('MSG_NOTICE_FETCH')}")
        except discord.Forbidden:
            await interaction.followup.send(f"{self.bot.localisation.get('MSG_WARNING_DMS_CLOSED')}", ephemeral=True)
            logger.info(f"{header}{self.bot.localisation.get('LOG_ERROR_CLOSED')}")
            log += f"\n{header}{self.bot.localisation.get('LOG_ERROR_CLOSED')}"
            return log
        for message in messages:
            await interaction.user.send(embeds=message)
            await asyncio.sleep(0.5)
        logger.info(f"{header}{self.bot.localisation.get('LOG_DONE_DM')}")
        log += f"\n{header}{self.bot.localisation.get('LOG_DONE_DM')}"
        if interaction.guild:
            await interaction.followup.send(f"{self.bot.localisation.get('MSG_NOTICE_SENT_DMS')}", ephemeral=True)
        return log

async def setup(bot):
    await bot.add_cog(VisionCommandCog(bot))
