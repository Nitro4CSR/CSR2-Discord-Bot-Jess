import asyncio
import discord
from discord.ext import commands
from discord import app_commands, ui
from cogs import communitytune
import in_app_logging
import tunes_manager
import helpers

logger = helpers.load_logging()
localisation = dict(helpers.load_localisation())

log = None
active_submissions = {}

class ShareTuneCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name=localisation.get('SHARE_TUNE_CMD_NAME'), description=localisation.get('SHARE_TUNE_CMD_DESC'))
    @app_commands.describe(fusions=localisation.get('SHARE_TUNE_CMD_FUSIONS'))
    @app_commands.choices(fusions=[app_commands.Choice(name=localisation.get('SHARE_TUNE_CMD_FUSIONS_OPTION_MAXED'), value=int(1)), app_commands.Choice(name=localisation.get('SHARE_TUNE_CMD_FUSIONS_OPTION_STOCK'), value=int(2)), app_commands.Choice(name=localisation.get('SHARE_TUNE_CMD_FUSIONS_OPTION_CUSTOM'), value=int(0))])
    async def sharetune(self, interaction: discord.Interaction, fusions: int = None):
        await interaction.response.defer()
        try:
            global log
            header = localisation.get('SHARE_TUNE_LOG_HEADER')
            logger.info(f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('SHARE_TUNE_CMD_NAME')}")
            log = f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('SHARE_TUNE_CMD_NAME')}"
            if fusions is None:
                fusions = 0
            active_submissions[interaction.user.id] = {"Messages": {}, "Fusions": fusions, "SelectionPage": 0, "Car": None}
            if interaction.guild:
                logger.info(f"{localisation.get('SHARE_TUNE_LOG_SERVER')}")
                log += f"{localisation.get('SHARE_TUNE_LOG_SERVER')}"
                await interaction.followup.send(f"{localisation.get('SHARE_TUNE_MSG_LOOP_CONTINUE')}")
            else:
                logger.info(f"{localisation.get('SHARE_TUNE_LOG_DMS')}")
                log += f"{localisation.get('SHARE_TUNE_LOG_DMS')}"
            await interaction.followup.send(f"{localisation.get('SHARE_TUNE_MSG_LOOP_START')}") if not interaction.guild else await interaction.user.send(f"{localisation.get('SHARE_TUNE_MSG_LOOP_START')}")
            logger.info(f"{localisation.get('SHARE_TUNE_LOG_DM_SUCCESS')}")
            log += f"{localisation.get('SHARE_TUNE_LOG_DM_SUCCESS')}"
            active_submissions["Chunks"] = await self.get_car_chunks()
            selection_page = await self.get_selection_page(page = active_submissions[interaction.user.id]["SelectionPage"])
            Buttons = self.CarSelectionButtons(active_submissions["Chunks"][active_submissions[interaction.user.id]["SelectionPage"]], interaction.user.id, self.bot, self)
            msg = await interaction.user.send(embed=selection_page, view=Buttons)
            active_submissions[interaction.user.id]["Messages"]["SelectionMessage"] = msg
        except Exception as e:
            await interaction.followup.send(f"{localisation.get('MSG_ERROR_FETCH')} {e}")
            logger.info(f"{localisation.get('LOG_ERROR_FETCH')} {e}")
            log += f"{localisation.get('LOG_ERROR_FETCH')} {e}"
            await in_app_logging.send_log(self.bot, log, 0, 1, interaction)

    async def submission_loop(self, interaction: discord.Interaction):
        global log
        header = localisation.get('SHARE_TUNE_LOG_HEADER')
        logger.info(f"{localisation.get('SHARE_TUNE_LOG_SUBMISSION_LOOP')}")
        log += f"{localisation.get('SHARE_TUNE_LOG_SUBMISSION_LOOP')}"
        questions = [
            f"{localisation.get('SHARE_TUNE_MSG_QUESTION_01')}",
            f"{localisation.get('SHARE_TUNE_MSG_QUESTION_02')}",
            f"{localisation.get('SHARE_TUNE_MSG_QUESTION_03')}",
            f"{localisation.get('SHARE_TUNE_MSG_QUESTION_04')}",
            f"{localisation.get('SHARE_TUNE_MSG_QUESTION_05')}",
            f"{localisation.get('SHARE_TUNE_MSG_QUESTION_06')}",
            f"{localisation.get('SHARE_TUNE_MSG_QUESTION_07')}",
            f"{localisation.get('SHARE_TUNE_MSG_QUESTION_08')}",
            f"{localisation.get('SHARE_TUNE_MSG_QUESTION_09')}",
            f"{localisation.get('SHARE_TUNE_MSG_QUESTION_10')}",
            f"{localisation.get('SHARE_TUNE_MSG_QUESTION_11')}",
            f"{localisation.get('SHARE_TUNE_MSG_QUESTION_12')}",
            f"{localisation.get('SHARE_TUNE_MSG_QUESTION_13')}",
            f"{localisation.get('SHARE_TUNE_MSG_QUESTION_14')}",
            f"{localisation.get('SHARE_TUNE_MSG_QUESTION_15')}"
        ]

        user_answers = {}
        noq = 0

        for idx, question in enumerate(questions):
            valid = False
            while valid == False:
                await interaction.user.send(question)
                response = await self.bot.wait_for('message', check=lambda m: m.author == interaction.user)
                if response.content.upper() == "CANCEL":
                    return log
                logger.info(f"{header}{idx}: {response.content}")
                log += f"\n{header}{idx}: {response.content}"
                input, valid = await self.validate_input(response.content, interaction.user, idx, None)
                if valid == True:
                    user_answers[noq] = input
                    noq = noq + 1
                    logger.info(f"{header}{user_answers}")
                    log += f"{header}{user_answers}"
                    await asyncio.sleep(0.1)

                    if 2 <= idx <= 8:
                        fitted_stages = int(input)
                        sub_questions = await self.sub_questions_gen(idx)
                        for index, sub_question in enumerate(sub_questions):
                            valid = False
                            while valid == False:
                                if active_submissions[interaction.user.id]["Fusions"] == 1:
                                    input = "All"
                                    valid = True
                                elif (active_submissions[interaction.user.id]["Fusions"] == 2 or index >= fitted_stages):
                                    input = "0"
                                    valid = True
                                else:
                                    await interaction.user.send(sub_question)
                                    response = await self.bot.wait_for('message', check=lambda m: m.author == interaction.user)
                                    if response.content.upper() == "CANCEL":
                                        await interaction.user.send(f"{localisation.get('SHARE_TUNE_MSG_LOOP_STOP')} </{localisation.get('SHARE_TUNE_CMD_NAME')}:{helpers.load_json_key('session', 'CSR2_SHARE_TUNE_CMD')}>")
                                        active_submissions.pop(interaction.user.id, None)
                                        logger.info(f"{header}{localisation.get('SHARE_TUNE_LOG_CANCELED')}")
                                        log += f"\n{header}{localisation.get('SHARE_TUNE_LOG_CANCELED')}"
                                        await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
                                    logger.info(f"{index}: {response.content}")
                                    log += f"\n{index}: {response.content}"
                                    input, valid = await self.validate_input(response.content, interaction.user, None, index)
                                if valid == True:
                                    user_answers[noq] = input
                                    noq = noq + 1
                                    logger.info(f"{user_answers}")
                                    log += f"\n{user_answers}"
                                    await asyncio.sleep(0.1)
        log += f"\n{user_answers}"

        await interaction.user.send(f"{localisation.get('SHARE_TUNE_MSG_SUCCESS')}")

        dbn = active_submissions[interaction.user.id]["Car"][1][0]
        ign = active_submissions[interaction.user.id]["Car"][1][1]
        tier = active_submissions[interaction.user.id]["Car"][1][2]
        stars = active_submissions[interaction.user.id]["Car"][1][3]
        user_name = interaction.user.display_name
        user_id = interaction.user.id

        tune_id, log = await tunes_manager.add_entry(dbn, ign, tier, stars, user_answers.get(0), user_answers.get(1), user_answers.get(2), user_answers.get(3), user_answers.get(4), user_answers.get(5), user_answers.get(6), user_answers.get(7), user_answers.get(8), user_answers.get(9), user_answers.get(10), user_answers.get(11), user_answers.get(12), user_answers.get(13), user_answers.get(14), user_answers.get(15), user_answers.get(16), user_answers.get(17), user_answers.get(18), user_answers.get(19), user_answers.get(20), user_answers.get(21), user_answers.get(22), user_answers.get(23), user_answers.get(24), user_answers.get(25), user_answers.get(26), user_answers.get(27), user_answers.get(28), user_answers.get(29), user_answers.get(30), user_answers.get(31), user_answers.get(32), user_answers.get(33), user_answers.get(34), user_answers.get(35), user_answers.get(36), user_answers.get(37), user_answers.get(38), user_answers.get(39), user_answers.get(40), user_answers.get(41), user_answers.get(42), user_answers.get(43), user_answers.get(44), user_answers.get(45), user_answers.get(46), user_answers.get(47), user_answers.get(48), user_answers.get(49), user_answers.get(50), user_answers.get(51), user_answers.get(52), user_answers.get(53), user_answers.get(54), user_answers.get(55), user_answers.get(56), user_name, user_id, log)
        await interaction.user.send(f"{localisation.get('SHARE_TUNE_MSG_TUNE_ID_1')} **{tune_id}**\n{localisation.get('SHARE_TUNE_MSG_TUNE_ID_2')}")
        results = await tunes_manager.query_tune(car = None, tune_id = tune_id, tier = None, rarity = None, purpose = None, creator = None)

        active_submissions.pop(interaction.user.id, None)
        messages, log = await communitytune.create_embeds(results, log)
        await communitytune.send_dms(interaction, messages, log)
        await in_app_logging.send_log(self.bot, log, 2, 1, interaction)

    async def get_car_chunks(self):
        cars = await tunes_manager.pull_available_cars()
        cars_with_index = [(i+1, car) for i, car in enumerate(cars)]
        chunks = [cars_with_index[i:i + 20] for i in range(0, len(cars_with_index), 20)]
        return chunks

    async def get_selection_page(self, page: int):
        embed = discord.Embed(
            title=f"{localisation.get('SHARE_TUNE_MSG_EMBED_TITLE')}",
            description="\n".join([f"{idx + 1}. {car[1][1]} ({await helpers.emojify_tier(car[1][2])} {await helpers.emojify_rarity(car[1][3])})" for idx, car in enumerate(active_submissions["Chunks"][page])]),
            color=discord.Color(0xff00ff)
        )
        embed.set_footer(text=f"{localisation.get('MSG_EMBED_DESC_PAGE')} {page + 1} {localisation.get('MSG_EMBED_DESC_OF')} {len(active_submissions["Chunks"])}")
        embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')
        return embed

    async def sub_questions_gen(self, part_counter: int):
        parts = [
            f"{localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_ENGINE_MOTOR')}",
            f"{localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_TURBO_BATTERY')}",
            f"{localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_INTAKE_INVERTER')}",
            f"{localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_NITROUS_OVERBOOST')}",
            f"{localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_BODY')}",
            f"{localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_TIRES')}",
            f"{localisation.get('COMMUNITY_TUNE_MSG_EMBED_DESC_TRANSMISSION')}"
        ]
        sub_questions = [
            f"{localisation.get('SHARE_TUNE_MSG_SUB_QUESTION')} 1  {parts[part_counter-2]}",
            f"{localisation.get('SHARE_TUNE_MSG_SUB_QUESTION')} 2  {parts[part_counter-2]}",
            f"{localisation.get('SHARE_TUNE_MSG_SUB_QUESTION')} 3  {parts[part_counter-2]}",
            f"{localisation.get('SHARE_TUNE_MSG_SUB_QUESTION')} 4  {parts[part_counter-2]}",
            f"{localisation.get('SHARE_TUNE_MSG_SUB_QUESTION')} 5  {parts[part_counter-2]}",
            f"{localisation.get('SHARE_TUNE_MSG_SUB_QUESTION')} 6  {parts[part_counter-2]}",
        ]
        return sub_questions

    async def validate_input(self, response: str, user: discord.User, idx: int, index: int):
        if idx is not None:
            if idx < 2:
                if response.isdigit():
                    valid = True
                else:
                    valid = False
                    await user.send(f"{localisation.get('SHARE_TUNE_MSG_WARNING_NO_INTEGER')}")
            elif 2 <= idx <= 8:
                if (response.isdigit() and 0 <= int(response) <= 6):
                    valid = True
                else:
                    valid = False
                    await user.send(f"{localisation.get('SHARE_TUNE_MSG_WARNING_NO_INT_0_6')}")
            elif 9 <= idx <= 12:
                if response.lower() == "none":
                    response = None
                valid = True
            elif 13 <= idx <= 14:
                valid = True
        elif index is not None:
            if (response.isdigit() and 0 <= int(response) <= 5):
                valid = True
            else:
                valid = False
                await user.send(f"{localisation.get('SHARE_TUNE_MSG_WARNING_NO_INT_0_5')}")
        else:
            valid = False
            await user.send(f"{localisation.get('SHARE_TUNE_MSG_WARNING_INVALID')}")
        return response, valid

    class CarSelectionButtons(ui.View):
        def __init__(self, chunk: list, user: int, bot, cog):
            super().__init__()
            self.chunk = chunk
            self.user = user
            self.bot = bot
            self.cog = cog

            for idx, car in enumerate(self.chunk):
                self.add_item(ShareTuneCog.CarButton(idx+1, car, bot, cog, user))
            self.add_item(ShareTuneCog.NavigationButton("Previous", -1, bot, cog, user))
            self.add_item(ShareTuneCog.NavigationButton("Next", 1, bot, cog, user))
            self.add_item(ShareTuneCog.JumpToPageButton(self, bot, cog, user))

        async def on_timeout(self):
            global log
            for msg in active_submissions[self.user]["Messages"].values():
                try:
                    await msg.delete()
                except Exception as e:
                    logger.info(f"{localisation.get('LOG_ERROR_FETCH')} {e}")
                    log += f"{localisation.get('LOG_ERROR_FETCH')} {e}"

    class CarButton(ui.Button):
        def __init__(self, index, car, bot, cog, user_id):
            super().__init__(label=str(index), style=discord.ButtonStyle.primary)
            self.index = index
            self.car = car
            self.bot = bot
            self.cog = cog
            self.user_id = user_id

        async def callback(self, interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True)
            global log
            logger.info(f"{localisation.get('SHARE_TUNE_LOG_CAR_SELECTED')}")
            log += f"{localisation.get('SHARE_TUNE_LOG_CAR_SELECTED')}"
            if interaction.message.id == active_submissions[interaction.user.id]["Messages"]["SelectionMessage"].id:
                selection_message = f"{localisation.get('SHARE_TUNE_MSG_CONFIRM_1')} {self.car[1][1]} ({localisation.get('SHARE_TUNE_MSG_CONFIRM_2')} {self.car[1][2]}, {localisation.get('SHARE_TUNE_MSG_CONFIRM_3')} {self.car[1][3]})\n\n{localisation.get('SHARE_TUNE_MSG_CONFIRM_4')}"
                interaction.followup.edit_message(view=self)
                Buttons = ShareTuneCog.CarConfirmButtons(self.car, self.bot, self.cog, self.user_id)
                msg = await interaction.followup.send(selection_message, view=Buttons)
                active_submissions[interaction.user.id]["Messages"]["ConfirmationMessage"] = msg

    class NavigationButton(ui.Button):
        def __init__(self, label, direction, bot, cog, user_id):
            super().__init__(label=label, style=discord.ButtonStyle.secondary)
            self.label = label
            self.direction = direction
            self.bot = bot
            self.cog = cog
            self.user_id = user_id

        async def callback(self, interaction):
            await interaction.response.defer(ephemeral=True)
            active_submissions[interaction.user.id]["SelectionPage"] = (active_submissions[interaction.user.id]["SelectionPage"] + self.direction) % len(active_submissions["Chunks"])
            selection_page = await self.cog.get_selection_page(page = active_submissions[interaction.user.id]["SelectionPage"])
            Buttons = ShareTuneCog.CarSelectionButtons(active_submissions["Chunks"][active_submissions[interaction.user.id]["SelectionPage"]], interaction.user.id, self.view.bot, self.view.cog)
            await active_submissions[interaction.user.id]["Messages"]["SelectionMessage"].edit(embed=selection_page, view=Buttons)

    class JumpToPageButton(ui.Button):
        def __init__(self, view, bot, cog, user_id):
            super().__init__(label=bot.localisation.get("MSG_BUTTON_JUMP_TO_PAGE"), style=discord.ButtonStyle.secondary)
            self._view = view
            self.bot = bot
            self.cog = cog
            self.user_id = user_id

        @property
        def view(self):
            return self._view

        async def callback(self, interaction: discord.Interaction):
            if interaction.message.id != active_submissions[interaction.user.id]["Messages"]["SelectionMessage"].id:
                return await interaction.response.send_message(localisation.get("MSG_NO_PERMISSION"), ephemeral=True)
            else:
                await interaction.response.send_modal(ShareTuneCog.PageJumpModal(self.view, self.bot, self.cog, interaction.user.id))


    class PageJumpModal(discord.ui.Modal):
        def __init__(self, view: "ShareTuneCog.CarSelectionButtons", bot, cog, user_id):
            super().__init__(title=bot.localisation.get("MSG_BUTTON_JUMP_TO_PAGE"))
            self.view = view
            self.bot = bot
            self.cog = cog
            self.user_id = user_id

            self.page_number = discord.ui.TextInput(label=localisation.get("MSG_MODAL_JUMP_TO_PAGE"), required=True)
            self.add_item(self.page_number)

        async def on_submit(self, interaction):
            await interaction.response.defer()
            try:
                input_text = self.page_number.value.strip()

                if input_text.startswith(('+', '-')):
                    offset = int(input_text)
                    active_submissions[interaction.user.id]["SelectionPage"] = (
                        active_submissions[interaction.user.id]["SelectionPage"] + offset
                    ) % len(active_submissions["Chunks"])
                    if active_submissions[interaction.user.id]["SelectionPage"] == -1:
                        active_submissions[interaction.user.id]["SelectionPage"] = len(active_submissions["Chunks"])
                else:
                    page_number = int(input_text) - 1
                    active_submissions[interaction.user.id]["SelectionPage"] = page_number % len(active_submissions["Chunks"])
                    if (
                        active_submissions[interaction.user.id]["SelectionPage"] < 1
                        or active_submissions[interaction.user.id]["SelectionPage"] > len(active_submissions["Chunks"])
                    ):
                        active_submissions[interaction.user.id]["SelectionPage"] = (
                            (active_submissions[interaction.user.id]["SelectionPage"] - 1)
                            % len(active_submissions["Chunks"])
                        ) + 1

                selection_page = await self.view.cog.get_selection_page(page=active_submissions[interaction.user.id]["SelectionPage"])
                Buttons = ShareTuneCog.CarSelectionButtons(
                    active_submissions["Chunks"][active_submissions[interaction.user.id]["SelectionPage"]], interaction.user.id, self.view.bot, self.view.cog)
                await active_submissions[interaction.user.id]["Messages"]["SelectionMessage"].edit(embed=selection_page, view=Buttons)
            except ValueError:
                await interaction.response.send_message(localisation.get("MSG_JUMP_INVALID"), ephemeral=True)

    class CarConfirmButtons(ui.View):
        def __init__(self, car: list, bot, cog, user_id):
            super().__init__()
            self.car = car
            self.bot = bot
            self.cog = cog
            self.user_id = user_id

            self.add_item(ShareTuneCog.ConfirmButton(car, bot, cog, user_id))
            self.add_item(ShareTuneCog.DeclineButton(bot, cog, user_id))

    class ConfirmButton(ui.Button):
        def __init__(self, car, bot, cog, user_id):
            super().__init__(label="✅", style=discord.ButtonStyle.success)
            self.car = car
            self.bot = bot
            self.cog = cog
            self.user_id = user_id

        async def callback(self, interaction: discord.Interaction):
            global log
            logger.info(f"{localisation.get('SHARE_TUNE_LOG_CAR_CONFIRMED')}")
            log += f"{localisation.get('SHARE_TUNE_LOG_CAR_CONFIRMED')}"
            await interaction.response.edit_message(content=f"{localisation.get('SHARE_TUNE_MSG_SELECT_CONFIRMED')}", view=self)
            if interaction.message.id == active_submissions[interaction.user.id]["Messages"]["ConfirmationMessage"].id:
                active_submissions[interaction.user.id]["Car"] = self.car
                cog = interaction.client.get_cog("ShareTuneCog")
                await cog.submission_loop(interaction)

    class DeclineButton(ui.Button):
        def __init__(self, bot, cog, user_id):
            super().__init__(label="❌", style=discord.ButtonStyle.danger)
            self.bot = bot
            self.cog = cog
            self.user_id = user_id

        async def callback(self, interaction: discord.Interaction):
            global log
            logger.info(f"{localisation.get('SHARE_TUNE_LOG_CAR_DECLINED')}")
            header = localisation.get('SHARE_TUNE_LOG_HEADER')
            if interaction.message.id == active_submissions[interaction.user.id]["Messages"]["ConfirmationMessage"].id:
                await interaction.response.send_message(f"{localisation.get('SHARE_TUNE_MSG_LOOP_STOP')} </{localisation.get('SHARE_TUNE_CMD_NAME')}:{helpers.load_json_key('session', 'CSR2_SHARE_TUNE_CMD')}>")
                for msg in active_submissions[self.user_id]["Messages"].values():
                    try:
                        await msg.delete()
                    except Exception as e:
                        logger.info(f"{header}{localisation.get('LOG_ERROR_FETCH')} {e}")
                        log += f"{header}{localisation.get('LOG_ERROR_FETCH')} {e}"

async def setup(bot):
    await bot.add_cog(ShareTuneCog(bot))
