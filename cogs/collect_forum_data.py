import discord
from discord import app_commands
from discord.ext import commands
import aiofiles
import os
import csv
import os
import asyncio
import in_app_logging
import helpers

logger = helpers.load_logging()

class CollectForumDataCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="csr2_collect_forum_data", description="[Admin Command] Collect all posts in a forum channel with their tags and save to a CSV file.")
    @app_commands.describe(channel="The forum channel to collect posts from.")
    async def collect_forum_posts(self, interaction: discord.Interaction, channel: discord.ForumChannel):
        logger.info(f"COLLECT_FORUM_DATA - The following command has been used: /csr2_collect_forum_data")
        log = f"COLLECT_FORUM_DATA - The following command has been used: /csr2_collect_forum_data"
        await interaction.response.defer(ephemeral=True)

        NITRO = await helpers.load_super_admin()
        if int(interaction.user.id) == int(NITRO):
            posts_data = []

            async for thread in channel.archived_threads(limit=None):
                await self.process_thread(thread, posts_data)

            for thread in channel.threads:
                await self.process_thread(thread, posts_data)

            csv_file_path = os.path.join(os.getcwd(), 'resources/forum_data.csv')

            try:
                async with aiofiles.open(csv_file_path, mode='w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['thread_id', 'thread_title', 'tags']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                    writer.writeheader()
                    for post_data in posts_data:
                        writer.writerow(post_data)

                await interaction.followup.send(f"Collected {len(posts_data)} threads from {channel.name} and saved to {csv_file_path}.", ephemeral=True)
            except Exception as e:
                await interaction.followup.send(f"An error occurred while writing to the CSV file: {e}", ephemeral=True)
            log += f"\nCOLLECT_FORUM_DATA - User is NITRO"
        else:
            await interaction.followup.send(f"You don't have permission to run this command", ephemeral=True)
            log += f"\nCOLLECT_FORUM_DATA - User is not NITRO"
        await in_app_logging.send_log(self.bot, log, 2, 1, interaction)

    async def process_thread(self, thread, posts_data):
        if thread.archived:
            try:
                await thread.edit(archived=False)
                await asyncio.sleep(1)
            except discord.errors.HTTPException as e:
                if e.status == 429:
                    retry_after = int(e.response.headers.get("Retry-After", 1))
                    await asyncio.sleep(retry_after)

        tags = [tag.name for tag in thread.applied_tags]
        tags_str = ', '.join(tags) if tags else 'N/A'

        posts_data.append({
            'thread_id': thread.id,
            'thread_title': thread.name,
            'tags': tags_str
        })

        try:
            await thread.edit(archived=True)
        except discord.errors.HTTPException as e:
            if e.status == 429:
                retry_after = int(e.response.headers.get("Retry-After", 1))
                await asyncio.sleep(retry_after)

async def setup(bot):
    await bot.add_cog(CollectForumDataCog(bot))
