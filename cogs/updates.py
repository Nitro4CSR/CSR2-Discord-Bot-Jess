import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import logging
import in_app_logging
import helpers

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UpdatesCommandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="csr2_updates", description="Lists all changes made to the DB")
    async def wrlist_command(self, interaction: discord.Interaction):
        logger.info(f"The following command has been used: /csr2_updates")
        log = f"The following command has been used: /csr2_updates"
        await interaction.response.defer()
        
        # Fetch results
        results, log = await self.fetch_all_results(interaction, log)
        logger.info(f"{len(results)} results found")
        log += f"\n{len(results)} results found"
        
        if results:
            view = PaginatedView(results, interaction.user)
            await view.start(interaction)
            await in_app_logging.send_log(self.bot, log, interaction)
        else:
            logger.info(f"Sending message...")
            log += f"\nSending message..."
            await interaction.followup.send("No results found.")
            await in_app_logging.send_log(self.bot, log, interaction)

    async def fetch_all_results(self, interaction: discord.Interaction, log: str):
        # Connect to the database
        DATABASE_PATH = helpers.load_external_db()
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        query = """\nSELECT "Date", "Output Vision"\nFROM updates\nORDER BY "ID" ASC"""

        logger.info(f"The following query has been used: {query}")
        log += f"\nThe following query has been used: {query}"

        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            logger.info(f"Fetched {len(rows)} rows from the database.")
            log += f"\nFetched {len(rows)} rows from the database."
            return rows, log
        except sqlite3.OperationalError as e:
            logger.error(f"Database error occurred: {e}")
            log += f"\nDatabase error occurred: {e}"
            await interaction.followup.send(f"Database error occurred: {e}")
            await in_app_logging.send_log(self.bot, log, interaction)
            return []
        finally:
            conn.close()


class PaginatedView(discord.ui.View):
    def __init__(self, results, user):
        super().__init__(timeout=300)
        self.results = results
        self.user = user
        self.page_number = 1
        self.max_pages = len(results) // 10 + (1 if len(results) % 10 != 0 else 0)

    def get_embed_page(self):
        start_index = (self.page_number - 1) * 10
        end_index = start_index + 10
        page_results = self.results[start_index:end_index]

        logger.info(f"Constructing Embed for page {self.page_number}")
        embed = discord.Embed(
            title=f"Database Changes",
            description="\n".join(
                f"{row[0][:10]} - {row[1]}"  # Truncate row[0] to the first 10 characters
                for row in page_results
            ),
            color=discord.Color(0xff00ff)
        )
        embed.set_footer(text=f"Page {self.page_number} of {self.max_pages}")
        embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')
        return embed

    async def start(self, interaction: discord.Interaction):
        logger.info(f"Sending initial Embed with buttons")
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
        
        logger.info(f"Going to previous page: {self.page_number}")
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

        logger.info(f"Going to next page: {self.page_number}")
        embed = self.get_embed_page()
        await interaction.response.edit_message(embed=embed, view=self)

    async def on_timeout(self):
        logger.info("Button view timed out, disabling buttons.")
        for child in self.children:
            child.disabled = True
        # Assuming you keep a reference to the original message (e.g., `self.message`), you can edit it to disable buttons:
        await self.message.edit(view=self)


async def setup(bot):
    await bot.add_cog(UpdatesCommandCog(bot))
