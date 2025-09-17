import asyncio
import discord
from discord.ext import commands
from discord import app_commands
import helpers
import in_app_logging

logger = helpers.load_logging()
localisation = dict(helpers.load_localisation())

class BroadcastCommandCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name=localisation.get('BROADCAST_CMD_NAME'), description=localisation.get('BROADCAST_CMD_DESC'))
    @app_commands.describe(message_title=localisation.get('BROADCAST_CMD_MESSAGE_TITLE'))
    async def broadcast(self, interaction: discord.Interaction, message_title: str):
        await interaction.response.defer(ephemeral=True)
        try:
            header = localisation.get('BROADCAST_LOG_HEADER')
            logger.info(f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('BROADCAST_CMD_NAME')} message_title: {message_title}")
            log = f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('BROADCAST_CMD_NAME')} message_title: {message_title}"

            await interaction.followup.send(f"{localisation.get('BROADCAST_MSG_SEND_MESSAGE_BODY')}", ephemeral=True)

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

            logger.info(f"{header} {len(all_moderators)} {localisation.get('BROADCAST_LOG_MODERATOR_COUNT_DETECTED')}")
            log += f"\n{header} {len(all_moderators)} {localisation.get('BROADCAST_LOG_MODERATOR_COUNT_DETECTED')}"

            sent = 0
            for moderator in all_moderators:
                try:
                    await moderator.send(embed=embed)
                    sent = sent + 1
                    await asyncio.sleep(1)
                except Exception as e:
                    logger.warning(f"{header}{localisation.get('BROADCAST_LOG_MESSAGE_FAIL_BLOCK')} {moderator}: {e}")

            await interaction.followup.send(f"{sent} {localisation.get('BROADCAST_MSG_SUMMARY')}", ephemeral=True)
            logger.info(f"{header}{localisation.get('BROADCAST_LOG_DONE')}")
            log += f"\n{header}{localisation.get('BROADCAST_LOG_DONE')}"
            await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
        except Exception as e:
            await interaction.followup.send(f"{localisation.get('MSG_ERROR_FETCH')} {e}", ephemeral=True)
            logger.info(f"{localisation.get('LOG_ERROR_FETCH')} {e}")
            log += f"{localisation.get('LOG_ERROR_FETCH')} {e}"
            await in_app_logging.send_log(self.bot, log, 0, 1, interaction)

async def setup(bot):
    ADMIN_SERVERS = await helpers.load_json_key("config", "ClientAdminServers")
    for server in ADMIN_SERVERS:
        await bot.add_cog(BroadcastCommandCog(bot), guilds=[discord.Object(id=int(server))], override=True)
