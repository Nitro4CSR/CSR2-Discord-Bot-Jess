import discord
from discord.ext import commands
from discord import app_commands
import in_app_logging
import helpers

logger = helpers.load_logging()

class DBStructureCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):

        @app_commands.command(name=self.bot.localisation.get('DBSTRUCTURE_CMD_NAME'), description=self.bot.localisation.get('DBSTRUCTURE_CMD_DESC'))
        async def dbstructure(interaction: discord.Interaction):
            await interaction.response.defer()
            try:
                header = self.bot.localisation.get('DBSTRUCTURE_LOG_HEADER')
                logger.info(f"{header}{self.bot.localisation.get('LOG_CMD_TRIGGERED')} /{self.bot.localisation.get('DBSTRUCTURE_CMD_NAME')}")
                log = f"{header}{self.bot.localisation.get('LOG_CMD_TRIGGERED')} /{self.bot.localisation.get('DBSTRUCTURE_CMD_NAME')}"
    
                embed = discord.Embed(
                    title=f"{self.bot.localisation.get('DBSTRUCTURE_MSG_EMBED_TITLE')}",
                    description="## tunes.db\n# community_tunes\n- `TuneID`: INTEGER (PRIMARY KEY)\n- `DB Name`: TEXT\n- `Ingame Name Clarification`: TEXT\n- `Un`: TEXT\n- `★`: TEXT\n- `PP`: TEXT\n- `EVO`: TEXT\n- `Engine/Motor`: INTEGER\n- `En_st.1`: INTEGER`\n- `En_st.2`: INTEGER`\n- `En_st.3`: INTEGER`\n- `En_st.4`: INTEGER`\n- `En_st.5`: INTEGER`\n- `En_st.6`: INTEGER`\n- `Turbo/Battery`: INTEGER\n- `Tu_st.1`: INTEGER\n-  `Tu_st.2`: INTEGER\n-  `Tu_st.3`: INTEGER\n-  `Tu_st.4`: INTEGER\n-  `Tu_st.5`: INTEGER\n-  `Tu_st.6`: INTEGER\n- `Intake/Inverter`: INTEGER\n- `In_st.1`: INTEGER\n-  `In_st.2`: INTEGER\n-  `In_st.3`: INTEGER\n-  `In_st.4`: INTEGER\n-  `In_st.5`: INTEGER\n-  `In_st.6`\n- `Nitrous/Overboost`: INTEGER\n- `Ni_st.1`: INTEGER\n-  `Ni_st.2`: INTEGER\n-  `Ni_st.3`: INTEGER\n-  `Ni_st.4`: INTEGER\n-  `Ni_st.5`: INTEGER\n-  `Ni_st.6`\n- `Body`: INTEGER\n- `Bo_st.1`: INTEGER\n-  `Bo_st.2`: INTEGER\n-  `Bo_st.3`: INTEGER\n-  `Bo_st.4`: INTEGER\n-  `Bo_st.5`: INTEGER\n-  `Bo_st.6`\n- `Tires`: INTEGER\n- `Ti_st.1`: INTEGER\n-  `Ti_st.2`: INTEGER\n-  `Ti_st.3`: INTEGER\n-  `Ti_st.4`: INTEGER\n-  `Ti_st.5`: INTEGER\n-  `Ti_st.6`\n- `Transmission`: INTEGER\n- `Tr_st.1`: INTEGER\n-  `Tr_st.2`: INTEGER\n-  `Tr_st.3`: INTEGER\n-  `Tr_st.4`: INTEGER\n-  `Tr_st.5`: INTEGER\n-  `Tr_st.6`\n- `NITRO`: TEXT\n- `FD`: REAL\n- `TIRE`: TEXT\n- `DYNO`: REAL\n- `Purpose`: TEXT\n- `Usage Guide`: TEXT\n- `Creator`: TEXT\n- `Creator ID`: TEXT\n# sqlite_sequence\n- `name`: TEXT\n- `seq`: INTEGER\n---\n## WRs.db\n# records\n- `UniqueID`: TEXT (PRIMARY KEY)\n- `DB Name`: TEXT\n- `Ingame Name Clarification`: TEXT\n- `Un`: TEXT\n- `★`: TEXT\n- `WR-PP`: TEXT\n- `WR-EVO`: TEXT\n- `WR-NITRO`: TEXT\n- `WR-FD`: REAL\n- `WR-TIRE`: TEXT\n- `WR-DYNO`: REAL\n- `WR-BEST ET`: REAL\n- `WR Addon`: TEXT\n- `SHIFT Links`: TEXT\n- `WR-DRIVER`: TEXT\n# s6_effects\n- `UniqueID`: TEXT (PRIMARY KEY)\n- `DB Name`: TEXT\n- `Ingame Name`: TEXT\n- `Un`: TEXT\n- `★`: TEXT\n- `S5 - PP`: TEXT\n- `S5 - EVO`: TEXT\n- `S5 - NOS`: TEXT\n- `S5 - FD`: REAL\n- `S5 - TIRES`: TEXT\n- `S5 - DYNO`: REAL\n- `Engine`: REAL\n- `Turbo`: REAL\n- `Intake`: REAL\n- `NOS`: REAL\n- `Body`: REAL\n- `Tires`: REAL\n- `Trans`: REAL\n- `is EV?`: TEXT\n# info\n- `UniqueID`: TEXT (PRIMARY KEY)\n- `DB Name`: TEXT\n- `Ingame Name Clarification`: TEXT\n- `Un`: TEXT\n- `★`: TEXT\n- `IMG`: TEXT\n- `Vision Info`: TEXT\n- `is EV?`: TEXT\n- `thread`: TEXT\n# updates\n- `ID`: TEXT (PRIMARY KEY)\n- `Date`: TEXT\n- `Output Vision`: TEXT",
                    color=discord.Color(0xff00ff)
                )
                embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')
    
                await interaction.followup.send(embed=embed)
                await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
            except Exception as e:
                await interaction.followup.send(f"{self.bot.localisation.get('MSG_ERROR_FETCH')} {e}")
                logger.info(f"{self.bot.localisation.get('LOG_ERROR_FETCH')} {e}")
                log += f"{self.bot.localisation.get('LOG_ERROR_FETCH')} {e}"
                await in_app_logging.send_log(self.bot, log, 0, 1, interaction)

        self.bot.tree.add_command(dbstructure)

async def setup(bot):
    await bot.add_cog(DBStructureCog(bot))
