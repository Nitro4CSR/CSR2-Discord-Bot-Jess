import discord
from discord.ext import commands
from discord import app_commands
import in_app_logging
import helpers

logger = helpers.load_logging()

class ConnectedCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="csr2_connected", description="Get the amount of Servers this bot is used in")
    @app_commands.describe(mod="'y' if you want to see which servers exactly use the bot and not just the an integer for the amount of servers")
    async def connected(self, interaction: discord.Interaction, mod: str = None):
        logger.info(f"CONNECTED - The following command hs been used: /csr2_connected mod:{mod}")
        log = f"CONNECTED - The following command hs been used: /csr2_connected mod:{mod}"
        await interaction.response.defer(ephemeral=True)

        NITRO = await helpers.load_super_admin()
        if str(interaction.user.id) == NITRO:
            guildlist = []
            for guild in self.bot.guilds:
                guildlist.append(guild.name + ' (' + str(guild.id) + ')')
            try:
                embed = discord.Embed(
                    title="Connected Servers",
                    description=f"Jess is present on {str(len(self.bot.guilds))} Servers.",
                    color=discord.Color(0xff00ff)
                )
                embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')
                await interaction.followup.send(embed=embed)
                if mod == 'y':
                    embed = discord.Embed(
                        title=f"Connected Servers List",
                        description=f"{'\n'.join(guildlist)}",
                        color=discord.Color(0xff00ff)
                    )
                    embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')
                    await interaction.followup.send(embed=embed, ephemeral=True)
            except Exception as e:
                print(e)
            log += f"\nCONNECTED - User is NITRO"
        else:
            await interaction.followup.send(f"You don't have permission to run this command", ephemeral=True)
            log += f"\nCONNECTED - User is not NITRO"
        await in_app_logging.send_log(self.bot, log, 2, 1, interaction)

async def setup(bot):
    ADMIN_SERVER = await helpers.load_admin_server()
    await bot.add_cog(ConnectedCog(bot), guilds=[discord.Object(id=ADMIN_SERVER)], override=True)
