import discord
from discord.ext import commands
from discord import app_commands
import in_app_logging
import helpers

logger = helpers.load_logging()
localisation = dict(helpers.load_localisation())

class WRlistCog(commands.Cog):
    def __init__(self, bot: commands.bot):
        self.bot = bot

    @app_commands.command(name=localisation.get('WRLIST_CMD_NAME'), description=localisation.get('WRLIST_CMD_DESC'))
    @app_commands.describe(car=localisation.get('ANY_CMD_CAR'), rarity=localisation.get('ANY_CMD_RARITY'), tier=localisation.get('WRLIST_CMD_RACE'), csr2_version=localisation.get('ANY_CMD_CSR2_VERSION'))
    @app_commands.choices(race=[app_commands.Choice(name=localisation.get('WRLIST_CMD_RACE_OPTION_12_MILE'), value="'T4', 'T5'"), app_commands.Choice(name=localisation.get('WRLIST_CMD_RACE_OPTION_14_MILE'), value="'T1', 'T2', 'T3'")])
    @app_commands.choices(rarity=helpers.load_command_options_rarity(localisation))
    @app_commands.choices(tier=helpers.load_command_options_tier(localisation))
    async def wrlist(self, interaction: discord.Interaction, car: str = None, race: str = None, rarity: str = None, tier: str = None, csr2_version: str = None):
        await interaction.response.defer()
        try:
            header = localisation.get('WRLIST_LOG_HEADER')
            logger.info(f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('WRLIST_CMD_NAME')} car: {car} race: {race} rarity: {rarity} tier: {tier} csr2_version: {csr2_version}")
            log = f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('WRLIST_CMD_NAME')} car: {car} race: {race} rarity: {rarity} tier: {tier} csr2_version: {csr2_version}"
            if not any([car, race, rarity, tier, csr2_version]):
                tier = "T5"
            parameters = []
            query = """\nSELECT records."Ingame Name Clarification", records."WR-BEST ET", records."★", records.UniqueID\nFROM records"""
            if csr2_version:
                query += """\nJOIN info ON records.UniqueID = info.UniqueID"""
            query += """\nWHERE "WR-BEST ET" IS NOT NULL AND "WR-BEST ET" <> '0.000'"""
            if car:
                if car.startswith('T') and len(car) > 1 and car[1] in '12345':
                    query += """ AND records.UniqueID COLLATE NOCASE LIKE ?"""
                elif "_" in car:
                    query += """ AND records."DB Name" COLLATE NOCASE LIKE ?"""
                else:
                    query += """ AND records."Ingame Name Clarification" COLLATE NOCASE LIKE ?"""
                parameters.append(f"%{car}%")
            if race:
                query += f""" AND records.Un IN ({race})"""
            if rarity:
                query += """ AND records.★ LIKE ?"""
                parameters.append(rarity)
            if tier:
                query += """ AND records.Un == ?"""
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
                query += """ AND info."Vision Info" LIKE ?"""
                parameters.append(f"{csr2_version}")
            query += """\nORDER BY records."WR-BEST ET" """
            logger.info(f"{header}{localisation.get('LOG_QUERY')} {query}\n{localisation.get('LOG_PARAMETERS')} {parameters}")
            log += f"\n{header}{localisation.get('LOG_QUERY')} ```{query}```\n{localisation.get('LOG_PARAMETERS')} {parameters}"
            results = await helpers.execute_sql_statement("WRs", query, parameters)
            if results:
                logger.info(f"{header}{len(results)} {localisation.get('LOG_RESULTS_FOUND')}")
                log += f"\n{header}{len(results)} {localisation.get('LOG_RESULTS_FOUND')}"
                t1_t3_results = []
                t4_t5_results = []
                for result in results:
                    if any(tier in result[3] for tier in ["T1", "T2", "T3"]):
                        t1_t3_results.append(result)
                    if any(tier in result[3] for tier in ["T4", "T5"]):
                        t4_t5_results.append(result)
                await interaction.followup.send(f"{localisation.get('MSG_NOTICE_FETCH')}")
                if t1_t3_results and t4_t5_results:
                    view1 = WRlistCog.PaginatedView(t1_t3_results, interaction.user, car, race, rarity, "T1-T3", csr2_version, self.bot, self)
                    view2 = WRlistCog.PaginatedView(t4_t5_results, interaction.user, car, race, rarity, "T4-T5", csr2_version, self.bot, self)
                    await interaction.followup.send(f"**{localisation.get('WRLIST_MSG_14M_RESULTS')}**", embed=await view1.get_embed_page(), view=view1)
                    await interaction.followup.send(f"**{localisation.get('WRLIST_MSG_12M_RESULTS')}**", embed=await view2.get_embed_page(), view=view2)
                else:
                    view = WRlistCog.PaginatedView(results, interaction.user, car, race, rarity, tier, csr2_version, self.bot, self)
                    await view.start(interaction)
            else:
                logger.info(f"{header}{localisation.get('LOG_NO_RESULTS')}")
                log += f"\n{header}{localisation.get('LOG_NO_RESULTS')}"
                await interaction.followup.send(f"{localisation.get('WRLIST_MSG_NO_RESULTS')}", ephemeral=True)
            await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
        except Exception as e:
            await interaction.followup.send(f"{localisation.get('MSG_ERROR_FETCH')} {e}")
            logger.info(f"{localisation.get('LOG_ERROR_FETCH')} {e}")
            log += f"{localisation.get('LOG_ERROR_FETCH')} {e}"
            await in_app_logging.send_log(self.bot, log, 0, 1, interaction)

    class PageJumpModal(discord.ui.Modal, title="Jump to Page"):
        page_number = discord.ui.TextInput(label="Enter Page Number or +/- Offset", required=True)

        def __init__(self, view: "WRlistCog.PaginatedView"):
            super().__init__()
            self.view = view

        async def on_submit(self, interaction: discord.Interaction):
            try:
                input_text = self.page_number.value.strip()
                if input_text.startswith(('+', '-')):
                    offset = int(input_text)
                    new_page = (self.view.page_number + offset - 1) % self.view.max_pages + 1
                else:
                    new_page = int(input_text)
                    if new_page < 1 or new_page > self.view.max_pages:
                        new_page = (new_page - 1) % self.view.max_pages + 1

                self.view.page_number = new_page
                embed = await self.view.get_embed_page()
                await interaction.response.edit_message(embed=embed, view=self.view)
            except ValueError:
                await interaction.response.send_message(f"{localisation.get('MSG_JUMP_INVALID')}", ephemeral=True)

    class PaginatedView(discord.ui.View):
        def __init__(self, results, user, car, race, rarity, tier, csr2_version, bot, cog):
            super().__init__(timeout=300)
            self.results = results
            self.user = user
            self.car = car
            self.race = race
            self.rarity = rarity
            self.tier = tier
            self.csr2_version = csr2_version
            self.bot = bot
            self.cog = cog
            self.page_number = 1
            self.page_size = 10
            self.max_pages = len(results) // self.page_size + (1 if len(results) % self.page_size != 0 else 0)
            self.message = None
            self.previous_button.label = localisation.get('MSG_BUTTON_PREVIOUS')
            self.next_button.label = localisation.get('MSG_BUTTON_NEXT')
            self.jump_button.label = localisation.get('MSG_BUTTON_JUMP_TO_PAGE')

        async def get_embed_page(self):
            header = localisation.get('WRLIST_LOG_HEADER')
            start_index = (self.page_number - 1) * self.page_size
            end_index = start_index + self.page_size
            self.results = [[row[0], row[1], await helpers.emojify_rarity(row[2]), row[3]] for row in self.results]
            page_results = self.results[start_index:end_index]
            car_display = self.car if self.car else f"{localisation.get('WRLIST_MSG_EMBED_TITLE_ANY_CAR')}"
            race_display = (f"{localisation.get('WRLIST_MSG_EMBED_TITLE_12M')}" if self.race == "'T4', 'T5'" else f"{localisation.get('WRLIST_MSG_EMBED_TITLE_14M')}") if self.race else f"{localisation.get('WRLIST_MSG_EMBED_TITLE_ANY')}"
            rarity_display = f"{await helpers.emojify_rarity(self.rarity)}" if self.rarity else f"{localisation.get('WRLIST_MSG_EMBED_TITLE_ANY_RARITY')}"
            tier_display = f"{await helpers.emojify_tier(self.tier)}" if self.tier else f"{localisation.get('WRLIST_MSG_EMBED_TITLE_ANY_TIER')}"
            version_display = f"{localisation.get('WRLIST_MSG_EMBED_TITLE_VERSION')} {self.csr2_version}" if self.csr2_version else f"{localisation.get('WRLIST_MSG_EMBED_TITLE_ANY_VERSION')}"

            logger.info(f"{header}{localisation.get('WRLIST_LOG_EMBED_PAGE')} {self.page_number}")
            embed = discord.Embed(
                title=f"{localisation.get('WRLIST_MSG_EMBED_TITLE_1')} {tier_display} {car_display} {localisation.get('WRLIST_MSG_EMBED_TITLE_2')} {rarity_display}{localisation.get('WRLIST_MSG_EMBED_TITLE_3')} {race_display} {localisation.get('WRLIST_MSG_EMBED_TITLE_4')} {version_display}",
                description="\n".join(
                    f"{start_index + i + 1}. {row[0]}\n{row[2]} | {float(row[1]):.3f}s"
                    for i, row in enumerate(page_results)
                ),
                color=discord.Color(0xff00ff)
            )
            embed.set_footer(text=f"{localisation.get('MSG_EMBED_DESC_PAGE')} {self.page_number} {localisation.get('MSG_EMBED_DESC_OF')} {self.max_pages}")
            embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')
            return embed

        async def start(self, interaction: discord.Interaction):
            header = localisation.get('WRLIST_LOG_HEADER')
            logger.info(f"{header}{localisation.get('LOG_EMBED_INITIAL')}")
            embed = await self.get_embed_page()
            self.message = await interaction.followup.send(embed=embed, view=self)

        @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary)
        async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            header = localisation.get('WRLIST_LOG_HEADER')
            if interaction.user != self.user:
                await interaction.response.send_message(f"{localisation.get('MSG_NO_PERMISSION')}", ephemeral=True)
                return

            self.page_number -= 1
            if self.page_number < 1:
                self.page_number = self.max_pages

            logger.info(f"{header}{localisation.get('WRLIST_LOG_EMBED_PREVIOUS')} {self.page_number}")
            embed = await self.get_embed_page()
            await interaction.response.edit_message(embed=embed, view=self)

        @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
        async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            header = localisation.get('WRLIST_LOG_HEADER')
            if interaction.user != self.user:
                await interaction.response.send_message(f"{localisation.get('MSG_NO_PERMISSION')}", ephemeral=True)
                return

            self.page_number += 1
            if self.page_number > self.max_pages:
                self.page_number = 1

            logger.info(f"{header}{localisation.get('LOG_EMBED_NEXT')} {self.page_number}")
            embed = await self.get_embed_page()
            await interaction.response.edit_message(embed=embed, view=self)

        @discord.ui.button(label="Jump to Page", style=discord.ButtonStyle.secondary)
        async def jump_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            if interaction.user != self.user:
                return await interaction.response.send_message(f"{localisation.get('MSG_NO_PERMISSION')}", ephemeral=True)
            await interaction.response.send_modal(self.cog.PageJumpModal(self))

        async def on_timeout(self):
            header = localisation.get('WRLIST_LOG_HEADER')
            logger.info(f"{header}{localisation.get('UPDATES_LOG_TIMEOUT')}")
            for child in self.children:
                child.disabled = True
            if hasattr(self, "message"):
                await self.message.edit(view=self)
            self.stop()

async def setup(bot):
    await bot.add_cog(WRlistCog(bot))
