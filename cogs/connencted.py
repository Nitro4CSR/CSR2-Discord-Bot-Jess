import discord
from discord.ext import commands
from discord import app_commands
import in_app_logging
import helpers

logger = helpers.load_logging()
localisation = dict(helpers.load_localisation())

class ConnectedCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name=localisation.get('CONNECTED_CMD_NAME'), description=localisation.get('CONNECTED_CMD_DESC'))
    @app_commands.describe(mod=localisation.get('CONNECTED_CMD_MOD'))
    async def connected(self, interaction: discord.Interaction, mod: str = None):
        await interaction.response.defer(ephemeral=True)
        try:
            header = localisation.get('CONNECTED_LOG_HEADER')
            logger.info(f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('CONNECTED_CMD_NAME')} mod: {mod}")
            log = f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('CONNECTED_CMD_NAME')} mod: {mod}"
            if interaction.user.id in await helpers.load_json_key("config", "ClientAdminIDs"):
                guildlist = []
                for guild in self.bot.guilds:
                    guildlist.append(guild.name + ' (' + str(guild.id) + ')')
                embed = discord.Embed(
                    title=f"{localisation.get('CONNECTED_MSG_EMBED_TITLE')}",
                    description=f"{str(len(self.bot.guilds))} {localisation.get('CONNECTED_MSG_EMBED_DESC')}",
                    color=discord.Color(0xff00ff)
                )
                embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')
                await interaction.followup.send(embed=embed)
                if mod == 'y':
                    embed = discord.Embed(
                        title=f"{localisation.get('CONNECTED_MSG_EMBED_TITLE')}",
                        description=f"{'\n'.join(guildlist)}",
                        color=discord.Color(0xff00ff)
                    )
                    embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    logger.info(f"{header}{localisation.get('CLIENTADMIN_IS_ADMIN')}")
                log += f"\n{header}{localisation.get('CLIENTADMIN_IS_ADMIN')}"
            else:
                await interaction.followup.send(f"{localisation.get('ADMIN_MSG_NO_PERMISSION')}", ephemeral=True)
                logger.info(f"{header}{localisation.get('CLIENTADMIN_NOT_ADMIN')}")
                log += f"\n{header}{localisation.get('CLIENTADMIN_NOT_ADMIN')}"
            await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
        except Exception as e:
            await interaction.followup.send(f"{localisation.get('MSG_ERROR_FETCH')} {e}")
            logger.info(f"{localisation.get('LOG_ERROR_FETCH')} {e}")
            log += f"{localisation.get('LOG_ERROR_FETCH')} {e}"
            await in_app_logging.send_log(self.bot, log, 0, 1, interaction)

async def setup(bot):
    ADMIN_SERVERS = await helpers.load_json_key("config", "ClientAdminServers")
    for server in ADMIN_SERVERS:
        await bot.add_cog(ConnectedCog(bot), guilds=[discord.Object(id=int(server))], override=True)
