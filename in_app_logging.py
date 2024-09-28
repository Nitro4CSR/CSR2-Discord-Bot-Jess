import discord
from discord.ext import commands
import logging
import helpers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load environment variables from .env file
CHANNEL = helpers.load_log_channel()

async def send_log(bot: commands.Bot, log: str, interaction: discord.Interaction):
    log_channel = bot.get_channel(int(CHANNEL))
    if interaction.guild is not None:
        log += f"\n\n-# {interaction.guild.name} ({interaction.guild.id})"
    embed = construct_log(log, interaction)
    try:
        await log_channel.send(embed=embed)
    except Exception as e:
        logging.error(f"{e}")

def construct_log(log: str, interaction: discord.Interaction):
    embed = discord.Embed(
        title="A command was executed!",
        description=f"{log}",
        color=discord.Color(0xff00ff)
    )
    embed.set_footer(text=f"{interaction.user.global_name} ({interaction.user.display_name} ({interaction.user.name}) [{interaction.user.id}])")
    return embed