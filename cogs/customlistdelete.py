import discord
from discord.ext import commands
from discord import app_commands
import helpers
import in_app_logging

logger = helpers.load_logging()
localisation = dict(helpers.load_localisation())

class CustomListDeleteCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name=localisation.get('CUSTOMLIST_DELETE_CMD_NAME'), description=localisation.get('CUSTOMLIST_DELETE_CMD_DESC'))
    @app_commands.describe(list_id=localisation.get('CUSTOMLIST_ANY_CMD_LIST_ID'), global_list=localisation.get('CUSTOMLIST_ANY_CMD_GLOBAL_LIST'))
    @app_commands.choices(global_list=[app_commands.Choice(name=localisation.get('CUSTOMLIST_ANY_CMD_GLOBAL_LIST_OPTION_TRUE'), value=1), app_commands.Choice(name=localisation.get('CUSTOMLIST_ANY_CMD_GLOBAL_LIST_OPTION_FALSE'), value=0)])
    async def customlistdelete(self, interaction: discord.Interaction, list_id: int, global_list: int = None):
        await interaction.response.defer()
        try:
            header = localisation.get('CUSTOMLIST_DELETE_LOG_HEADER')
            logger.info(f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('CUSTOMLIST_DELETE_CMD_NAME')} list_id: {list_id} global_list: {global_list}")
            log = f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('CUSTOMLIST_DELETE_CMD_NAME')} list_id: {list_id} global_list: {global_list}"

            if global_list is None:
                global_list = 0 if interaction.guild else 1

            if interaction.guild:
                if global_list:
                    if str(interaction.user.id) not in await helpers.load_json_key("config", "ClientAdminIDs") and str(interaction.user.id) not in await helpers.load_file("global_list_admins"):
                        await interaction.followup.send(f"{localisation.get('CUSTOM_LISTS_MSG_WARNING_NO_PERMISSION_GLOBAL')}", ephemeral=True)
                        await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
                        return
                else:
                    if str(interaction.user.id) not in await helpers.load_json_key("config", "ClientAdminIDs") and not interaction.user.guild_permissions.administrator:
                        await interaction.followup.send(f"{localisation.get('CUSTOM_LISTS_MSG_WARNING_NO_PERMISSION_SERVER')}", ephemeral=True)
                        await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
                        return
            else:
                if global_list:
                    if str(interaction.user.id) not in await helpers.load_json_key("config", "ClientAdminIDs") and str(interaction.user.id) not in await helpers.load_file("global_list_admins"):
                        await interaction.followup.send(f"{localisation.get('CUSTOM_LISTS_MSG_WARNING_NO_PERMISSION_GLOBAL')}", ephemeral=True)
                        await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
                        return
                    else:
                        await interaction.followup.send(f"{localisation.get('CUSTOM_LISTS_MSG_WARNING_NO_SERVER')}", ephemeral=True)
                        await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
                        return

            custom_lists = dict(await helpers.load_file("custom_lists"))
            server_id = "GLOBAL" if global_list else str(interaction.guild.id)
            if server_id in custom_lists.keys():
                custom_lists[server_id].pop(str(list_id).zfill(3), None)
            await helpers.save_file("custom_lists", custom_lists)

            embed = discord.Embed(
                title=localisation.get('CUSTOMLIST_DELETE_MSG_EMBED_TITLE'),
                description=f"{localisation.get('CUSTOMLIST_DELETE_MSG_EMBED_DESC')}: {str(list_id).zfill(3)}",
                color=discord.Color(0xff00ff)
            )
            embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')
            await interaction.followup.send(embed=embed, ephemeral=True)
            await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
        except Exception as e:
            await interaction.followup.send(f"{localisation.get('MSG_ERROR_FETCH')} {e}", ephemeral=True)
            logger.info(f"{localisation.get('LOG_ERROR_FETCH')} {e}")
            log += f"\n{localisation.get('LOG_ERROR_FETCH')} {e}"
            await in_app_logging.send_log(self.bot, log, 0, 1, interaction)

async def setup(bot):
    await bot.add_cog(CustomListDeleteCog(bot))