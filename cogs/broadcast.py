import asyncio
import discord
from discord.ext import commands
from discord import app_commands
import helpers
import in_app_logging

logger = helpers.load_logging()

class BroadcastCommandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="csr2_broadcast", description="Send a message to all moderators of joined servers")
    async def broadcast_command(self, interaction: discord.Interaction, message_title: str):
        logger.info(f"BROADCAST - The following command has been used: /csr2_broadcast message_title: {message_title}")
        log = f"BROADCAST - The following command has been used: /csr2_broadcast message_title: {message_title}"
        await interaction.response.defer(ephemeral=True)

        await interaction.followup.send("Please send the text you wanna broadcast to all server Administrators below.")

        response = await self.bot.wait_for('message', check=lambda m: m.author == interaction.user)
        embed = discord.Embed(
            title=message_title,
            description=response.content,
            color=discord.Color(0xff00ff)
        )
        embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')

        all_moderators = set()

        for guild in self.bot.guilds:
            moderators = {member for member in guild.members if member.guild_permissions.administrator and not member.bot}
            moderators.add(guild.owner)
            all_moderators.update(moderators)

        logger.info(f"BROADCAST - Detected {len(all_moderators)} unique moderators across all connected servers")
        log += f"\nBROADCAST - Detected {len(all_moderators)} unique moderators across all connected servers"

        for moderator in all_moderators:
            try:
                await moderator.send(embed=embed)
                await asyncio.sleep(1)
            except Exception as e:
                logger.warning(f"BROADCAST - Could not send message to {moderator} (DMs might be closed): {e}")

        await interaction.followup.send(f"Broadcast sent to {len(all_moderators)} unique moderators.", ephemeral=True)
        logger.info("BROADCAST - Broadcast sent")
        log += "\nBROADCAST - Broadcast sent"
        await in_app_logging.send_log(self.bot, log, 2, 1, interaction)

async def setup(bot):
    ADMIN_SERVER = await helpers.load_admin_server()
    await bot.add_cog(BroadcastCommandCog(bot), guilds=[discord.Object(id=int(ADMIN_SERVER))], override=True)
