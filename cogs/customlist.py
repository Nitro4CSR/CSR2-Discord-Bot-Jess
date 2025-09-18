import discord
from discord.ext import commands
from discord import app_commands
import in_app_logging
import helpers

logger = helpers.load_logging()
localisation = dict(helpers.load_localisation())

querry = {
    'wr': """\nSELECT UniqueID, "DB Name", "Ingame Name Clarification", Un, ★, "WR-PP", "WR-EVO", "WR-NITRO", "WR-FD", "WR-TIRE", "WR-DYNO", "WR-BEST ET", "WR Addon", "SHIFT Links", "WR-DRIVER"\nFROM records\nWHERE "DB Name" COLLATE NOCASE LIKE ?""",
    'wrlist': """\nSELECT "Ingame Name Clarification", "WR-BEST ET", "★", UniqueID\nFROM records\nWHERE "DB Name" COLLATE NOCASE LIKE ?""",
    's6effects': """\nSELECT UniqueID, "DB Name", "Ingame Name", Un, ★, "S5 - PP", "S5 - EVO", "S5 - NOS", "S5 - FD", "S5 - TIRES", "S5 - DYNO", Engine, Turbo, Intake, NOS, Body, Tires, Trans, "is EV?"\nFROM s6_effects\nWHERE "DB Name" COLLATE NOCASE LIKE ?""",
    'info': """\nSELECT "UniqueID", "DB Name", "Ingame Name", Un, ★, IMG, "Vision Info", "is EV?", "thread"\nFROM info\nWHERE "DB Name" COLLATE NOCASE LIKE ?""",
    'vision': """\nSELECT records.UniqueID, records."DB Name", records."Ingame Name Clarification", records.Un, records.★, records."WR-PP", records."WR-EVO", records."WR-NITRO", records."WR-FD", records."WR-TIRE", records."WR-DYNO", records."WR-BEST ET", records."WR Addon", records."SHIFT Links", records."WR-DRIVER", info.IMG, info."Vision Info", info."is EV?", info.thread, s6_effects."S5 - PP", s6_effects."S5 - EVO", s6_effects."S5 - Nos", s6_effects."S5 - FD", s6_effects."S5 - TIRES", s6_effects."S5 - DYNO", s6_effects.Engine, s6_effects.Turbo, s6_effects.Intake, s6_effects.NOS, s6_effects.Body, s6_effects.Tires, s6_effects.Trans\nFROM records\nLEFT JOIN info ON records.UniqueID = info.UniqueID\nLEFT JOIN s6_effects ON records.UniqueID = s6_effects.UniqueID\nWHERE records."DB Name" COLLATE NOCASE LIKE ?"""
}

class CustomListCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name=localisation.get('CUSTOMLIST_CMD_NAME'), description=localisation.get('CUSTOMLIST_CMD_DESC'))
    @app_commands.describe(data=localisation.get('CUSTOMLIST_CMD_DATA'), list_id=localisation.get('CUSTOMLIST_ANY_CMD_LIST_ID'), global_list=localisation.get('CUSTOMLIST_ANY_CMD_GLOBAL_LIST'), list_group=localisation.get('CUSTOMLIST_CMD_LIST_GROUP'))
    @app_commands.choices(data=[app_commands.Choice(name=localisation.get('CUSTOMLIST_CMD_DATA_OPTION_WR'), value="wr"), app_commands.Choice(name=localisation.get('CUSTOMLIST_CMD_DATA_OPTION_WRLIST'), value="wrlist"), app_commands.Choice(name=localisation.get('CUSTOMLIST_CMD_DATA_OPTION_S6EFFECTS'), value="s6effects"), app_commands.Choice(name=localisation.get('CUSTOMLIST_CMD_DATA_OPTION_INFO'), value="info"), app_commands.Choice(name=localisation.get('CUSTOMLIST_CMD_DATA_OPTION_VISION'), value="vision")])
    @app_commands.choices(global_list=[app_commands.Choice(name=localisation.get('CUSTOMLIST_ANY_CMD_GLOBAL_LIST_OPTION_TRUE'), value=1), app_commands.Choice(name=localisation.get('CUSTOMLIST_ANY_CMD_GLOBAL_LIST_OPTION_FALSE'), value=0), app_commands.Choice(name=localisation.get('CUSTOMLIST_ANY_CMD_GLOBAL_LIST_OPTION_BOTH'), value=2)])
    async def customlist(self, interaction: discord.Interaction, data: str, list_id: str = None, list_name: str = None, global_list: int = None, list_group: str = None):
        await interaction.response.defer()
        try:
            header = localisation.get('CUSTOMLIST_LOG_HEADER')
            logger.info(f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('CUSTOMLIST_CMD_NAME')} data: {data} list_id {list_id} list_name: {list_name} global_list: {global_list} list_group: {list_group}")
            log = f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('CUSTOMLIST_CMD_NAME')} data: {data} list_id {list_id} list_name: {list_name} global_list: {global_list} list_group: {list_group}"

            if not str(list_id).zfill(3) and not list_name:
                await interaction.followup.send(f"{localisation.get('CUSTOMLIST_MSG_WARNING_MISSING_ARGUMENT')}")
                await in_app_logging.send_log(self.bot, log, 0, 1, interaction)
                return

            if not global_list:
                global_list = 0 if interaction.guild else 1
            if global_list == 0:
                if interaction.guild:
                    global_list = [str(interaction.guild.id)]
                else:
                    await interaction.followup.send(f"{localisation.get('CUSTOMLIST_MSG_WARNING_NO_SERVER')}")
            if global_list == 1:
                global_list = ["GLOBAL"]
            if global_list == 2:
                if interaction.guild:
                    global_list = [str(interaction.guild.id), "GLOBAL"]
                else:
                    global_list = ["GLOBAL"]

            custom_lists = await helpers.load_file("custom_lists")

            lists = {}
            if list_id:
                for server_id in global_list:
                    if str(list_id).zfill(3) in custom_lists[server_id].keys():
                        lists.setdefault(f"{str(list_id).zfill(3)}_{server_id}", custom_lists[server_id][str(list_id).zfill(3)])
            else:
                for server_id in global_list:
                    if server_id not in custom_lists:
                        continue
                for id, customlist in custom_lists[server_id].items():
                    if customlist.get("Name") == list_name:
                        lists.setdefault(f"{str(id).zfill(3)}_{server_id}", customlist)

            if len(lists) > 1:
                await self.send_selection_prompt(interaction, lists, list_group, data, log)
            elif len(lists) == 1:
                key = next(iter(lists))
                await self.process_selection(interaction, key, lists[key], list_group, data, log)
            else:
                await interaction.followup.send(localisation.get('CUSTOMLIST_MSG_WARNING_NO_LIST'))
        except Exception as e:
            await interaction.followup.send(f"{localisation.get('MSG_ERROR_FETCH')} {e}", ephemeral=True)
            logger.info(f"{localisation.get('LOG_ERROR_FETCH')} {e}")
            log += f"\n{localisation.get('LOG_ERROR_FETCH')} {e}"
            await in_app_logging.send_log(self.bot, log, 0, 1, interaction)

    async def send_selection_prompt(self, interaction: discord.Interaction, lists: dict, list_group, data: str, log: str):
        embed_data = []
        for key, list_content in lists.items(), lists:
            embed_data.append([key, list_content["Name"]])

        desc_lines = []
        for idx, (key, name) in enumerate(embed_data):
            list_type = "Global list" if key.endswith("GLOBAL") else "Server list"
            desc_lines.append(f"{idx+1}. {name}: {list_type}")
        desc = "\n".join(desc_lines)

        embed = discord.Embed(
            title=localisation.get('CUSTOMLIST_MSG_CHOOSE_EMBED_TITLE'),
            description=f"{localisation.get('CUSTOMLIST_MSG_CHOOSE_EMBED_DESC')}\n{desc}",
            color=discord.Color(0xff00ff)
        )
        embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')

        view = CustomListCog.ListSelectionView(lists, list_group, data, self.bot, self, log)

        await interaction.followup.send(embed=embed, view=view)

    async def process_selection(self, interaction: discord.Interaction, key: str, custom_list: dict, list_group, data, log):
        try:
            header = localisation.get('CUSTOMLIST_LOG_HEADER')
            list_name = custom_list["Name"]
            del custom_list["Name"]
            if list_group:
                for car_group, car_list in custom_list.copy().items():
                    if str(car_group) != str(list_group):
                        del custom_list[car_group]
            embeds = []
            wrlist_results = []
            for group, cars in custom_list.items():
                results = []
                for car in cars:
                    car = str(car).replace("*", "%")
                    result = await helpers.execute_sql_statement("WRs", querry[data], [f"{car}%"])
                    for row in result:
                        results.append(row)
                if results and data != "wrlist":
                    new_embeds, log = await self.create_embeds(interaction, data, results, list_name, key, group, None, log)
                    embeds.extend(new_embeds)
                else:
                    wrlist_results.extend(results)
            if results:
                await interaction.followup.send(f"{localisation.get('MSG_NOTICE_FETCH')}")
            else:
                await interaction.followup.send(f"{localisation.get('MSG_NOTICE_NO_RESULTS')}")
            if data == "wrlist":
                t1_t3_results = []
                t4_t5_results = []
                wrlist_results = sorted(cars, key=lambda wrlist_results: min(float(result[1]) for result in wrlist_results))
                for wrlist_result in wrlist_results:
                    if any(tier in wrlist_result[3] for tier in ["T1", "T2", "T3"]):
                        t1_t3_results.extend(wrlist_result)
                    if any(tier in wrlist_result[3] for tier in ["T4", "T5"]):
                        t4_t5_results.extend(wrlist_result)
                if t1_t3_results and t4_t5_results:
                    t1_t3_embeds, log = await self.create_embeds(data, interaction, t1_t3_results, list_name, key, group, "T1-T3", log)
                    t4_t5_embeds, log = await self.create_embeds(data, interaction, t4_t5_results, list_name, key, group, "T4-T5", log)
                    await self.send_embeds_wrlist(interaction, t1_t3_embeds, log)
                    await self.send_embeds_wrlist(interaction, t4_t5_embeds, log)
                else:
                    new_embeds, log = await self.create_embeds(data, interaction, wrlist_results, list_name, key, group, None, log)
                    embeds.extend(new_embeds)
                    await self.send_embeds_wrlist(interaction, embeds, log)
            else:
                await self.send_embeds(interaction, embeds, log)

            await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
        except Exception as e:
            await interaction.followup.send(f"{localisation.get('MSG_ERROR_FETCH')} {e}", ephemeral=True)
            logger.info(f"{localisation.get('LOG_ERROR_FETCH')} {e}")
            log += f"\n{localisation.get('LOG_ERROR_FETCH')} {e}"
            await in_app_logging.send_log(self.bot, log, 0, 1, interaction)

    async def create_embeds(self, interaction: discord.Interaction, data: str, results: list, list_name, key: str, group: str, tier, log: str):
        header = localisation.get('CUSTOMLIST_LOG_HEADER')
        logger.info(f"{header}{localisation.get('LOG_BUILD_EMBEDS')}")
        log += f"\n{header}{localisation.get('LOG_BUILD_EMBEDS')}"
        embeds = []
        if data == "wr":
            for row in results:
                result = list(row)
                result[3] = await helpers.emojify_tier(result[3])
                result[4] = await helpers.emojify_rarity(result[4])
                markdown_characters = ['*', '_', '~', '#']
                escaped_text = ''
                if result[14][0] in markdown_characters:
                    escaped_text = '\\'
                if isinstance(result[8], float) or result[8].replace('.', '', 1).isdigit():
                    result[8] = f"{float(result[8]):.2f}"

                embed = discord.Embed(
                    title=f"{group+': ' if group != 'UNGROUPED' else ''}{result[2]}",
                    description=f"# {result[3]}   {result[4]}",
                    color=discord.Color(0xff00ff)
                )
                embed.add_field(name=f"{localisation.get('WR_MSG_EMBED_DESC_PP')} {result[5]}\n{localisation.get('WR_MSG_EMBED_DESC_EVO')} {result[6]}\n", value=f"\n", inline=False)
                embed.add_field(name=f"{localisation.get('WR_MSG_EMBED_DESC_NOS')} {result[7]}\n{localisation.get('WR_MSG_EMBED_DESC_FD')} {result[8]}\n{localisation.get('WR_MSG_EMBED_DESC_TP')} {result[9]}\n{localisation.get('WR_MSG_EMBED_DESC_DYNO')} {float(result[10]):.3f}", value=f"\n", inline=False)
                embed.add_field(name=f"{localisation.get('WR_MSG_EMBED_DESC_WR')} {float(result[11]):.3f}", value=f"**{localisation.get('WR_MSG_EMBED_DESC_DRIVER')} {escaped_text}{result[14]}\n**", inline=False)
                embed.add_field(name=f"{localisation.get('WR_MSG_EMBED_DESC_UPGRADES')} {result[12]}", value=f"**[{localisation.get('WR_MSG_EMBED_DESC_SHIFT')}]({result[13]})**\n\n-# {result[0]} - {result[1]}", inline=False)
                embed.set_footer(text=f"""ListID: {key[:3]}{f" - {localisation.get('CUSTOMLIST_MSG_RESULT_EMBED_FOOTER')} {list_name}" if list_name else ""}""")
                embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')
                embeds.append(embed)
        elif data == "wrlist":
            title = f"""{localisation.get('CUSTOMLIST_MSG_WRLIST_EMBED_TITLE')} {list_name if list_name else f"{localisation.get('CUSTOMLIST_MSG_WRLIST_EMBED_TITLE_NO_LIST_NAME')} {key[:3]}"} {f"({await helpers.emojify_tier(tier)})" if tier else ""}"""
            wrlist = []
            descriptions = []
            for idx, row in enumerate(results, start=1):
                result = list(row)
                line = f"{idx}. {result[0]} ({group if group != 'UNGROUPED' else ''})\n{await helpers.emojify_rarity(result[2])} | {float(result[1]):.3f}s"
                wrlist.append(line)
            for i in range(0, len(wrlist), 10):
                description = wrlist[i:i+10]
                descriptions.append("\n".join(description))
            for idx, desc in enumerate(descriptions, start=1):
                embed = discord.Embed(
                    title=title,
                    description=desc,
                    color=discord.Color(0x000000)
                )
                embed.set_footer(text=f"{localisation.get('MSG_EMBED_DESC_PAGE')} {idx} {localisation.get('MSG_EMBED_DESC_OF')} {len(descriptions)}")
                embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')
                embeds.append(embed)
        elif data == "s6effects":
            for row in results:
                result = list(row)
                result[3] = await helpers.emojify_tier(result[3])
                result[4] = await helpers.emojify_rarity(result[4])
                result[8] = f"{float(result[8]):.2f}" if await helpers.is_float(result[8]) else result[8]
                if result[18] == 'false':
                    spacing = max([len(f"{localisation.get('PART_ENGINE')}"), len(f"{localisation.get('PART_TURBO')}"), len(f"{localisation.get('PART_INTAKE')}"), len(f"{localisation.get('PART_NITROUS')}"), len(f"{localisation.get('PART_BODY')}"), len(f"{localisation.get('PART_TIRES')}"), len(f"{localisation.get('PART_TRANSMISSION')}"), len(f"{localisation.get('S6_EFFECTS_MSG_EMBED_DESC_PART')}")])
                    categories = [f"{localisation.get('PART_ENGINE'):<{spacing}}", f"{localisation.get('PART_TURBO'):<{spacing}}", f"{localisation.get('PART_INTAKE'):<{spacing}}", f"{localisation.get('PART_NITROUS'):<{spacing}}", f"{localisation.get('PART_BODY'):<{spacing}}", f"{localisation.get('PART_TIRES'):<{spacing}}", f"{localisation.get('PART_TRANSMISSION'):<{spacing}}"]
                else:
                    spacing = max([len(f"{localisation.get('PART_MOTOR')}"), len(f"{localisation.get('PART_BATTERY')}"), len(f"{localisation.get('PART_INVERTER')}"), len(f"{localisation.get('PART_OVERBOOST')}"), len(f"{localisation.get('PART_BODY')}"), len(f"{localisation.get('PART_TIRES')}"), len(f"{localisation.get('PART_TRANSMISSION')}"), len(f"{localisation.get('S6_EFFECTS_MSG_EMBED_DESC_PART')}")])
                    categories = [f"{localisation.get('PART_MOTOR'):<{spacing}}", f"{localisation.get('PART_BATTERY'):<{spacing}}", f"{localisation.get('PART_INVERTER'):<{spacing}}", f"{localisation.get('PART_OVERBOOST'):<{spacing}}", f"{localisation.get('PART_BODY'):<{spacing}}", f"{localisation.get('PART_TIRES'):<{spacing}}", f"{localisation.get('PART_TRANSMISSION'):<{spacing}}"]

                values = result[11:18]
                offsets = [round(float(values[i]) - float(result[10]), 3) for i in range(7)]
                combined = sorted(zip(values, categories, offsets))
                sorted_values, sorted_categories, sorted_offsets = zip(*combined)
                chart_lines = [f"{category}   {offset:+.3f}          {value:6.3f}" for category, offset, value in zip(sorted_categories, sorted_offsets, sorted_values)]
                chart = "\n".join(chart_lines)

                embed = discord.Embed(
                    title=f"{group+': ' if group != 'UNGROUPED' else ''}{result[2]}",
                    description=f"# {result[3]}   {result[4]}",
                    color=discord.Color(0xff00ff)
                )
                embed.add_field(name=f"{localisation.get('S6_EFFECTS_MSG_EMBED_DESC_S5PP')} {result[5]}\n{localisation.get('S6_EFFECTS_MSG_EMBED_DESC_S5EVO')} {result[6]}\n", value=f"", inline=False)
                embed.add_field(name=f"{localisation.get('S6_EFFECTS_MSG_EMBED_DESC_S5NOS')} {result[7]}\n{localisation.get('S6_EFFECTS_MSG_EMBED_DESC_S5FD')} {result[8]}\n{localisation.get('S6_EFFECTS_MSG_EMBED_DESC_S5TP')} {result[9]}\n", value=f"**{localisation.get('S6_EFFECTS_MSG_EMBED_DESC_S5DYYO')} {float(result[10]):.3f}**", inline=False)
                embed.add_field(name=f"{localisation.get('S6_EFFECTS_MSG_EMBED_DESC_TOPS6')} {sorted_categories[0]} ({float(sorted_offsets[0]):+.3f}) ({float(sorted_values[0]):.3f})", value=f"​\n`"+f"{localisation.get('S6_EFFECTS_MSG_EMBED_DESC_PART'):<{spacing+3}}"+f"{localisation.get('S6_EFFECTS_MSG_EMBED_DESC_OFFSET'):<16}"[:16]+f"{localisation.get('S6_EFFECTS_MSG_EMBED_DESC_TIME'):>6}"+f"\n{chart}`\n\n-# {result[0]} - {result[1]}", inline=False)
                embed.set_footer(text=f"""ListID: {key[:3]}{f" - {localisation.get('CUSTOMLIST_MSG_RESULT_EMBED_FOOTER')} {list_name}" if list_name else ""}""")
                embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')
                embeds.append(embed)
        elif data == "info":
            for row in results:
                result = list(row)
                result[3] = await helpers.emojify_tier(result[3])
                result[4] = await helpers.emojify_rarity(result[4])
                if result[7] == "false":
                    result[7] = f"{localisation.get('INFO_MSG_CAR_TYPE_COMBUSTION')}"
                else:
                    result[7] = f"{localisation.get('INFO_MSG_CAR_TYPE_EV')}"
		
                embed = discord.Embed(
                    title=f"{group+': ' if group != 'UNGROUPED' else ''}{result[2]}",
                    description=f"# {result[3]}   {result[4]}",
                    color=discord.Color(0xff00ff)
                )
                embed.add_field(name=f"{localisation.get('INFO_MSG_EMBED_DESC_CAT_INFO_TITLE')}", value=f"**{result[7]}**\n{result[6]}\n\n**[{localisation.get('INFO_MSG_EMBED_DESC_CAT_INFO_DESC')}](https://discord.com/channels/683998568305917970/{result[8]})**\n\n{result[0]} - {result[1]}", inline=False)
                embed.set_footer(text=f"""ListID: {key[:3]}{f" - {localisation.get('CUSTOMLIST_MSG_RESULT_EMBED_FOOTER')} {list_name}" if list_name else ""}""")
                embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')
                embed.set_image(url=f"https://raw.githubusercontent.com/Nitro4CSR/{result[5]}")
                embeds.append(embed)
        elif data == "vision":
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
                    spacing = max([len(f"{localisation.get('PART_ENGINE')}"), len(f"{localisation.get('PART_TURBO')}"), len(f"{localisation.get('PART_INTAKE')}"), len(f"{localisation.get('PART_NITROUS')}"), len(f"{localisation.get('PART_BODY')}"), len(f"{localisation.get('PART_TIRES')}"), len(f"{localisation.get('PART_TRANSMISSION')}"), len(f"{localisation.get('S6_EFFECTS_MSG_EMBED_DESC_PART')}")])
                    categories = [f"{localisation.get('PART_ENGINE'):<{spacing}}", f"{localisation.get('PART_TURBO'):<{spacing}}", f"{localisation.get('PART_INTAKE'):<{spacing}}", f"{localisation.get('PART_NITROUS'):<{spacing}}", f"{localisation.get('PART_BODY'):<{spacing}}", f"{localisation.get('PART_TIRES'):<{spacing}}", f"{localisation.get('PART_TRANSMISSION'):<{spacing}}"]
                    result[17] = f"{localisation.get('INFO_MSG_CAR_TYPE_CUMBUSTION')}"
                else:
                    spacing = max([len(f"{localisation.get('PART_MOTOR')}"), len(f"{localisation.get('PART_BATTERY')}"), len(f"{localisation.get('PART_INVERTER')}"), len(f"{localisation.get('PART_OVERBOOST')}"), len(f"{localisation.get('PART_BODY')}"), len(f"{localisation.get('PART_TIRES')}"), len(f"{localisation.get('PART_TRANSMISSION')}"), len(f"{localisation.get('S6_EFFECTS_MSG_EMBED_DESC_PART')}")])
                    categories = [f"{localisation.get('PART_MOTOR'):<{spacing}}", f"{localisation.get('PART_BATTERY'):<{spacing}}", f"{localisation.get('PART_INVERTER'):<{spacing}}", f"{localisation.get('PART_OVERBOOST'):<{spacing}}", f"{localisation.get('PART_BODY'):<{spacing}}", f"{localisation.get('PART_TIRES'):<{spacing}}", f"{localisation.get('PART_TRANSMISSION'):<{spacing}}"]
                    result[17] = f"{localisation.get('INFO_MSG_CAR_TYPE_EV')}"
                if not any(x is None for x in result[24:31]) or result[27] == "-":
                    values = result[24:31]
                    offsets = [round(float(values[i]) - float(result[24]), 3) for i in range(7)]
                    combined = sorted(zip(values, categories, offsets))
                    sorted_values, sorted_categories, sorted_offsets = zip(*combined)
                    chart_lines = [f"{category}   {f"{offset:+.3f}" if await helpers.is_float(offset) else offset}          {f"{value:6.3f}" if await helpers.is_float(value) else value}" for category, offset, value in zip(sorted_categories, sorted_offsets, sorted_values)]
                    chart = "\n".join(chart_lines)
                    value = f"{localisation.get('S6_EFFECTS_MSG_EMBED_DESC_S5PP')} {result[19]}\n{localisation.get('S6_EFFECTS_MSG_EMBED_DESC_S5EVO')} {result[20]}\n\n{localisation.get('S6_EFFECTS_MSG_EMBED_DESC_S5NOS')} {result[21]}\n{localisation.get('S6_EFFECTS_MSG_EMBED_DESC_S5FD')} {f"{float(result[22]):.2f}" if await helpers.is_float(result[22]) else result[22]}\n{localisation.get('S6_EFFECTS_MSG_EMBED_DESC_S5TP')} {result[23]}\n{localisation.get('S6_EFFECTS_MSG_EMBED_DESC_S5DYYO')} {f"{float(result[24]):.3f}" if await helpers.is_float(result[24]) else result[24]}\n\n**{localisation.get('S6_EFFECTS_MSG_EMBED_DESC_TOPS6')}** {sorted_categories[0]} ({f"{float(sorted_offsets[0]):+.3f}" if await helpers.is_float(sorted_offsets[0]) else sorted_offsets[0]}) ({f"{float(sorted_values[0]):.3f}" if await helpers.is_float(sorted_values[0]) else sorted_values[0]})"+f"​\n`"+f"{localisation.get('S6_EFFECTS_MSG_EMBED_DESC_PART'):<{spacing+3}}"+f"{localisation.get('S6_EFFECTS_MSG_EMBED_DESC_OFFSET'):<16}"[:16]+f"{localisation.get('S6_EFFECTS_MSG_EMBED_DESC_TIME'):>6}"+f"\n{chart}`"
                else:
                    value = f"{localisation.get('S6_EFFECTS_MSG_WARNING_CAR_NOT_FOUND')} [{localisation.get('S6_EFFECTS_MSG_CONTRIBUTE')}](https://docs.google.com/spreadsheets/d/1pBamDQTOcWyJoUowrXM05Tj567UVAti1VA8zWsSlrhM/edit)"
                embed = discord.Embed(
                    title=f"{group+': ' if group != 'UNGROUPED' else ''}{result[2]}",
                    description=f"# {result[3]}   {result[4]}",
                    color=discord.Color(0xff00ff)
                )
                embed.add_field(name=f"{localisation.get('VISION_MSG_EMBED_DESC_CAR_INFO')}", value=f"{result[17]}\n{result[16]}\n\n[{localisation.get('INFO_MSG_EMBED_DESC_CAT_INFO_DESC')}](https://discord.com/channels/683998568305917970/1122543660282695780/threads/{result[18]})")
                embed.add_field(name=f"{localisation.get('VISION_MSG_EMBED_DESC_WR_TUNE')}", value=f"{localisation.get('WR_MSG_EMBED_DESC_PP')} {result[5]}\n{localisation.get('WR_MSG_EMBED_DESC_EVO')} {result[6]}\n\n{localisation.get('WR_MSG_EMBED_DESC_NOS')} {result[7]}\n{localisation.get('WR_MSG_EMBED_DESC_FD')}: {f"{float(result[8]):.2f}" if await helpers.is_float(result[8]) else result[8]}\n{localisation.get('WR_MSG_EMBED_DESC_TP')} {result[9]}\n{localisation.get('WR_MSG_EMBED_DESC_DYNO')} {f"{float(result[10]):.3f}" if await helpers.is_float(result[10]) else result[10]}\n\n{localisation.get('WR_MSG_EMBED_DESC_WR')} {f"{float(result[11]):.3f}" if await helpers.is_float(result[11]) else result[11]}\n{localisation.get('WR_MSG_EMBED_DESC_DRIVER')} {escaped_text}{result[14]}\n\n{localisation.get('WR_MSG_EMBED_DESC_UPGRADES')} {result[12]}\n[{localisation.get('WR_MSG_EMBED_DESC_SHIFT')}]({result[13]})", inline=False)
                embed.add_field(name=f"{localisation.get('VISION_MSG_EMBED_DESC_S6_EFFECTS')}", value=f"{value}\n\n{result[0]} - {result[1]}")
                embed.set_footer(text=f"""ListID: {key[:3]}{f" - {localisation.get('CUSTOMLIST_MSG_RESULT_EMBED_FOOTER')} {list_name}" if list_name else ""}""")
                embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')
                embed.set_image(url=f"https://raw.githubusercontent.com/Nitro4CSR/{result[15]}")
                embeds.append(embed)
        logger.info(f"{header}{localisation.get('LOG_EMBEDS_BUILD')}")
        log += f"\n{header}{localisation.get('LOG_EMBEDS_BUILD')}"
        return embeds, log

    async def send_embeds(self, interaction: discord.Interaction, embeds: list, log: str):
        header = localisation.get('CUSTOMLIST_LOG_HEADER')
        messages = []
        message = []
        for embed in embeds:
            message.append(embed)
            if len(message) == 10:
                messages.append(message)
                message = []
        if message:
            messages.append(message)
        for message in messages:
            await interaction.followup.send(embeds=message)
        logger.info(f"{header}{localisation.get('LOG_DONE_CHANNEL')}")
        log += f"\n{header}{localisation.get('LOG_DONE_CHANNEL')}"

    async def send_embeds_wrlist(self, interaction: discord.Interaction, embeds: list, log: str):
        header = localisation.get('CUSTOMLIST_LOG_HEADER')
        page = 0
        view = CustomListCog.NavigationView(embeds, page, interaction.user, self.bot, self)
        await interaction.followup.send(embed=embeds[page], view=view)


    class NavigationView(discord.ui.View):
        def __init__(self, embeds, page, user, bot, cog):
            super().__init__(timeout=300)
            self.embeds = embeds
            self.page = page
            self.user = user
            self.bot = bot
            self.cog = cog
            self.previous_button.label = localisation.get('MSG_BUTTON_PREVIOUS')
            self.next_button.label = localisation.get('MSG_BUTTON_NEXT')
            self.jump_button.label = localisation.get('MSG_BUTTON_JUMP_TO_PAGE')

        @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary)
        async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            if interaction.user != self.user:
                await interaction.response.send_message(f"{localisation.get('MSG_NO_PERMISSION')}", ephemeral=True)
                return
            self.page -= 1
            if self.page < 0:
                self.page = len(self.embeds) - 1
            await interaction.response.edit_message(embed=self.embeds[self.page], view=self)

        @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
        async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            if interaction.user != self.user:
                await interaction.response.send_message(f"{localisation.get('MSG_NO_PERMISSION')}", ephemeral=True)
                return
            self.page += 1
            if self.page >= len(self.embeds):
                self.page = 0
            await interaction.response.edit_message(embed=self.embeds[self.page], view=self)

        @discord.ui.button(label="Jump to Page", style=discord.ButtonStyle.secondary)
        async def jump_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            if interaction.user != self.user:
                return await interaction.response.send_message(f"{localisation.get('MSG_NO_PERMISSION')}", ephemeral=True)
            await interaction.response.send_modal(CustomListCog.JumpModal(self))

        async def on_timeout(self):
            header = localisation.get('WRLIST_LOG_HEADER')
            logger.info(f"{header}{localisation.get('UPDATES_LOG_TIMEOUT')}")
            for child in self.children:
                child.disabled = True
            if hasattr(self, "message"):
                await self.message.edit(view=self)
            self.stop()


    class JumpModal(discord.ui.Modal):
        def __init__(self, view: "CustomListCog.NavigationView"):
            super().__init__(title=view.bot.localisation.get('MSG_BUTTON_JUMP_TO_PAGE'))
            self.view = view
            self.input = discord.ui.TextInput(
                label=f"{self.view.bot.localisation.get('MSG_MODAL_INPUT_TITLE')}",
                placeholder=f"{self.view.bot.localisation.get('MSG_MODAL_JUMP_TO_PAGE')}",
                required=True,
                max_length=10
            )
            self.add_item(self.input)

        async def on_submit(self, interaction: discord.Interaction):
            value = self.input.value.strip()
            try:
                if value.startswith(("+", "-")):
                    offset = int(value)
                    self.view.page += offset
                else:
                    self.view.page = int(value) - 1
                self.view.page = max(0, min(self.view.page, len(self.view.embeds) - 1))
            except ValueError:
                await interaction.response.send_message(f"{self.view.bot.localisation.get('MSG_JUMP_INVALID')}", ephemeral=True)
                return
            await interaction.response.edit_message(embed=self.view.embeds[self.view.page], view=self.view)


    class ListSelectionView(discord.ui.View):
        def __init__(self, lists: dict, list_group, data, bot, cog, log):
            super().__init__(timeout=180)
            self.lists = lists
            self.list_group = list_group
            self.data = data
            self.bot = bot
            self.cog = cog
            self.log = log

            for idx, (key, custom_list) in enumerate(lists.items(), start=1):
                self.add_item(CustomListCog.ListButton(idx, key, custom_list, list_group, self.data, bot, cog, log))

        async def on_timeout(self, interaction: discord.Interaction):
            await interaction.response.send_message(f"{localisation.get('CUSTOMLIST_MSG_SELECTION_TIMEOUT')}")

    class ListButton(discord.ui.Button):
        def __init__(self, idx, key, custom_list, list_group, data, bot, cog, log):
            super().__init__(label=str(idx), style=discord.ButtonStyle.primary)
            self.idx = idx
            self.key = key
            self.custom_list = custom_list
            self.list_group = list_group
            self.data = data
            self.bot = bot
            self.cog = cog
            self.log = log

        async def callback(self, interaction: discord.Interaction):
            await interaction.response.defer()
            await interaction.followup.edit_message(content=f"{localisation.get('CUSTOMLIST_MSG_SELECTION_CONFIRM')}", view=self)
            await self.cog.process_selection(interaction, self.key, self.custom_list, self.list_group, self.data, self.log)

async def setup(bot):
    await bot.add_cog(CustomListCog(bot))