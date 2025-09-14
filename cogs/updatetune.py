import discord
from discord.ext import commands
from discord import app_commands
from cogs import communitytune
import in_app_logging
import tunes_manager
import helpers

logger = helpers.load_logging()

class UpdateTuneCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):

        @app_commands.command(name=self.bot.localisation.get('UPDATE_TUNE_CMD_NAME'), description=self.bot.localisation.get('UPDATE_TUNE_CMD_DESC'))
        @discord.app_commands.describe(tune_id=self.bot.localisation.get('UPDATE_TUNE_CMD_TUNE_ID'), pp=self.bot.localisation.get('UPDATE_TUNE_CMD_PP'), evo=self.bot.localisation.get('UPDATE_TUNE_CMD_EVO'), engine_motor=self.bot.localisation.get('UPDATE_TUNE_CMD_EN_MO'), fusions_engine_motor=f"{self.bot.localisation.get('UPDATE_TUNE_CMD_FUSIONS_FORMAT')} {self.bot.localisation.get('UPDATE_TUNE_CMD_FUSIONS_DESC')} {self.bot.localisation.get('PART_EN_MO')}", turbo_battery=self.bot.localisation.get('UPDATE_TUNE_CMD_TU_BA'), fusions_turbo_battery=f"{self.bot.localisation.get('UPDATE_TUNE_CMD_FUSIONS_FORMAT')} {self.bot.localisation.get('UPDATE_TUNE_CMD_FUSIONS_DESC')} {self.bot.localisation.get('PART_TU_BA')}", intake_inverter=self.bot.localisation.get('UPDATE_TUNE_CMD_IN_IN'), fusions_intake_inverter=f"{self.bot.localisation.get('UPDATE_TUNE_CMD_FUSIONS_FORMAT')} {self.bot.localisation.get('UPDATE_TUNE_CMD_FUSIONS_DESC')} {self.bot.localisation.get('PART_IN_IN')}", nitrous_overboost=self.bot.localisation.get('UPDATE_TUNE_CMD_NI_OV'), fusions_nitrous_overboost=f"{self.bot.localisation.get('UPDATE_TUNE_CMD_FUSIONS_FORMAT')} {self.bot.localisation.get('UPDATE_TUNE_CMD_FUSIONS_DESC')} {self.bot.localisation.get('PART_NI_OV')}", body=self.bot.localisation.get('UPDATE_TUNE_CMD_BODY'), fusions_body=f"{self.bot.localisation.get('UPDATE_TUNE_CMD_FUSIONS_FORMAT')} {self.bot.localisation.get('UPDATE_TUNE_CMD_FUSIONS_DESC')} {self.bot.localisation.get('PART_BODY')}", tires=self.bot.localisation.get('UPDATE_TUNE_CMD_TIRES'), fusions_tires=f"{self.bot.localisation.get('UPDATE_TUNE_CMD_FUSIONS_FORMAT')} {self.bot.localisation.get('UPDATE_TUNE_CMD_FUSIONS_DESC')} {self.bot.localisation.get('PART_TIRES')}", transmission=self.bot.localisation.get('UPDATE_TUNE_CMD_TRANSMISSION'), fusions_transmission=f"{self.bot.localisation.get('UPDATE_TUNE_CMD_FUSIONS_FORMAT')} {self.bot.localisation.get('UPDATE_TUNE_CMD_FUSIONS_DESC')} {self.bot.localisation.get('PART_TRANSMISSION')}", nitrous=self.bot.localisation.get('UPDATE_TUNE_CMD_NOS'), final_drive=self.bot.localisation.get('UPDATE_TUNE_CMD_FD'), tire_pressure=self.bot.localisation.get('UPDATE_TUNE_CMD_TP'), dyno=self.bot.localisation.get('UPDATE_TUNE_CMD_DYNO'), purpose=self.bot.localisation.get('UPDATE_TUNE_CMD_PURPOSE'), usage=self.bot.localisation.get('UPDATE_TUNE_CMD_USAGE'))
        @app_commands.choices(engine_motor=helpers.load_command_options_upgrade_stages(self.bot.localisation))
        @app_commands.choices(turbo_battery=helpers.load_command_options_upgrade_stages(self.bot.localisation))
        @app_commands.choices(intake_inverter=helpers.load_command_options_upgrade_stages(self.bot.localisation))
        @app_commands.choices(nitrous_overboost=helpers.load_command_options_upgrade_stages(self.bot.localisation))
        @app_commands.choices(body=helpers.load_command_options_upgrade_stages(self.bot.localisation))
        @app_commands.choices(tires=helpers.load_command_options_upgrade_stages(self.bot.localisation))
        @app_commands.choices(transmission=helpers.load_command_options_upgrade_stages(self.bot.localisation))
        async def updatetune(interaction: discord.Interaction, tune_id: int, pp: str = None, evo: str = None, engine_motor: str = None, fusions_engine_motor: str = None, turbo_battery: str = None, fusions_turbo_battery: str = None, intake_inverter: str = None, fusions_intake_inverter: str = None, nitrous_overboost: str = None, fusions_nitrous_overboost: str = None, body: str = None, fusions_body: str = None, tires: str = None, fusions_tires: str = None, transmission: str = None, fusions_transmission: str = None, nitrous: str = None, final_drive: float = None, tire_pressure: str = None, dyno: float = None, purpose: str = None, usage: str = None):
            await interaction.response.defer()
            try:
                header = self.bot.localisation.get('UPDATE_TUNE_LOG_HEADER')
                logger.info(f"{header}{self.bot.localisation.get('LOG_CMD_TRIGGERED')} /{self.bot.localisation.get('UPDATE_TUNE_CMD_NAME')} tune_id: {tune_id} pp: {pp} evo: {evo} engine_motor: {engine_motor} fusions_engine_motor: {fusions_engine_motor} turbo_battery: {turbo_battery} fusions_turbo_battery: {fusions_turbo_battery} intake_inverter: {intake_inverter} fusions_intake_inverter: {fusions_intake_inverter} nitrous_overboost: {nitrous_overboost} fusions_nitrous_overboost: {fusions_nitrous_overboost} body: {body} fusions_body: {fusions_body} tires: {tires} fusions_tires: {fusions_tires} transmission: {transmission} fusions_transmission: {fusions_transmission} nitrous: {nitrous} final_drive: {final_drive} tire_pressure: {tire_pressure} dyno: {dyno} purpose: {purpose} usage: {usage}")
                log = f"{header}{self.bot.localisation.get('LOG_CMD_TRIGGERED')} /{self.bot.localisation.get('UPDATE_TUNE_CMD_NAME')} tune_id: {tune_id} pp: {pp} evo: {evo} engine_motor: {engine_motor} fusions_engine_motor: {fusions_engine_motor} turbo_battery: {turbo_battery} fusions_turbo_battery: {fusions_turbo_battery} intake_inverter: {intake_inverter} fusions_intake_inverter: {fusions_intake_inverter} nitrous_overboost: {nitrous_overboost} fusions_nitrous_overboost: {fusions_nitrous_overboost} body: {body} fusions_body: {fusions_body} tires: {tires} fusions_tires: {fusions_tires} transmission: {transmission} fusions_transmission: {fusions_transmission} nitrous: {nitrous} final_drive: {final_drive} tire_pressure: {tire_pressure} dyno: {dyno} purpose: {purpose} usage: {usage}"
                user = str(f"{interaction.user.id}")
                owner = await tunes_manager.get_creator_by_tune_id(int(tune_id))
                if owner is None or owner[0] is None:
                    await interaction.followup.send(f"{self.bot.localisation.get('UPDATE_TUNE_MSG_ERROR_TUNE_ID')}")
                    await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
                    return
                elif user != str(owner[0][0]) or int(user) not in await helpers.load_json_key("config", "ClientAdminIDs"):
                    await interaction.followup.send(f"{self.bot.localisation.get('UPDATE_TUNE_MSG_ERROR_OWNER')}")
                    logger.info(f"{header}{self.bot.localisation.get('LOG_ERROR_NOT_OWNER')}")
                    log += f"\n{header}{self.bot.localisation.get('LOG_ERROR_NOT_OWNER')}"
                    await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
                    return
                else:
                    fusion_cats = []
                    for upgrades in [fusions_engine_motor, fusions_turbo_battery, fusions_intake_inverter, fusions_nitrous_overboost, fusions_body, fusions_tires, fusions_transmission]:
                        fusion_list = (upgrades.split(',') if upgrades else [])[:6]
                        fusion_list += [None] * (6 - len(fusion_list))
                        fusion_list = fusion_list[:6]
                        fusion_cats.append(fusion_list)
                    en_fusions, tu_fusions, in_fusions, ni_fusions, bo_fusions, ti_fusions, tr_fusions = fusion_cats
                    parameters = [pp, evo, engine_motor, en_fusions[0], en_fusions[1], en_fusions[2], en_fusions[3], en_fusions[4], en_fusions[5], turbo_battery, tu_fusions[0], tu_fusions[1], tu_fusions[2], tu_fusions[3], tu_fusions[4], tu_fusions[5], intake_inverter, in_fusions[0], in_fusions[1], in_fusions[2], in_fusions[3], in_fusions[4], in_fusions[5], nitrous_overboost, ni_fusions[0], ni_fusions[1], ni_fusions[2], ni_fusions[3], ni_fusions[4], ni_fusions[5], body, bo_fusions[0], bo_fusions[1], bo_fusions[2], bo_fusions[3], bo_fusions[4], bo_fusions[5], tires, ti_fusions[0], ti_fusions[1], ti_fusions[2], ti_fusions[3], ti_fusions[4], ti_fusions[5], transmission, tr_fusions[0], tr_fusions[1], tr_fusions[2], tr_fusions[3], tr_fusions[4], tr_fusions[5], nitrous, final_drive, tire_pressure, dyno, purpose, usage]
                    error_texts = [
                        "UPDATE_TUNE_LOG_ERROR_TRANSMISSION",
                        "UPDATE_TUNE_LOG_ERROR_TRANSMISSION",
                        "UPDATE_TUNE_LOG_ERROR_TRANSMISSION",
                        "UPDATE_TUNE_LOG_ERROR_TRANSMISSION",
                        "UPDATE_TUNE_LOG_ERROR_TRANSMISSION",
                        "UPDATE_TUNE_LOG_ERROR_TRANSMISSION",
                        "UPDATE_TUNE_LOG_ERROR_TRANSMISSION",
                        "UPDATE_TUNE_LOG_ERROR_TIRES",
                        "UPDATE_TUNE_LOG_ERROR_TIRES",
                        "UPDATE_TUNE_LOG_ERROR_TIRES",
                        "UPDATE_TUNE_LOG_ERROR_TIRES",
                        "UPDATE_TUNE_LOG_ERROR_TIRES",
                        "UPDATE_TUNE_LOG_ERROR_TIRES",
                        "UPDATE_TUNE_LOG_ERROR_TIRES",
                        "UPDATE_TUNE_LOG_ERROR_BODY",
                        "UPDATE_TUNE_LOG_ERROR_BODY",
                        "UPDATE_TUNE_LOG_ERROR_BODY",
                        "UPDATE_TUNE_LOG_ERROR_BODY",
                        "UPDATE_TUNE_LOG_ERROR_BODY",
                        "UPDATE_TUNE_LOG_ERROR_BODY",
                        "UPDATE_TUNE_LOG_ERROR_BODY",
                        "UPDATE_TUNE_LOG_ERROR_NITROUS",
                        "UPDATE_TUNE_LOG_ERROR_NITROUS",
                        "UPDATE_TUNE_LOG_ERROR_NITROUS",
                        "UPDATE_TUNE_LOG_ERROR_NITROUS",
                        "UPDATE_TUNE_LOG_ERROR_NITROUS",
                        "UPDATE_TUNE_LOG_ERROR_NITROUS",
                        "UPDATE_TUNE_LOG_ERROR_NOS_BOOST",
                        "UPDATE_TUNE_LOG_ERROR_INTAKE",
                        "UPDATE_TUNE_LOG_ERROR_INTAKE",
                        "UPDATE_TUNE_LOG_ERROR_INTAKE",
                        "UPDATE_TUNE_LOG_ERROR_INTAKE",
                        "UPDATE_TUNE_LOG_ERROR_INTAKE",
                        "UPDATE_TUNE_LOG_ERROR_INTAKE",
                        "UPDATE_TUNE_LOG_ERROR_INTAKE_INVERTER",
                        "UPDATE_TUNE_LOG_ERROR_TURBO",
                        "UPDATE_TUNE_LOG_ERROR_TURBO",
                        "UPDATE_TUNE_LOG_ERROR_TURBO",
                        "UPDATE_TUNE_LOG_ERROR_TURBO",
                        "UPDATE_TUNE_LOG_ERROR_TURBO",
                        "UPDATE_TUNE_LOG_ERROR_TURBO",
                        "UPDATE_TUNE_LOG_ERROR_TURBO_BATTERY",
                        "UPDATE_TUNE_LOG_ERROR_ENGINE",
                        "UPDATE_TUNE_LOG_ERROR_ENGINE",
                        "UPDATE_TUNE_LOG_ERROR_ENGINE",
                        "UPDATE_TUNE_LOG_ERROR_ENGINE",
                        "UPDATE_TUNE_LOG_ERROR_ENGINE",
                        "UPDATE_TUNE_LOG_ERROR_ENGINE",
                        "UPDATE_TUNE_LOG_ERROR_ENGINE_MOTOR",
                        "UPDATE_TUNE_LOG_ERROR_EVO",
                        "UPDATE_TUNE_LOG_ERROR_PP"
                    ]
                    for idx, parameter in enumerate(parameters):
                        if idx in [0, 1]:
                            if parameter is None or parameter.isdigit():
                                continue
                            else:
                                await interaction.followup.send(f"{header}{self.bot.localisation.get(error_texts[idx].replace("_LOG_", "_MSG_"))} {parameter}")
                                logger.info(f"{header}{self.bot.localisation.get(error_texts[idx])} {parameter}")
                                log += (f"{header}{self.bot.localisation.get(error_texts[idx])} {parameter}")
                        if idx in [2, 9, 16, 23, 30, 37, 44]:
                            if parameter is None or (int(parameter) >= 0 and int(parameter) <= 6):
                                continue
                            else:
                                await interaction.followup.send(f"{header}{self.bot.localisation.get(error_texts[idx].replace("_LOG_", "_MSG_"))} {parameter}")
                                logger.info(f"{header}{self.bot.localisation.get(error_texts[idx])} {parameter}")
                                log += (f"{header}{self.bot.localisation.get(error_texts[idx])} {parameter}")
                        if idx in [3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 24, 25, 26, 27, 28, 29, 31, 32, 33, 34, 35, 36, 38, 39, 40, 41, 42, 43, 45, 46, 47, 48, 49, 50]:
                            if parameter is None or (int(parameter) >= 0 and int(parameter) <= 5):
                                continue
                            else:
                                await interaction.followup.send(f"{header}{self.bot.localisation.get(error_texts[idx].replace("_LOG_", "_MSG_"))} {parameter}")
                                logger.info(f"{header}{self.bot.localisation.get(error_texts[idx])} {parameter}")
                                log += (f"{header}{self.bot.localisation.get(error_texts[idx])} {parameter}")
                    parameters.append(interaction.user.display_name)
                    if any(parameters):
                        log, status = await tunes_manager.alter_entry(tune_id, parameters, log)
                    else:
                        await interaction.followup.send(f"{self.bot.localisation.get('UPDATE_TUNE_MSG_ERROR_NO_VALUE')}")
                        logger.info(f"{header}{self.bot.localisation.get('UPDATE_TUNE_LOG_ERROR_NO_VALUE')}")
                        log += f"\n{header}{self.bot.localisation.get('UPDATE_TUNE_LOG_ERROR_NO_VALUE')}"
                        status = 0
                    await interaction.followup.send(f"{self.bot.localisation.get('UPDATE_TUNE_MSG_DONE')}")
                    results = await tunes_manager.query_tune(car = None, tune_id = tune_id, tier = None, rarity = None, purpose = None, creator = None)
                    messages, log = await communitytune.create_embeds(results, log)
                    await communitytune.send_channel(interaction, messages, log) if interaction.guild else await communitytune.send_dms(interaction, messages, log)
                    await in_app_logging.send_log(self.bot, log, status, 1, interaction)
                    return
            except Exception as e:
                await interaction.followup.send(f"{self.bot.localisation.get('MSG_ERROR_FETCH')} {e}")
                logger.info(f"{self.bot.localisation.get('LOG_ERROR_FETCH')} {e}")
                log += f"{self.bot.localisation.get('LOG_ERROR_FETCH')} {e}"
                await in_app_logging.send_log(self.bot, log, 0, 1, interaction)

        self.bot.tree.add_command(updatetune)

async def setup(bot):
    await bot.add_cog(UpdateTuneCog(bot))
