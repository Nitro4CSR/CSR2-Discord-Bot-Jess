import discord
from discord.ext import commands
from discord import app_commands
import json
import random
import helpers
import in_app_logging

logger = helpers.load_logging()
localisation = dict(helpers.load_localisation())

class CustomListUploadCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name=localisation.get('CUSTOMLIST_UPLOAD_CMD_NAME'), description=localisation.get('CUSTOMLIST_UPLOAD_CMD_DESC'))
    @app_commands.describe(list_file=localisation.get('CUSTOMLIST_UPLOAD_CMD_LIST_FILE'), global_list=localisation.get('CUSTOMLIST_ANY_CMD_GLOBAL_LIST'))
    @app_commands.choices(global_list=[app_commands.Choice(name=localisation.get('CUSTOMLIST_ANY_CMD_GLOBAL_LIST_OPTION_TRUE'), value=1), app_commands.Choice(name=localisation.get('CUSTOMLIST_ANY_CMD_GLOBAL_LIST_OPTION_FALSE'), value=0)])
    async def customlistupload(self, interaction: discord.Interaction, list_file: discord.Attachment, global_list: int = None):
        await interaction.response.defer(ephemeral=True)
        try:
            header = localisation.get('CUSTOMLIST_UPLOAD_LOG_HEADER')
            logger.info(f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('CUSTOMLIST_UPLOAD_CMD_NAME')} list_file: {list_file.filename} global_list: {global_list}")
            log = f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('CUSTOMLIST_UPLOAD_CMD_NAME')} list_file: {list_file.filename} global_list: {global_list}"

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

            try:
                custom_list = dict(json.loads((await list_file.read()).decode("utf-8")))
            except:
                await interaction.followup.send(f"{localisation.get('CUSTOM_LISTS_MSG_WARNING_FILE_INVALID')}", ephemeral=True)
                await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
                return

            server_id = "GLOBAL" if global_list else f"{interaction.guild.id}"
            custom_lists = dict(await helpers.load_file("custom_lists"))
            while True:
                custom_list_id = str(random.randint(0, 999)).zfill(3)
                if custom_list_id not in custom_lists[server_id].keys():
                    break
            for group, cars in custom_list.items():
                if group != "Name":
                    for car in cars.copy():
                        if "*" in car:
                            querry = """\nSELECT "DB Name"\nFROM info\nWHERE "DB Name" LIKE ?"""
                            results = await helpers.execute_sql_statement("WRs", querry, [car.replace("*", "%")])
                            for result in list(results):
                                if result[0] not in list(cars):
                                    cars.append(result[0])
                            cars.remove(car)
                    cars = list(set(cars))
            custom_lists.setdefault(server_id, {})
            custom_lists[server_id].setdefault(custom_list_id, custom_list)
            await helpers.save_file("custom_lists", custom_lists)

            embed = discord.Embed(
                title=localisation.get('CUSTOMLIST_UPLOAD_MSG_EMBED_TITLE'),
                description=f"{localisation.get('CUSTOMLIST_UPLOAD_MSG_EMBED_DESC_1')}: {custom_list_id}\n{localisation.get('CUSTOMLIST_UPLOAD_MSG_EMBED_DESC_2')} </{localisation.get('CUSTOMLIST_EDIT_CMD_NAME')}:{await helpers.load_json_key('session', f'{localisation.get("CUSTOMLIST_EDIT_CMD_NAME")}_CMD'.upper())}>\n{localisation.get('CUSTOMLIST_EDIT_MSG_EMBED_DESC')}\n{custom_list_id}: {json.dumps(custom_lists[server_id][custom_list_id], indent=2)[:3750]}",
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
    await bot.add_cog(CustomListUploadCog(bot))