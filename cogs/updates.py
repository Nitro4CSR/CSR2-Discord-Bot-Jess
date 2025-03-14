import discord
from discord.ext import commands
from discord import app_commands
import aiosqlite
import in_app_logging
import helpers

logger = helpers.load_logging()

class UpdatesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="csr2_updates", description="Lists all changes made to the DB")
    async def wrlist_command(self, interaction: discord.Interaction):
        logger.info(f"UPDATES - The following command has been used: /csr2_updates")
        log = f"UPDATES - The following command has been used: /csr2_updates"
        await interaction.response.defer()

        results, log = await fetch_all_results(self.bot, interaction, log)
        logger.info(f"UPDATES - {len(results)} results found")
        log += f"\nUPDATES - {len(results)} results found"

        if results:
            view = PaginatedView(results, interaction.user)
            await view.start(interaction)
        else:
            logger.info(f"UPDATES - Sending message...")
            log += f"\nUPDATES - Sending message..."
            await interaction.followup.send("No results found.", ephemeral=True)
        await in_app_logging.send_log(self.bot, log, 2, 1, interaction)

async def fetch_all_results(bot: commands.Bot, interaction: discord.Interaction, log: str):
    DATABASE_PATH = await helpers.load_file_path('EDB')
    async with aiosqlite.connect(DATABASE_PATH) as conn:
        async with conn.cursor() as cursor:

            query = """\nSELECT "Date", "Output Vision"\nFROM updates\nORDER BY "ID" ASC"""
        
            logger.info(f"UPDATES - The following query has been used: {query}")
            log += f"\nUPDATES - The following query has been used: {query}"
        
            try:
                await cursor.execute(query)
                rows = await cursor.fetchall()
                logger.info(f"UPDATES - Fetched {len(rows)} rows from the database.")
                log += f"\nUPDATES - Fetched {len(rows)} rows from the database."
                return rows, log
            except aiosqlite.OperationalError as e:
                logger.error(f"UPDATES - Database error occurred: {e}")
                log += f"\nUPDATES - Database error occurred: {e}"
                await interaction.followup.send(f"Database error occurred: {e}")
                await in_app_logging.send_log(bot, log, 0, 1, interaction)
                return []

    await conn.close()

class PageJumpModal(discord.ui.Modal, title="Jump to Page"):
    page_number = discord.ui.TextInput(label="Enter Page Number or +/- Offset", required=True)

    def __init__(self, view: "PaginatedView"):
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
            await interaction.response.send_message("Invalid input. Please enter a number.", ephemeral=True)

class PaginatedView(discord.ui.View):
    def __init__(self, results, user):
        super().__init__(timeout=300)
        self.results = results
        self.user = user
        self.page_number = 1
        self.max_pages = len(results) // 25 + (1 if len(results) % 25 != 0 else 0)

    def get_embed_page(self):
        start_index = (self.page_number - 1) * 25
        end_index = start_index + 25
        page_results = self.results[start_index:end_index]

        logger.info(f"UPDATES - Constructing Embed for page {self.page_number}")
        embed = discord.Embed(
            title=f"Database Changes",
            description="\n".join(
                f"{row[0][:25]} - {row[1]}"
                for row in page_results
            ),
            color=discord.Color(0xff00ff)
        )
        embed.set_footer(text=f"Page {self.page_number} of {self.max_pages}")
        embed.set_thumbnail(url='https://imgur.com/1VWi2Di.png')
        return embed

    async def start(self, interaction: discord.Interaction):
        logger.info(f"UPDATES - Sending initial Embed with buttons")
        embed = self.get_embed_page()
        await interaction.followup.send(embed=embed, view=self)

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            await interaction.response.send_message("You can't interact with this button!", ephemeral=True)
            return

        self.page_number -= 1
        if self.page_number < 1:
            self.page_number = self.max_pages

        logger.info(f"UPDATES - Going to previous page: {self.page_number}")
        embed = self.get_embed_page()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            await interaction.response.send_message("You can't interact with this button!", ephemeral=True)
            return

        self.page_number += 1
        if self.page_number > self.max_pages:
            self.page_number = 1

        logger.info(f"UPDATES - Going to next page: {self.page_number}")
        embed = self.get_embed_page()
        await interaction.response.edit_message(embed=embed, view=self)

    async def on_timeout(self):
        logger.info("UPDATES - Button view timed out, disabling buttons.")
        for child in self.children:
            child.disabled = True
        await self.message.edit(view=self)

    @discord.ui.button(label="Jump to Page", style=discord.ButtonStyle.secondary)
    async def jump_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            return await interaction.response.send_message("You can't interact with this!", ephemeral=True)
        await interaction.response.send_modal(PageJumpModal(self))

    async def on_timeout(self):
        logger.info("UPDATES - Button view timed out, restarting pagination.")
        new_view = PaginatedView(self.results, self.user)
        embed = await new_view.get_embed_page()
        if self.message:
            await self.message.edit(embed=embed, view=new_view)
        self.stop()

async def setup(bot):
    await bot.add_cog(UpdatesCog(bot))
