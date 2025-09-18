import discord
from discord.ext import commands
from discord import app_commands
import in_app_logging
import helpers

logger = helpers.load_logging()
localisation = dict(helpers.load_localisation())

class CustomListTemplateCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name=localisation.get('CUSTOMLIST_TEMPLATE_CMD_NAME'), description=localisation.get('CUSTOMLIST_TEMPLATE_CMD_DESC'))
    async def template(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            header = localisation.get('CUSTOMLIST_TEMPLATE_LOG_HEADER')
            logger.info(f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('CUSTOMLIST_TEMPLATE_CMD_NAME')}")
            log = f"{header}{localisation.get('LOG_CMD_TRIGGERED')} /{localisation.get('CUSTOMLIST_TEMPLATE_CMD_NAME')}"
            await interaction.followup.send(f"""```properties\n{"{"} # {localisation.get('CUSTOMLIST_TEMPLATE_MSG_JSON_COMMENT_01')}\n    "Name": "LIST_NAME", # {localisation.get('CUSTOMLIST_TEMPLATE_MSG_JSON_COMMENT_02')}\n    "UNGROUPED": [ # {localisation.get('CUSTOMLIST_TEMPLATE_MSG_JSON_COMMENT_03')}\n        "CAR_DB_NAME", # {localisation.get('CUSTOMLIST_TEMPLATE_MSG_JSON_COMMENT_04')}\n        "CAR_DB_NAME" # {localisation.get('CUSTOMLIST_TEMPLATE_MSG_JSON_COMMENT_05')}\n    ], # {localisation.get('CUSTOMLIST_TEMPLATE_MSG_JSON_COMMENT_06')}\n    "GROUP1_NAME_HERE": [ # {localisation.get('CUSTOMLIST_TEMPLATE_MSG_JSON_COMMENT_07')}\n        "CAR_DB_NAME", # {localisation.get('CUSTOMLIST_TEMPLATE_MSG_JSON_COMMENT_08')}\n        "CAR_DB_NAME" # {localisation.get('CUSTOMLIST_TEMPLATE_MSG_JSON_COMMENT_09')}\n    ], # {localisation.get('CUSTOMLIST_TEMPLATE_MSG_JSON_COMMENT_10')}\n    "GROUP2_NAME_HERE": [ # {localisation.get('CUSTOMLIST_TEMPLATE_MSG_JSON_COMMENT_11')}\n        "CAR_DB_NAME", # {localisation.get('CUSTOMLIST_TEMPLATE_MSG_JSON_COMMENT_12')}\n        "CAR_DB_NAME" # {localisation.get('CUSTOMLIST_TEMPLATE_MSG_JSON_COMMENT_13')}\n    ] # {localisation.get('CUSTOMLIST_TEMPLATE_MSG_JSON_COMMENT_14')}\n{"}"} # {localisation.get('CUSTOMLIST_TEMPLATE_MSG_JSON_COMMENT_15')}\n```""", file=discord.File(await helpers.load_file_path('customlist_template'), filename="CustomList_Template.json"), ephemeral=True)
            await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
        except Exception as e:
            await interaction.followup.send(f"{localisation.get('MSG_ERROR_FETCH')} {e}", ephemeral=True)
            logger.info(f"{localisation.get('LOG_ERROR_FETCH')} {e}")
            log += f"\n{localisation.get('LOG_ERROR_FETCH')} {e}"
            await in_app_logging.send_log(self.bot, log, 0, 1, interaction)

async def setup(bot):
    await bot.add_cog(CustomListTemplateCog(bot))