import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
import os
import csv
import os
import asyncio
import logging
import in_app_logging
import helpers

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()
TOKEN = helpers.load_token()
CLIENT_ID = helpers.load_client_id()
NITRO = helpers.load_super_admin()

class ForumCollector(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_nitro(interaction: discord.Interaction):
        return int(interaction.user.id) == int(NITRO)

    @app_commands.command(name="csr2_collect_forum_data", description="[Admin Command] Collect all posts in a forum channel with their tags and save to a CSV file.")
    @app_commands.check(is_nitro)
    @app_commands.describe(channel="The forum channel to collect posts from.")
    async def collect_forum_posts(self, interaction: discord.Interaction, channel: discord.ForumChannel):
        logger.info(f"The following command has been used: /csr2_collect_forum_data")
        log = f"The following command has been used: /csr2_collect_forum_data"
        # Defer the interaction response to give more time to process
        await interaction.response.defer(ephemeral=True)

        if int(interaction.user.id) == int(NITRO):
        
            # Collect posts and tags from the specified forum channel
            posts_data = []

            # Fetch and unarchive archived threads
            async for thread in channel.archived_threads(limit=None):
                await self.process_thread(thread, posts_data)

            # Fetch active threads
            for thread in channel.threads:
                await self.process_thread(thread, posts_data)

            # Define CSV file path
            csv_file_path = os.path.join(os.getcwd(), 'resources/forum_data.csv')

            # Write collected data to CSV file
            try:
                with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['thread_id', 'thread_title', 'tags']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                    writer.writeheader()
                    for post_data in posts_data:
                        writer.writerow(post_data)

                await interaction.followup.send(f"Collected {len(posts_data)} threads from {channel.name} and saved to {csv_file_path}.", ephemeral=True)
            except Exception as e:
                await interaction.followup.send(f"An error occurred while writing to the CSV file: {e}", ephemeral=True)
            log += f"\nUser is NITRO"
        else:
            await interaction.followup.send(f"You don't have permission to run this command", ephemeral=True)
            log += f"\nUser is not NITRO"
        await in_app_logging.send_log(self.bot, log, interaction)

    @collect_forum_posts.error
    async def collect_forum_posts_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)

    async def process_thread(self, thread, posts_data):
        if thread.archived:
            try:
                await thread.edit(archived=False)
                await asyncio.sleep(1)  # Slight delay to handle rate limiting
            except discord.errors.HTTPException as e:
                if e.status == 429:  # Rate limit exceeded
                    retry_after = int(e.response.headers.get("Retry-After", 1))
                    await asyncio.sleep(retry_after)

        # Extract and format tags for each thread
        tags = [tag.name for tag in thread.applied_tags]  # Extract tag names
        tags_str = ', '.join(tags) if tags else 'N/A'  # Join tag names into a string

        # Collect relevant data for each thread
        posts_data.append({
            'thread_id': thread.id,
            'thread_title': thread.name,
            'tags': tags_str  # Include tags as a string
        })

        # Re-archive the thread
        try:
            await thread.edit(archived=True)
            await asyncio.sleep(1)  # Slight delay to handle rate limiting
        except discord.errors.HTTPException as e:
            if e.status == 429:  # Rate limit exceeded
                retry_after = int(e.response.headers.get("Retry-After", 1))
                await asyncio.sleep(retry_after)

async def setup(bot):
    await bot.add_cog(ForumCollector(bot))
