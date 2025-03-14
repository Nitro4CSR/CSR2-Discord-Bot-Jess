import discord
from discord.ext import commands
import json
import helpers

logger = helpers.load_logging()

async def send_log(bot: commands.Bot, log: str, status: int, type: int, interaction: discord.Interaction = None):
    await bot.wait_until_ready()
    CHANNEL = json.loads(await helpers.load_log_channels())
    NITRO = await helpers.load_super_admin()
    log_channel = bot.get_channel(CHANNEL[type-1])

    if status == 0:
        log += f"\n\n<@{NITRO}>"

    embed = await log_type_to_embed(log, status, type, interaction)
    try:
        await log_channel.send(embed=embed)
    except Exception as e:
        logger.error(f"{e}")

async def log_type_to_embed(log: str, status: int, type: int, interaction: discord.Interaction):
    conversion = {
        None: f"", # Debug
        1: await construct_command_log(log, status, interaction), # Commands
        2: await construct_task_log(log, status), # Scheduled Tasks
    }

    embed = conversion.get(type)

    return embed

async def get_status(status: int):
    conversion = {
        None: f"", # Debug
        0: 0xff0000, # Error
        1: 0xff7d00, # Warning
        2: 0x00ff00 # Success
    }
    color = discord.Color(conversion.get(status))

    return color

async def construct_command_log(log: str, status: int, interaction: discord.Interaction):
    if (interaction and interaction.guild):
        log += f"\n\n-# {interaction.guild.name} ({interaction.guild.id})"
    color = await get_status(status)
    embed = discord.Embed(
        title="A command was executed!",
        description=f"{log}",
        color=color
    )
    if interaction:
        embed.set_footer(text=f"{interaction.user.global_name} ({interaction.user.display_name} ({interaction.user.name}) [{interaction.user.id}])")

    return embed

async def construct_task_log(log: str, status: int):
    color = await get_status(status)
    embed = discord.Embed(
        title="A scheduled task was executed!",
        description=f"{log}",
        color=color
    )

    return embed
