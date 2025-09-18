import discord
from discord.ext import commands
from discord import app_commands
import json
import helpers
import in_app_logging

logger = helpers.load_logging()
localisation = dict(helpers.load_localisation())

class CustomListEditCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name=localisation.get('CUSTOMLIST_EDIT_CMD_NAME'), description=localisation.get('CUSTOMLIST_EDIT_CMD_DESC'))
    @app_commands.describe(list_id=localisation.get('CUSTOMLIST_ANY_CMD_LIST_ID'), global_list=localisation.get('CUSTOMLIST_ANY_CMD_GLOBAL_LIST'), list_name=localisation.get('CUSTOMLIST_ANY_CMD_LIST_NAME'), group=localisation.get('CUSTOMLIST_ANY_CMD_GROUP'), group_name=localisation.get('CUSTOMLIST_ANY_CMD_GROUP_NAME'), car=localisation.get('CUSTOMLIST_ANY_CMD_CAR'), car_name=localisation.get('CUSTOMLIST_ANY_CMD_CAR_NAME'), car_group=localisation.get('CUSTOMLIST_ANY_CMD_CAR_GROUP'))
    @app_commands.choices(global_list=[app_commands.Choice(name=localisation.get('CUSTOMLIST_ANY_CMD_GLOBAL_LIST_OPTION_TRUE'), value=1), app_commands.Choice(name=localisation.get('CUSTOMLIST_ANY_CMD_GLOBAL_LIST_OPTION_FALSE'), value=0)])
    @app_commands.choices(group=[app_commands.Choice(name=localisation.get('CUSTOMLIST_EDIT_CMD_ANY_OPTION_ADD'), value=1), app_commands.Choice(name=localisation.get('CUSTOMLIST_EDIT_CMD_ANY_OPTION_RENAME'), value=2), app_commands.Choice(name=localisation.get('CUSTOMLIST_EDIT_CMD_ANY_OPTION_DELETE'), value=0)])
    @app_commands.choices(car=[app_commands.Choice(name=localisation.get('CUSTOMLIST_EDIT_CMD_ANY_OPTION_ADD'), value=1), app_commands.Choice(name=localisation.get('CUSTOMLIST_EDIT_CMD_ANY_OPTION_DELETE'), value=0)])
    async def customlistedit(self, interaction: discord.Interaction, list_id: int, global_list: int = None, list_name: str = None, group: int = None, group_name: str = None, car: int = None, car_name: str = None, car_group: str = None):
        await interaction.response.defer(ephemeral=True)
        try:
            header = localisation.get('CUSTOMLIST_EDIT_LOG_HEADER')
            logger.info(f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('CUSTOMLIST_EDIT_CMD_NAME')} list_id: {list_id} global_list: {global_list} list_name: {list_name} groupe: {group} groupe_name: {group_name} car: {car} car_name: {car_name} car_group: {car_group}")
            log = f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('CUSTOMLIST_EDIT_CMD_NAME')} list_id: {list_id} global_list: {global_list}"

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
            if server_id not in custom_lists.keys():
                await interaction.followup.send(f"{localisation.get('CUSTOMLIST_EDIT_MSG_WARNING_NO_SERVER')}", ephemeral=True)
                return
            else:
                if str(list_id).zfill(3) not in custom_lists[server_id].keys():
                    await interaction.followup.send(f"{localisation.get('CUSTOMLIST_EDIT_MSG_WARNING_NO_ID')}", ephemeral=True)
                    return

            if list_name:
                custom_lists[server_id][str(list_id).zfill(3)]["Name"] = list_name

            if group is not None:
                if group == 0:
                    if group_name != "Name" and group_name != "UNGROUPED":
                        custom_lists[server_id][str(list_id).zfill(3)].pop(str(group_name), None)
                    else:
                        await interaction.followup.send(f"{localisation.get('CUSTOMLIST_EDIT_MSG_WARNING_NAME_INVALID')} categegory: {group}", ephemeral=True)
                if group == 1:
                    if await helpers.is_list(group_name):
                        for name in json.loads(group_name):
                            if name != "Name" and name != "UNGROUPED" and not None:
                                custom_lists[server_id][str(list_id).zfill(3)].setdefault(name, [])
                            else:
                                await interaction.followup.send(f"{localisation.get('CUSTOMLIST_EDIT_MSG_WARNING_NAME_INVALID')} categegory: {group}", ephemeral=True)
                    else:
                        if group_name != "Name" and group_name != "UNGROUPED" and not None:
                            custom_lists[server_id][str(list_id).zfill(3)].setdefault(group_name, [])
                        else:
                            await interaction.followup.send(f"{localisation.get('CUSTOMLIST_EDIT_MSG_WARNING_NAME_INVALID')} categegory: {group}", ephemeral=True)
                if group == 2:
                    if await helpers.is_list(group_name):
                        if len(json.loads(group_name)) == 2:
                            rename_list = json.loads(group_name)
                            old_name = rename_list[0]
                            new_name = rename_list[1]
                            if old_name in custom_lists[server_id][str(list_id).zfill(3)].keys() and  old_name != "Name" and old_name != "UNGROUPED":
                                custom_lists[server_id][str(list_id).zfill(3)][new_name] = custom_lists[server_id][str(list_id).zfill(3)].pop(old_name)
                            else:
                                await interaction.followup.send(f"{localisation.get('CUSTOMLIST_EDIT_MSG_WARNING_NO_GROUP')} categegory: {group}", ephemeral=True)
                        else:
                            await interaction.followup.send(f"{localisation.get('CUSTOMLIST_EDIT_MSG_WARNING_TO_MANY_ARGUMENTS')} categegory: {group}", ephemeral=True)
                    else:
                        await interaction.followup.send(f"{localisation.get('CUSTOMLIST_EDIT_MSG_WARNING_LIST_INVALID')} categegory: {group}", ephemeral=True)

            if car is not None:
                if car == 0:
                    if car_group is None:
                        car_group = "UNGROUPED"
                    if car_group:
                        if car_group in custom_lists[server_id][str(list_id).zfill(3)].keys() and car_group != "Name":
                            if car_name:
                                if car_name in custom_lists[server_id][str(list_id).zfill(3)][car_group]:
                                    custom_lists[server_id][str(list_id).zfill(3)][car_group].remove(car_name)
                                else:
                                    await interaction.followup.send(f"{localisation.get('CUSTOMLIST_EDIT_MSG_WARNING_NOT_IN_LIST')} car_name: {car_name}, car_group: {car_group}", ephemeral=True)
                            else:
                                await interaction.followup.send(f"{localisation.get('CUSTOMLIST_EDIT_MSG_WARNING_NO_VALUE')} car_name", ephemeral=True)
                        else:
                            await interaction.followup.send(f"{localisation.get('CUSTOMLIST_EDIT_MSG_WARNING_NO_GROUP')} car_group: {car_group}", ephemeral=True)
                    else:
                        await interaction.followup.send(f"{localisation.get('CUSTOMLIST_EDIT_MSG_WARNING_NO_VALUE')} car_group", ephemeral=True)

                if car == 1:
                    if car_group:
                        if car_group in custom_lists[server_id][str(list_id).zfill(3)].keys() and car_group != "Name":
                            if car_name:
                                car_name = car_name.replace("*", "%")
                                querry = """\nSELECT "DB Name"\nFROM info\nWHERE "DB Name" LIKE ?"""
                                results = []
                                if await helpers.is_list(car_name):
                                    for car in json.loads(car_name):
                                        result = await helpers.execute_sql_statement("WRs", querry, [f"{car}%"])
                                        results = list(set(results + result))
                                else:
                                    results = await helpers.execute_sql_statement("WRs", querry, [f"{car_name}%"])
                                if results:
                                    for result in results:
                                        if result[0] not in custom_lists[server_id][str(list_id).zfill(3)][car_group]:
                                            custom_lists[server_id][str(list_id).zfill(3)][car_group].append(result[0])
                                else:
                                    await interaction.followup.send(f"{localisation.get('CUSTOMLIST_EDIT_MSG_WARNING_INVALID')} car_name: {car_name}", ephemeral=True)
                            else:
                                await interaction.followup.send(f"{localisation.get('CUSTOMLIST_EDIT_MSG_WARNING_NO_VALUE')} car_name", ephemeral=True)
                        else:
                            await interaction.followup.send(f"{localisation.get('CUSTOMLIST_EDIT_MSG_WARNING_NO_GROUP')} car_group: {car_group}", ephemeral=True)
                    else:
                        await interaction.followup.send(f"{localisation.get('CUSTOMLIST_EDIT_MSG_WARNING_NO_VALUE')} car_group", ephemeral=True)

            await helpers.save_file("custom_lists", custom_lists)

            embed = discord.Embed(
                title=localisation.get('CUSTOMLIST_EDIT_MSG_EMBED_TITLE'),
                description=f"{localisation.get('CUSTOMLIST_EDIT_MSG_EMBED_DESC')}\n```json\n{str(list_id).zfill(3)}: {json.dumps(custom_lists[server_id][str(list_id).zfill(3)], indent=2)[:4000]}```",
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
    await bot.add_cog(CustomListEditCog(bot))