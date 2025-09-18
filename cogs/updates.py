import discord
from discord.ext import commands
from discord import app_commands
import in_app_logging
import helpers

logger = helpers.load_logging()
localisation = dict(helpers.load_localisation())

class UpdatesCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name=localisation.get('UPDATES_CMD_NAME'), description=localisation.get('UPDATES_CMD_DESC'))
    async def updates(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            header = localisation.get('UPDATES_LOG_HEADER')
            logger.info(f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('UPDATES_CMD_NAME')}")
            log = f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('UPDATES_CMD_NAME')}"

            results, log = await self.fetch_all_results(log)
            logger.info(f"{header}{len(results)} {localisation.get('LOG_RESULTS_FOUND')}")
            log += f"\n{header}{len(results)} {localisation.get('LOG_RESULTS_FOUND')}"

            if results:
                view = self.PaginatedView(results, interaction.user, self.bot, self)
                await view.start(interaction)
            else:
                logger.info(f"{header}{localisation.get('LOG_NO_RESULTS')}")
                log += f"\n{header}{localisation.get('LOG_NO_RESULTS')}"
                await interaction.followup.send(f"{localisation.get('LOG_NO_RESULTS')}", ephemeral=True)
                await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
        except Exception as e:
            await interaction.followup.send(f"{localisation.get('MSG_ERROR_FETCH')} {e}")
            logger.info(f"{localisation.get('LOG_ERROR_FETCH')} {e}")
            log += f"{localisation.get('LOG_ERROR_FETCH')} {e}"
            await in_app_logging.send_log(self.bot, log, 0, 1, interaction)

    async def fetch_all_results(self, log: str):
        header = localisation.get('UPDATES_LOG_HEADER')
        query = """\nSELECT "Date", "Output Vision"\nFROM updates\nORDER BY "ID" ASC"""
        logger.info(f"{header}{localisation.get('INFO_LOG_QUERY')} {query}")
        log += f"\n{header}{localisation.get('INFO_LOG_QUERY')} ```sql{query}```"
        results = await helpers.execute_sql_statement("WRs", query)
        return results, log

    class PageJumpModal(discord.ui.Modal, title="Jump to Page"):
        page_number = discord.ui.TextInput(label="Enter Page Number or +/- for an offset", required=True)

        def __init__(self, view: "UpdatesCog.PaginatedView"):
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
                await interaction.response.send_message(f"{self.view.bot.localisation.get('MSG_JUMP_INVALID')}", ephemeral=True)

    class PaginatedView(discord.ui.View):
        def __init__(self, results: list, user: discord.User, bot: commands.Bot, cog: commands.Cog):
            super().__init__(timeout=300)
            self.results = results
            self.user = user
            self.bot = bot
            self.cog = cog
            self.page_number = 1
            self.max_pages = len(results) // 25 + (1 if len(results) % 25 != 0 else 0)
            self.previous_button.label = localisation.get('MSG_BUTTON_PREVIOUS')
            self.next_button.label = localisation.get('MSG_BUTTON_NEXT')
            self.jump_button.label = localisation.get('MSG_BUTTON_JUMP_TO_PAGE')

        async def get_embed_page(self):
            header = localisation.get('UPDATES_LOG_HEADER')
            start_index = (self.page_number - 1) * 25
            end_index = start_index + 25
            page_results = self.results[start_index:end_index]

            logger.info(f"{header}{localisation.get('WRLIST_LOG_EMBED_PAGE')} {self.page_number}")
            embed = discord.Embed(
                title=f"{localisation.get('UPDATES_MSG_EMBED_TITLE')}",
                description="\n".join(
                    f"{row[0][:10]} - {row[1]}"
                    for row in page_results
                ),
                color=discord.Color(0xff00ff)
            )
            embed.set_footer(text=f"{localisation.get('MSG_EMBED_DESC_PAGE')} {self.page_number} {localisation.get('MSG_EMBED_DESC_OF')} {self.max_pages}")
            embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')
            return embed

        async def start(self, interaction: discord.Interaction):
            header = localisation.get('UPDATES_LOG_HEADER')
            logger.info(f"{header}{localisation.get('LOG_EMBED_INITIAL')}")
            embed = await self.get_embed_page()
            self.message = await interaction.followup.send(embed=embed, view=self)

        @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary)
        async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            header = localisation.get('UPDATES_LOG_HEADER')
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
            header = localisation.get('UPDATES_LOG_HEADER')
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
            header = localisation.get('UPDATES_LOG_HEADER')
            logger.info(f"{header}{localisation.get('UPDATES_LOG_TIMEOUT')}")
            for child in self.children:
                child.disabled = True
            if hasattr(self, "message"):
                await self.message.edit(view=self)
            self.stop()

async def setup(bot):
    await bot.add_cog(UpdatesCog(bot))