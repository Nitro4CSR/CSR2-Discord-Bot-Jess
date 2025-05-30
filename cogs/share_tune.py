import asyncio
import discord
from discord.ext import commands
from discord import app_commands, ui
import aiofiles
import json
import in_app_logging
import tunes_manager
import helpers

logger = helpers.load_logging()

class ShareTuneCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.car_message = None
        self.active_submissions = {}

    @app_commands.command(name="csr2_share_tune", description="Start sharing a custom tune.")
    @app_commands.choices(fusions=[app_commands.Choice(name="Maxed", value=int(1)), app_commands.Choice(name="Stock", value=int(2)), app_commands.Choice(name="Custom", value=int(0))])
    async def share_tune(self, interaction: discord.Interaction, fusions: int = None):
        logger.info(f"SHARE_TUNE - The following command has been used: /csr2_share_tune")
        log = f"SHARE_TUNE - The following command has been used: /csr2_share_tune"
        await interaction.response.defer()

        if not fusions:
            fusions = 0
            save_fusion_selection(fusions)

        if interaction.guild is None:
            logger.info(f"SHARE_TUNE - DMs detected")
            log += f"\nSHARE_TUNE - DMs detected"
            logger.info("SHARE_TUNE - Starting submission loop...")
            log += f"\nSHARE_TUNE - Starting submission loop..."
            await interaction.followup.send(f"The submission loop will start in a bit...")
            if fusions:
                log = await self.submission_loop(interaction, log, fusions)
            else:
                log = await self.submission_loop(interaction, log)
        else:
            logger.info(f"SHARE_TUNE - Server detected. Trying to DM...")
            log += f"\nSHARE_TUNE - Server detected. Trying to DM..."
            try:
                await interaction.followup.send("Please continue your submission in DMs. Make sure you allow messages from non-friended users.")
                logger.info(f"SHARE_TUNE - DM success")
                log += f"\nSHARE_TUNE - DM success"
                if fusions:
                    log = await self.submission_loop(interaction, log, fusions)
                else:
                    log = await self.submission_loop(interaction, log)
            except Exception as e:
                if interaction.response.is_done():
                    await interaction.followup.send("There was an error starting the submission loop. Please try again later.")
                    logger.error(f"SHARE_TUNE - There was an error starting the submission loop: {e}")
                    log += f"SHARE_TUNE - There was an error starting the submission loop: {e}"
                    status = 0
                else:
                    await interaction.response.send_message("Please make sure your DMs are open and try again")
                    logger.warning(f"\nSHARE_TUNE - DM failed")
                    log += f"\nSHARE_TUNE - DM failed"
                    status = 1
                await in_app_logging.send_log(self.bot, log, status, 1, interaction)

            return

    @app_commands.command(name="csr2_update_tune", description="Update one of your tunes")
    @discord.app_commands.describe(tune_id="An unique identifier integer provided to you when you created your tune and needed to point at the tune you want to edit", pp="The pp rating of your cars tune", evo="The evo rating of your cars tune", engine_motor="The equipped upgrade stage in the category Engine/Motor", fusions_engine_motor="format: 1,2,3,4,5,6 The fitted fusions per stage in the category Engine/Motor", turbo_battery="The equipped upgrade stage in the category Turbo/Battery", fusions_turbo_battery="format: 1,2,3,4,5,6 The fitted fusions per stage in the category Turbo/Battery", intake_inverter="The equipped upgrade stage in the category Intake/Inverter", fusions_intake_inverter="format: 1,2,3,4,5,6 The fitted fusions per stage in the category Intake/Inverter", nitrous_overboost="The equipped upgrade stage in the category Nitrous/Overboost", fusions_nitrous_overboost="format: 1,2,3,4,5,6 The fitted fusions per stage in the category Nitrous/Overboost", body="The equipped upgrade stage in the category Body", fusions_body="format: 1,2,3,4,5,6 The fitted fusions per stage in the category Body", tires="The equipped upgrade stage in the category Tires", fusions_tires="format: 1,2,3,4,5,6 The fitted fusions per stage in the category Tires", transmission="The equipped upgrade stage in the category Transmission", fusions_transmission="format: 1,2,3,4,5,6 The fitted fusions per stage in the category Transmission", nitrous="Your nitrous tuning setup", final_drive="Your final drive tuning setup", tire_pressure="Your tire pressure tuning setup", dyno="Your tuning setups dyno time", purpose="The use case of your tune", usage="How to use your setup correctly")
    @app_commands.choices(engine_motor=[app_commands.Choice(name="Stage 1", value="1"), app_commands.Choice(name="Stage 2", value="2"), app_commands.Choice(name="Stage 3", value="3"), app_commands.Choice(name="Stage 4", value="4"), app_commands.Choice(name="Stage 5", value="5"), app_commands.Choice(name="Stage 6", value="6")])
    @app_commands.choices(turbo_battery=[app_commands.Choice(name="Stage 1", value="1"), app_commands.Choice(name="Stage 2", value="2"), app_commands.Choice(name="Stage 3", value="3"), app_commands.Choice(name="Stage 4", value="4"), app_commands.Choice(name="Stage 5", value="5"), app_commands.Choice(name="Stage 6", value="6")])
    @app_commands.choices(intake_inverter=[app_commands.Choice(name="Stage 1", value="1"), app_commands.Choice(name="Stage 2", value="2"), app_commands.Choice(name="Stage 3", value="3"), app_commands.Choice(name="Stage 4", value="4"), app_commands.Choice(name="Stage 5", value="5"), app_commands.Choice(name="Stage 6", value="6")])
    @app_commands.choices(nitrous_overboost=[app_commands.Choice(name="Stage 1", value="1"), app_commands.Choice(name="Stage 2", value="2"), app_commands.Choice(name="Stage 3", value="3"), app_commands.Choice(name="Stage 4", value="4"), app_commands.Choice(name="Stage 5", value="5"), app_commands.Choice(name="Stage 6", value="6")])
    @app_commands.choices(body=[app_commands.Choice(name="Stage 1", value="1"), app_commands.Choice(name="Stage 2", value="2"), app_commands.Choice(name="Stage 3", value="3"), app_commands.Choice(name="Stage 4", value="4"), app_commands.Choice(name="Stage 5", value="5"), app_commands.Choice(name="Stage 6", value="6")])
    @app_commands.choices(tires=[app_commands.Choice(name="Stage 1", value="1"), app_commands.Choice(name="Stage 2", value="2"), app_commands.Choice(name="Stage 3", value="3"), app_commands.Choice(name="Stage 4", value="4"), app_commands.Choice(name="Stage 5", value="5"), app_commands.Choice(name="Stage 6", value="6")])
    @app_commands.choices(transmission=[app_commands.Choice(name="Stage 1", value="1"), app_commands.Choice(name="Stage 2", value="2"), app_commands.Choice(name="Stage 3", value="3"), app_commands.Choice(name="Stage 4", value="4"), app_commands.Choice(name="Stage 5", value="5"), app_commands.Choice(name="Stage 6", value="6")])
    async def update_tune(self, interaction: discord.Interaction, tune_id: int, pp: str = None, evo: str = None, engine_motor: str = None, fusions_engine_motor: str = None, turbo_battery: str = None, fusions_turbo_battery: str = None, intake_inverter: str = None, fusions_intake_inverter: str = None, nitrous_overboost: str = None, fusions_nitrous_overboost: str = None, body: str = None, fusions_body: str = None, tires: str = None, fusions_tires: str = None, transmission: str = None, fusions_transmission: str = None, nitrous: str = None, final_drive: float = None, tire_pressure: str = None, dyno: float = None, purpose: str = None, usage: str = None):
        logger.info(f"UPDATE_TUNE - The following command has been used: /csr2_update_tune tune_id: {tune_id} pp: {pp} evo: {evo} engine_motor: {engine_motor} fusions_engine_motor: {fusions_engine_motor} turbo_battery: {turbo_battery} fusions_turbo_battery: {fusions_turbo_battery} intake_inverter: {intake_inverter} fusions_intake_inverter: {fusions_intake_inverter} nitrous_overboost: {nitrous_overboost} fusions_nitrous_overboost: {fusions_nitrous_overboost} body: {body} fusions_body: {fusions_body} tires: {tires} fusions_tires: {fusions_tires} transmission: {transmission} fusions_transmission: {fusions_transmission} nitrous: {nitrous} final_drive: {final_drive} tire_pressure: {tire_pressure} dyno: {dyno} purpose: {purpose} usage: {usage}")
        log = f"UPDATE_TUNE - The following command has been used: /csr2_update_tune tune_id: {tune_id} pp: {pp} evo: {evo} engine_motor: {engine_motor} fusions_engine_motor: {fusions_engine_motor} turbo_battery: {turbo_battery} fusions_turbo_battery: {fusions_turbo_battery} intake_inverter: {intake_inverter} fusions_intake_inverter: {fusions_intake_inverter} nitrous_overboost: {nitrous_overboost} fusions_nitrous_overboost: {fusions_nitrous_overboost} body: {body} fusions_body: {fusions_body} tires: {tires} fusions_tires: {fusions_tires} transmission: {transmission} fusions_transmission: {fusions_transmission} nitrous: {nitrous} final_drive: {final_drive} tire_pressure: {tire_pressure} dyno: {dyno} purpose: {purpose} usage: {usage}"
        await interaction.response.defer()

        NITRO = await helpers.load_super_admin()

        user = str(f"{interaction.user.id}")
        owner = await tunes_manager.get_creator_by_tune_id(int(tune_id))

        if fusions_engine_motor:
            en_fusions = fusions_engine_motor.split(',')
        else:
            en_fusions = [None, None, None, None, None, None]
        if fusions_turbo_battery:
            tu_fusions = fusions_turbo_battery.split(',')
        else:
            tu_fusions = [None, None, None, None, None, None]
        if fusions_intake_inverter:
            in_fusions = fusions_intake_inverter.split(',')
        else:
            in_fusions = [None, None, None, None, None, None]
        if fusions_nitrous_overboost:
            ni_fusions = fusions_nitrous_overboost.split(',')
        else:
            ni_fusions = [None, None, None, None, None, None]
        if fusions_body:
            bo_fusions = fusions_body.split(',')
        else:
            bo_fusions = [None, None, None, None, None, None]
        if fusions_tires:
            ti_fusions = fusions_tires.split(',')
        else:
            ti_fusions = [None, None, None, None, None, None]
        if fusions_transmission:
            tr_fusions = fusions_transmission.split(',')
        else:
            tr_fusions = [None, None, None, None, None, None]

        if owner is None or owner[0] is None:
            await interaction.followup.send("The TuneID you entered does not exist. Please enter a valid TuneID and try again.")
            await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
        elif user == owner[0] or user == NITRO:
            if (pp == None  or pp.isdigit()):
                if (evo == None or evo.isdigit()):
                    if (engine_motor is None) or (int(engine_motor) >= 0 and int(engine_motor) <= 6):
                        if (en_fusions[0] is None) or (int(en_fusions[0]) >= 0 and int(en_fusions[0]) <= 5):
                            if (en_fusions[1] is None) or (int(en_fusions[1]) >= 0 and int(en_fusions[1]) <= 5):
                                if (en_fusions[2] is None) or (int(en_fusions[2]) >= 0 and int(en_fusions[2]) <= 5):
                                    if (en_fusions[3] is None) or (int(en_fusions[3]) >= 0 and int(en_fusions[3]) <= 5):
                                        if (en_fusions[4] is None) or (int(en_fusions[4]) >= 0 and int(en_fusions[4]) <= 5):
                                            if (en_fusions[5] is None) or (int(en_fusions[5]) >= 0 and int(en_fusions[5]) <= 5):
                                                if (turbo_battery is None) or (int(turbo_battery) >= 0 and int(turbo_battery) <= 6):
                                                    if (tu_fusions[0] is None) or (int(tu_fusions[0]) >= 0 and int(tu_fusions[0]) <= 5):
                                                        if (tu_fusions[1] is None) or (int(tu_fusions[1]) >= 0 and int(tu_fusions[1]) <= 5):
                                                            if (tu_fusions[2] is None) or (int(tu_fusions[2]) >= 0 and int(tu_fusions[2]) <= 5):
                                                                if (tu_fusions[3] is None) or (int(tu_fusions[3]) >= 0 and int(tu_fusions[3]) <= 5):
                                                                    if (tu_fusions[4] is None) or (int(tu_fusions[4]) >= 0 and int(tu_fusions[4]) <= 5):
                                                                        if (tu_fusions[5] is None) or (int(tu_fusions[5]) >= 0 and int(tu_fusions[5]) <= 5):
                                                                            if (intake_inverter is None) or (int(intake_inverter) >= 0 and int(intake_inverter) <= 6):
                                                                                if (in_fusions[0] is None) or (int(in_fusions[0]) >= 0 and int(in_fusions[0]) <= 5):
                                                                                    if (in_fusions[1] is None) or (int(in_fusions[1]) >= 0 and int(in_fusions[1]) <= 5):
                                                                                        if (in_fusions[2] is None) or (int(in_fusions[2]) >= 0 and int(in_fusions[2]) <= 5):
                                                                                            if (in_fusions[3] is None) or (int(in_fusions[3]) >= 0 and int(in_fusions[3]) <= 5):
                                                                                                if (in_fusions[4] is None) or (int(in_fusions[4]) >= 0 and int(in_fusions[4]) <= 5):
                                                                                                    if (in_fusions[5] is None) or (int(in_fusions[5]) >= 0 and int(in_fusions[5]) <= 5):
                                                                                                        if (nitrous_overboost is None) or (int(nitrous_overboost) >= 0 and int(nitrous_overboost) <= 6):
                                                                                                            if (ni_fusions[0] is None) or (int(ni_fusions[0]) >= 0 and int(ni_fusions[0]) <= 5):
                                                                                                                if (ni_fusions[1] is None) or (int(ni_fusions[1]) >= 0 and int(ni_fusions[1]) <= 5):
                                                                                                                    if (ni_fusions[2] is None) or (int(ni_fusions[2]) >= 0 and int(ni_fusions[2]) <= 5):
                                                                                                                        if (ni_fusions[3] is None) or (int(ni_fusions[3]) >= 0 and int(ni_fusions[3]) <= 5):
                                                                                                                            if (ni_fusions[4] is None) or (int(ni_fusions[4]) >= 0 and int(ni_fusions[4]) <= 5):
                                                                                                                                if (ni_fusions[5] is None) or (int(ni_fusions[5]) >= 0 and int(ni_fusions[5]) <= 5):
                                                                                                                                    if (body is None) or (int(body) >= 0 and int(body) <= 6):
                                                                                                                                        if (bo_fusions[0] is None) or (int(bo_fusions[0]) >= 0 and int(bo_fusions[0]) <= 5):
                                                                                                                                            if (bo_fusions[1] is None) or (int(bo_fusions[1]) >= 0 and int(bo_fusions[1]) <= 5):
                                                                                                                                                if (bo_fusions[2] is None) or (int(bo_fusions[2]) >= 0 and int(bo_fusions[2]) <= 5):
                                                                                                                                                    if (bo_fusions[3] is None) or (int(bo_fusions[3]) >= 0 and int(bo_fusions[3]) <= 5):
                                                                                                                                                        if (bo_fusions[4] is None) or (int(bo_fusions[4]) >= 0 and int(bo_fusions[4]) <= 5):
                                                                                                                                                            if (bo_fusions[5] is None) or (int(bo_fusions[5]) >= 0 and int(bo_fusions[5]) <= 5):
                                                                                                                                                                if (tires is None) or (int(tires) >= 0 and int(tires) <= 6):
                                                                                                                                                                    if (ti_fusions[0] is None) or (int(ti_fusions[0]) >= 0 and int(ti_fusions[0]) <= 5):
                                                                                                                                                                        if (ti_fusions[1] is None) or (int(ti_fusions[1]) >= 0 and int(ti_fusions[1]) <= 5):
                                                                                                                                                                            if (ti_fusions[2] is None) or (int(ti_fusions[2]) >= 0 and int(ti_fusions[2]) <= 5):
                                                                                                                                                                                if (ti_fusions[3] is None) or (int(ti_fusions[3]) >= 0 and int(ti_fusions[3]) <= 5):
                                                                                                                                                                                    if (ti_fusions[4] is None) or (int(ti_fusions[4]) >= 0 and int(ti_fusions[4]) <= 5):
                                                                                                                                                                                        if (ti_fusions[5] is None) or (int(ti_fusions[5]) >= 0 and int(ti_fusions[5]) <= 5):
                                                                                                                                                                                            if (transmission is None) or (int(transmission) >= 0 and int(transmission) <= 6):
                                                                                                                                                                                                if (tr_fusions[0] is None) or (int(tr_fusions[0]) >= 0 and int(tr_fusions[0]) <= 5):
                                                                                                                                                                                                    if (tr_fusions[1] is None) or (int(tr_fusions[1]) >= 0 and int(tr_fusions[1]) <= 5):
                                                                                                                                                                                                        if (tr_fusions[2] is None) or (int(tr_fusions[2]) >= 0 and int(tr_fusions[2]) <= 5):
                                                                                                                                                                                                            if (tr_fusions[3] is None) or (int(tr_fusions[3]) >= 0 and int(tr_fusions[3]) <= 5):
                                                                                                                                                                                                                if (tr_fusions[4] is None) or (int(tr_fusions[4]) >= 0 and int(tr_fusions[4]) <= 5):
                                                                                                                                                                                                                    if (tr_fusions[5] is None) or (int(tr_fusions[5]) >= 0 and int(tr_fusions[5]) <= 5):
                                                                                                                                                                                                                        if any([tune_id, pp, evo, engine_motor, turbo_battery, intake_inverter, nitrous_overboost, body, tires, transmission, nitrous, final_drive, tire_pressure, dyno, purpose, usage]):
                                                                                                                                                                                                                            log, status = await tunes_manager.alter_entry(tune_id, pp, evo, engine_motor, en_fusions[0], en_fusions[1], en_fusions[2], en_fusions[3], en_fusions[4], en_fusions[5], turbo_battery, tu_fusions[0], tu_fusions[1], tu_fusions[2], tu_fusions[3], tu_fusions[4], tu_fusions[5], intake_inverter, in_fusions[0], in_fusions[1], in_fusions[2], in_fusions[3], in_fusions[4], in_fusions[5], nitrous_overboost, ni_fusions[0], ni_fusions[1], ni_fusions[2], ni_fusions[3], ni_fusions[4], ni_fusions[5], body, bo_fusions[0], bo_fusions[1], bo_fusions[2], bo_fusions[3], bo_fusions[4], bo_fusions[5], tires, ti_fusions[0], ti_fusions[1], ti_fusions[2], ti_fusions[3], ti_fusions[4], ti_fusions[5], transmission, tr_fusions[0], tr_fusions[1], tr_fusions[2], tr_fusions[3], tr_fusions[4], tr_fusions[5], nitrous, final_drive, tire_pressure, dyno, purpose, usage)
                                                                                                                                                                                                                            if status:
                                                                                                                                                                                                                                await interaction.followup.send(f"Your tune was updated successfully.")
                                                                                                                                                                                                                                logger.info(f"UPDATE_TUNE - Tune updated")
                                                                                                                                                                                                                                log += f"\nUPDATE_TUNE - Tune updated"
                                                                                                                                                                                                                            else:
                                                                                                                                                                                                                                await interaction.followup.send(f"Something went wrong during the database update. Please contact the bots owner.")
                                                                                                                                                                                                                                logger.warning(f"UPDATE_TUNE - ERROR")
                                                                                                                                                                                                                                log += f"\nUPDATE_TUNE - ERROR"
                                                                                                                                                                                                                        else:
                                                                                                                                                                                                                            await interaction.followup.send("You didn't enter a single value to be altered. Please rerun the command and state which values to alter.")
                                                                                                                                                                                                                            logger.info(f"UPDATE_TUNE - User provided no values to change. exiting...")
                                                                                                                                                                                                                            log += f"\nUPDATE_TUNE - User provided no values to change. exiting..."
                                                                                                                                                                                                                    else:
                                                                                                                                                                                                                        await interaction.followup.send(f"Your specified value for trasmission stage 6 fusions is not a valid integer between 0 and 5.")
                                                                                                                                                                                                                        logger.info(f"UPDATE_TUNE - Error in transmission variable: {tr_fusions[5]}")
                                                                                                                                                                                                                        log += f"\nUPDATE_TUNE - Error in transmission variable: {tr_fusions[5]}"
                                                                                                                                                                                                                else:
                                                                                                                                                                                                                    await interaction.followup.send(f"Your specified value for trasmission stage 5 fusions is not a valid integer between 0 and 5.")
                                                                                                                                                                                                                    logger.info(f"UPDATE_TUNE - Error in transmission variable: {tr_fusions[4]}")
                                                                                                                                                                                                                    log += f"\nUPDATE_TUNE - Error in transmission variable: {tr_fusions[4]}"
                                                                                                                                                                                                            else:
                                                                                                                                                                                                                await interaction.followup.send(f"Your specified value for trasmission stage 4 fusions is not a valid integer between 0 and 5.")
                                                                                                                                                                                                                logger.info(f"UPDATE_TUNE - Error in transmission variable: {tr_fusions[3]}")
                                                                                                                                                                                                                log += f"\nUPDATE_TUNE - Error in transmission variable: {tr_fusions[3]}"
                                                                                                                                                                                                        else:
                                                                                                                                                                                                            await interaction.followup.send(f"Your specified value for trasmission stage 3 fusions is not a valid integer between 0 and 5.")
                                                                                                                                                                                                            logger.info(f"UPDATE_TUNE - Error in transmission variable: {tr_fusions[2]}")
                                                                                                                                                                                                            log += f"\nUPDATE_TUNE - Error in transmission variable: {tr_fusions[2]}"
                                                                                                                                                                                                    else:
                                                                                                                                                                                                        await interaction.followup.send(f"Your specified value for trasmission stage 2 fusions is not a valid integer between 0 and 5.")
                                                                                                                                                                                                        logger.info(f"UPDATE_TUNE - Error in transmission variable: {tr_fusions[1]}")
                                                                                                                                                                                                        log += f"\nUPDATE_TUNE - Error in transmission variable: {tr_fusions[1]}"
                                                                                                                                                                                                else:
                                                                                                                                                                                                    await interaction.followup.send(f"Your specified value for trasmission stage 1 fusions is not a valid integer between 0 and 5.")
                                                                                                                                                                                                    logger.info(f"UPDATE_TUNE - Error in transmission variable: {tr_fusions[0]}")
                                                                                                                                                                                                    log += f"\nUPDATE_TUNE - Error in transmission variable: {tr_fusions[0]}"
                                                                                                                                                                                            else:
                                                                                                                                                                                                await interaction.followup.send(f"Your specified value for trasmission is not a valid integer between 0 and 6.")
                                                                                                                                                                                                logger.info(f"UPDATE_TUNE - Error in transmission variable: {transmission}")
                                                                                                                                                                                                log += f"\nUPDATE_TUNE - Error in transmission variable: {transmission}"
                                                                                                                                                                                        else:
                                                                                                                                                                                            await interaction.followup.send(f"Your specified value for tires stage 6 fusions is not a valid integer between 0 and 5.")
                                                                                                                                                                                            logger.info(f"UPDATE_TUNE - Error in transmission variable: {ti_fusions[5]}")
                                                                                                                                                                                            log += f"\nUPDATE_TUNE - Error in transmission variable: {ti_fusions[5]}"
                                                                                                                                                                                    else:
                                                                                                                                                                                        await interaction.followup.send(f"Your specified value for tires stage 5 fusions is not a valid integer between 0 and 5.")
                                                                                                                                                                                        logger.info(f"UPDATE_TUNE - Error in transmission variable: {ti_fusions[4]}")
                                                                                                                                                                                        log += f"\nUPDATE_TUNE - Error in transmission variable: {ti_fusions[4]}"
                                                                                                                                                                                else:
                                                                                                                                                                                    await interaction.followup.send(f"Your specified value for tires stage 4 fusions is not a valid integer between 0 and 5.")
                                                                                                                                                                                    logger.info(f"UPDATE_TUNE - Error in transmission variable: {ti_fusions[3]}")
                                                                                                                                                                                    log += f"\nUPDATE_TUNE - Error in transmission variable: {ti_fusions[3]}"
                                                                                                                                                                            else:
                                                                                                                                                                                await interaction.followup.send(f"Your specified value for tires stage 3 fusions is not a valid integer between 0 and 5.")
                                                                                                                                                                                logger.info(f"UPDATE_TUNE - Error in transmission variable: {ti_fusions[2]}")
                                                                                                                                                                                log += f"\nUPDATE_TUNE - Error in transmission variable: {ti_fusions[2]}"
                                                                                                                                                                        else:
                                                                                                                                                                            await interaction.followup.send(f"Your specified value for tires stage 2 fusions is not a valid integer between 0 and 5.")
                                                                                                                                                                            logger.info(f"UPDATE_TUNE - Error in transmission variable: {ti_fusions[1]}")
                                                                                                                                                                            log += f"\nUPDATE_TUNE - Error in transmission variable: {ti_fusions[1]}"
                                                                                                                                                                    else:
                                                                                                                                                                        await interaction.followup.send(f"Your specified value for tires stage 1 fusions is not a valid integer between 0 and 5.")
                                                                                                                                                                        logger.info(f"UPDATE_TUNE - Error in transmission variable: {ti_fusions[0]}")
                                                                                                                                                                        log += f"\nUPDATE_TUNE - Error in transmission variable: {ti_fusions[0]}"
                                                                                                                                                                else:
                                                                                                                                                                    await interaction.followup.send(f"Your specified value for tires is not a valid integer between 0 and 6.")
                                                                                                                                                                    logger.info(f"UPDATE_TUNE - Error in tires variable: {tires}")
                                                                                                                                                                    log += f"\nUPDATE_TUNE - Error in tires variable: {tires}"
                                                                                                                                                            else:
                                                                                                                                                                await interaction.followup.send(f"Your specified value for body stage 6 fusions is not a valid integer between 0 and 5.")
                                                                                                                                                                logger.info(f"UPDATE_TUNE - Error in transmission variable: {bo_fusions[5]}")
                                                                                                                                                                log += f"\nUPDATE_TUNE - Error in transmission variable: {bo_fusions[5]}"
                                                                                                                                                        else:
                                                                                                                                                            await interaction.followup.send(f"Your specified value for body stage 5 fusions is not a valid integer between 0 and 5.")
                                                                                                                                                            logger.info(f"UPDATE_TUNE - Error in transmission variable: {bo_fusions[4]}")
                                                                                                                                                            log += f"\nUPDATE_TUNE - Error in transmission variable: {bo_fusions[4]}"
                                                                                                                                                    else:
                                                                                                                                                        await interaction.followup.send(f"Your specified value for body stage 4 fusions is not a valid integer between 0 and 5.")
                                                                                                                                                        logger.info(f"UPDATE_TUNE - Error in transmission variable: {bo_fusions[3]}")
                                                                                                                                                        log += f"\nUPDATE_TUNE - Error in transmission variable: {bo_fusions[3]}"
                                                                                                                                                else:
                                                                                                                                                    await interaction.followup.send(f"Your specified value for body stage 3 fusions is not a valid integer between 0 and 5.")
                                                                                                                                                    logger.info(f"UPDATE_TUNE - Error in transmission variable: {bo_fusions[2]}")
                                                                                                                                                    log += f"\nUPDATE_TUNE - Error in transmission variable: {bo_fusions[2]}"
                                                                                                                                            else:
                                                                                                                                                await interaction.followup.send(f"Your specified value for body stage 2 fusions is not a valid integer between 0 and 5.")
                                                                                                                                                logger.info(f"UPDATE_TUNE - Error in transmission variable: {bo_fusions[1]}")
                                                                                                                                                log += f"\nUPDATE_TUNE - Error in transmission variable: {bo_fusions[1]}"
                                                                                                                                        else:
                                                                                                                                            await interaction.followup.send(f"Your specified value for body stage 1 fusions is not a valid integer between 0 and 5.")
                                                                                                                                            logger.info(f"UPDATE_TUNE - Error in transmission variable: {bo_fusions[0]}")
                                                                                                                                            log += f"\nUPDATE_TUNE - Error in transmission variable: {bo_fusions[0]}"
                                                                                                                                    else:
                                                                                                                                        await interaction.followup.send(f"Your specified value for body is not a valid integer between 0 and 6.")
                                                                                                                                        logger.info(f"UPDATE_TUNE - Error in body variable: {body}")
                                                                                                                                        log += f"\nUPDATE_TUNE - Error in body variable: {body}"
                                                                                                                                else:
                                                                                                                                    await interaction.followup.send(f"Your specified value for nitrous_overboost stage 6 fusions is not a valid integer between 0 and 5.")
                                                                                                                                    logger.info(f"UPDATE_TUNE - Error in transmission variable: {ni_fusions[5]}")
                                                                                                                                    log += f"\nUPDATE_TUNE - Error in transmission variable: {ni_fusions[5]}"
                                                                                                                            else:
                                                                                                                                await interaction.followup.send(f"Your specified value for nitrous_overboost stage 5 fusions is not a valid integer between 0 and 5.")
                                                                                                                                logger.info(f"UPDATE_TUNE - Error in transmission variable: {ni_fusions[4]}")
                                                                                                                                log += f"\nUPDATE_TUNE - Error in transmission variable: {ni_fusions[4]}"
                                                                                                                        else:
                                                                                                                            await interaction.followup.send(f"Your specified value for nitrous_overboost stage 4 fusions is not a valid integer between 0 and 5.")
                                                                                                                            logger.info(f"UPDATE_TUNE - Error in transmission variable: {ni_fusions[3]}")
                                                                                                                            log += f"\nUPDATE_TUNE - Error in transmission variable: {ni_fusions[3]}"
                                                                                                                    else:
                                                                                                                        await interaction.followup.send(f"Your specified value for nitrous_overboost stage 3 fusions is not a valid integer between 0 and 5.")
                                                                                                                        logger.info(f"UPDATE_TUNE - Error in transmission variable: {ni_fusions[2]}")
                                                                                                                        log += f"\nUPDATE_TUNE - Error in transmission variable: {ni_fusions[2]}"
                                                                                                                else:
                                                                                                                    await interaction.followup.send(f"Your specified value for nitrous_overboost stage 2 fusions is not a valid integer between 0 and 5.")
                                                                                                                    logger.info(f"UPDATE_TUNE - Error in transmission variable: {ni_fusions[1]}")
                                                                                                                    log += f"\nUPDATE_TUNE - Error in transmission variable: {ni_fusions[1]}"
                                                                                                            else:
                                                                                                                await interaction.followup.send(f"Your specified value for nitrous_overboost stage 1 fusions is not a valid integer between 0 and 5.")
                                                                                                                logger.info(f"UPDATE_TUNE - Error in transmission variable: {ni_fusions[0]}")
                                                                                                                log += f"\nUPDATE_TUNE - Error in transmission variable: {ni_fusions[0]}"
                                                                                                        else:
                                                                                                            await interaction.followup.send(f"Your specified value for nitrous_overboost is not a valid integer between 0 and 6.")
                                                                                                            logger.info(f"UPDATE_TUNE - Error in nitrous_overboost variable: {nitrous_overboost}")
                                                                                                            log += f"\nUPDATE_TUNE - Error in nitrous_overboost variable: {nitrous_overboost}"
                                                                                                    else:
                                                                                                            await interaction.followup.send(f"Your specified value for intake_inverter stage 6 fusions is not a valid integer between 0 and 5.")
                                                                                                            logger.info(f"UPDATE_TUNE - Error in transmission variable: {in_fusions[5]}")
                                                                                                            log += f"\nUPDATE_TUNE - Error in transmission variable: {in_fusions[5]}"
                                                                                                else:
                                                                                                    await interaction.followup.send(f"Your specified value for intake_inverter stage 5 fusions is not a valid integer between 0 and 5.")
                                                                                                    logger.info(f"UPDATE_TUNE - Error in transmission variable: {in_fusions[4]}")
                                                                                                    log += f"\nUPDATE_TUNE - Error in transmission variable: {in_fusions[4]}"
                                                                                            else:
                                                                                                await interaction.followup.send(f"Your specified value for intake_inverter stage 4 fusions is not a valid integer between 0 and 5.")
                                                                                                logger.info(f"UPDATE_TUNE - Error in transmission variable: {in_fusions[3]}")
                                                                                                log += f"\nUPDATE_TUNE - Error in transmission variable: {in_fusions[3]}"
                                                                                        else:
                                                                                            await interaction.followup.send(f"Your specified value for intake_inverter stage 3 fusions is not a valid integer between 0 and 5.")
                                                                                            logger.info(f"UPDATE_TUNE - Error in transmission variable: {in_fusions[2]}")
                                                                                            log += f"\nUPDATE_TUNE - Error in transmission variable: {in_fusions[2]}"
                                                                                    else:
                                                                                        await interaction.followup.send(f"Your specified value for intake_inverter stage 2 fusions is not a valid integer between 0 and 5.")
                                                                                        logger.info(f"UPDATE_TUNE - Error in transmission variable: {in_fusions[1]}")
                                                                                        log += f"\nUPDATE_TUNE - Error in transmission variable: {in_fusions[1]}"
                                                                                else:
                                                                                    await interaction.followup.send(f"Your specified value for intake_inverter stage 1 fusions is not a valid integer between 0 and 5.")
                                                                                    logger.info(f"UPDATE_TUNE - Error in transmission variable: {in_fusions[0]}")
                                                                                    log += f"\nUPDATE_TUNE - Error in transmission variable: {in_fusions[0]}"
                                                                            else:
                                                                                await interaction.followup.send(f"Your specified value for intake_inverter is not a valid integer between 0 and 6.")
                                                                                logger.info(f"UPDATE_TUNE - Error in intake_inverter variable: {intake_inverter}")
                                                                                log += f"\nUPDATE_TUNE - Error in intake_inverter variable: {intake_inverter}"
                                                                        else:
                                                                            await interaction.followup.send(f"Your specified value for turbo_battery stage 6 fusions is not a valid integer between 0 and 5.")
                                                                            logger.info(f"UPDATE_TUNE - Error in transmission variable: {tu_fusions[5]}")
                                                                            log += f"\nUPDATE_TUNE - Error in transmission variable: {tu_fusions[5]}"
                                                                    else:
                                                                        await interaction.followup.send(f"Your specified value for turbo_battery stage 5 fusions is not a valid integer between 0 and 5.")
                                                                        logger.info(f"UPDATE_TUNE - Error in transmission variable: {tu_fusions[4]}")
                                                                        log += f"\nUPDATE_TUNE - Error in transmission variable: {tu_fusions[4]}"
                                                                else:
                                                                    await interaction.followup.send(f"Your specified value for turbo_battery stage 4 fusions is not a valid integer between 0 and 5.")
                                                                    logger.info(f"UPDATE_TUNE - Error in transmission variable: {tu_fusions[3]}")
                                                                    log += f"\nUPDATE_TUNE - Error in transmission variable: {tu_fusions[3]}"
                                                            else:
                                                                await interaction.followup.send(f"Your specified value for turbo_battery stage 3 fusions is not a valid integer between 0 and 5.")
                                                                logger.info(f"UPDATE_TUNE - Error in transmission variable: {tu_fusions[2]}")
                                                                log += f"\nUPDATE_TUNE - Error in transmission variable: {tu_fusions[2]}"
                                                        else:
                                                            await interaction.followup.send(f"Your specified value for turbo_battery stage 2 fusions is not a valid integer between 0 and 5.")
                                                            logger.info(f"UPDATE_TUNE - Error in transmission variable: {tu_fusions[1]}")
                                                            log += f"\nUPDATE_TUNE - Error in transmission variable: {tu_fusions[1]}"
                                                    else:
                                                        await interaction.followup.send(f"Your specified value for turbo_battery stage 1 fusions is not a valid integer between 0 and 5.")
                                                        logger.info(f"UPDATE_TUNE - Error in transmission variable: {tu_fusions[0]}")
                                                        log += f"\nUPDATE_TUNE - Error in transmission variable: {tu_fusions[0]}"
                                                else:
                                                    await interaction.followup.send(f"Your specified value for turbo_battery is not a valid integer between 0 and 6.")
                                                    logger.info(f"UPDATE_TUNE - Error in turbo_battery variable: {turbo_battery}")
                                                    log += f"\nUPDATE_TUNE - Error in turbo_battery variable: {turbo_battery}"
                                            else:
                                                await interaction.followup.send(f"Your specified value for engine_motor stage 6 fusions is not a valid integer between 0 and 5.")
                                                logger.info(f"UPDATE_TUNE - Error in transmission variable: {en_fusions[5]}")
                                                log += f"\nUPDATE_TUNE - Error in transmission variable: {en_fusions[5]}"
                                        else:
                                            await interaction.followup.send(f"Your specified value for engine_motor stage 5 fusions is not a valid integer between 0 and 5.")
                                            logger.info(f"UPDATE_TUNE - Error in transmission variable: {en_fusions[4]}")
                                            log += f"\nUPDATE_TUNE - Error in transmission variable: {en_fusions[4]}"
                                    else:
                                        await interaction.followup.send(f"Your specified value for engine_motor stage 4 fusions is not a valid integer between 0 and 5.")
                                        logger.info(f"UPDATE_TUNE - Error in transmission variable: {en_fusions[3]}")
                                        log += f"\nUPDATE_TUNE - Error in transmission variable: {en_fusions[3]}"
                                else:
                                    await interaction.followup.send(f"Your specified value for engine_motor stage 3 fusions is not a valid integer between 0 and 5.")
                                    logger.info(f"UPDATE_TUNE - Error in transmission variable: {en_fusions[2]}")
                                    log += f"\nUPDATE_TUNE - Error in transmission variable: {en_fusions[2]}"
                            else:
                                await interaction.followup.send(f"Your specified value for engine_motor stage 2 fusions is not a valid integer between 0 and 5.")
                                logger.info(f"UPDATE_TUNE - Error in transmission variable: {en_fusions[1]}")
                                log += f"\nUPDATE_TUNE - Error in transmission variable: {en_fusions[1]}"
                        else:
                            await interaction.followup.send(f"Your specified value for engine_motor stage 1 fusions is not a valid integer between 0 and 5.")
                            logger.info(f"UPDATE_TUNE - Error in transmission variable: {en_fusions[0]}")
                            log += f"\nUPDATE_TUNE - Error in transmission variable: {en_fusions[0]}"
                    else:
                        await interaction.followup.send(f"Your specified value for engine_motor is not a valid integer between 0 and 6.")
                        logger.info(f"UPDATE_TUNE - Error in engine_motor variable: {engine_motor}")
                        log += f"\nUPDATE_TUNE - Error in engine_motor variable: {engine_motor}"
                else:
                    await interaction.followup.send(f"Your specified value for evo is not a valid integer.")
                    logger.info(f"UPDATE_TUNE - Error in evo variable: {evo}")
                    log += f"\nUPDATE_TUNE - Error in evo variable: {evo}"
            else:
                await interaction.followup.send(f"Your specified value for pp is not a valid integer.")
                logger.info(f"UPDATE_TUNE - Error in pp variable: {pp}")
                log += f"\nUPDATE_TUNE - Error in pp variable: {pp}"
        else:
            await interaction.followup.send("You are not the owner of this Tune. You can only update your own tunes. Please enter a TuneID of one of your tunes.")
            logger.info(f"UPDATE_TUNE - User is not owner of the tune to edit")
            log += f"\nUPDATE_TUNE - User is not owner of the tune to edit"
        await in_app_logging.send_log(self.bot, log, 2, 1, interaction)

    @app_commands.command(name="csr2_delete_tune", description="Delete one of your submitted tunes.")
    @discord.app_commands.describe(tune_id="An unique identifier integer provided to you when you created your tune and needed to point at the tune you want to edit")
    async def delete_tune(self, interaction: discord.Interaction, tune_id: int):
        logger.info(f"DELETE_TUNE - The following command has been used: /csr2_delete_tune tune_id: {tune_id}")
        log = f"DELETE_TUNE - The following command has been used: /csr2_delete_tune tune_id: {tune_id}"
        await interaction.response.defer()

        NITRO = await helpers.load_super_admin()

        user = str(f"{interaction.user.id}")
        owner = await tunes_manager.get_creator_by_tune_id(tune_id)

        if (owner is not None and owner[0] is None):
            await interaction.followup.send("The TuneID you entered does not exist. Please enter a valid TuneID and try again.")
        elif ((owner is not None and user == owner[0]) or user == NITRO):
            await tunes_manager.remove_entry(tune_id)
            result = await tunes_manager.search_tune_id(tune_id)
            if result:
                await interaction.followup.send("Something went wrong during the deletion process. Please try again. If this issue persists, please message the bot's owner.")
                logger.warning(f"DELETE_TUNE - ERROR")
                log += f"\nDELETE_TUNE - ERROR"
            else:
                await interaction.followup.send("Your tune was deleted as per your request.")
                logger.info(f"DELETE_TUNE - Tune was deleted successfully")
                log += f"\nDELETE_TUNE - Tune was deleted successfully"
        else:
            await interaction.followup.send("You are not the owner of this Tune. You can only delete your own tunes. Please enter a TuneID of one of your tunes.")
            logger(f"DELETE_TUNE - User is not owner of the tune to edit")
            log += f"\nDELETE_TUNE - User is not owner of the tune to edit"
        await in_app_logging.send_log(self.bot, log, 2, 1, interaction)

    @app_commands.command(name="csr2_community_tune", description="❗Select one more variable from above❗ Search for CSR2 tunes submitted by the community")
    @discord.app_commands.describe(tune_id="An unique identifier integer provided to you when you created your tune and needed to point at the tune you want to edit", car="Name or DB name of the car you want to search a community tune for", tier="Select an option from Above", rarity="Select an option from Above", purpose="The use case you want to search a tune for", creator="The creator of the tune you want to search for")
    @app_commands.choices(rarity=[app_commands.Choice(name="5 Gold Stars", value="5 G"), app_commands.Choice(name="5 Purple Stars", value="5 P"), app_commands.Choice(name="5 Stars", value="5"), app_commands.Choice(name="4 Gold Stars", value="4 G"), app_commands.Choice(name="4 Purple Stars", value="4 P"), app_commands.Choice(name="4 Stars", value="4"), app_commands.Choice(name="3 Gold Stars", value="3 G"), app_commands.Choice(name="3 Purple Stars", value="3 P"), app_commands.Choice(name="3 Stars", value="3"), app_commands.Choice(name="2 Gold Stars", value="2 G"), app_commands.Choice(name="2 Purple Stars", value="2 P"), app_commands.Choice(name="2 Stars", value="2"), app_commands.Choice(name="1 Gold Stars", value="1 G"), app_commands.Choice(name="1 Purple Stars", value="1 P"), app_commands.Choice(name="1 Stars", value="1"), app_commands.Choice(name="Gold Star", value="G"), app_commands.Choice(name="Purple Star", value="P"), app_commands.Choice(name="Non Star", value="0")])
    @app_commands.choices(tier=[app_commands.Choice(name="Tier 5/T5", value="T5"), app_commands.Choice(name="Tier 4/T4", value="T4"), app_commands.Choice(name="Tier 3/T3", value="T3"), app_commands.Choice(name="Tier 2/T2", value="T2"), app_commands.Choice(name="Tier 1/T1", value="T1")])
    async def community_tunes(self, interaction: discord.Interaction, car: str = None, tune_id: int = None, tier: str = None, rarity: str = None, purpose: str = None, creator: str = None):
        logger.info(f"COMMUNITY_TUNE - The following command has been used: /csr2_community_tune car: {car} tune_id: {tune_id} tier: {tier} rarity: {rarity} purpose: {purpose} creator: {creator}")
        log = f"COMMUNITY_TUNE - The following command has been used: /csr2_community_tune car: {car} tune_id: {tune_id} tier: {tier} rarity: {rarity} purpose: {purpose} creator: {creator}"
        await interaction.response.defer()

        if any([car, tune_id, tier, rarity, purpose, creator]):
            results = await tunes_manager.query_tune(car, tune_id, tier, rarity, purpose, creator)
        else:
            await interaction.followup.send("You selected no search arguments. Please run the command again and provide search arguments.")

        if results:
            logger.info(f"COMMUNITY_TUNE - {len(results)} results found")
            log += f"\nCOMMUNITY_TUNE - {len(results)} results found"
            LIMIT_FILE = await helpers.load_file_path('limits')
            if interaction.guild:
                async with aiofiles.open(LIMIT_FILE, 'r') as file:
                    limits = json.loads(await file.read())
                limit = limits.get(str(interaction.guild.id), {"PostLimit": 0})["PostLimit"]
                logger.info(f"COMMUNITY_TUNE - Limit on {interaction.guild.name} ({interaction.guild.id}): {limit}")
                log += f"\nCOMMUNITY_TUNE - Limit on {interaction.guild.name} ({interaction.guild.id}): {limit}"
            else:
                limit = 0
                logger.info(f"COMMUNITY_TUNE - Limit in DM's is infinite")
                log += f"\nCOMMUNITY_TUNE - Limit in DM's is infinite"

            if limit == 0 or len(results) <= limit:
                logger.info("COMMUNITY_TUNE - Sending in Channel")
                log += f"\nCOMMUNITY_TUNE - Sending in Channel"
                log = await self.send_tunes_in_channel(interaction, results, log)
            else:
                logger.info("COMMUNITY_TUNE - Sending in DMs")
                log = f"COMMUNITY_TUNE - Sending in DMs"
                log = await self.send_tunes_in_dm(interaction, results, log)
        else:
            await interaction.followup.send("Your search returned no results. Please try again with different search arguments.")
            logger.info(f"COMMUNITY_TUNE - No results found for query")
            log += f"\nCOMMUNITY_TUNE - No results found for query"

    async def submission_loop(self, interaction: discord.Interaction, log: str, fusions = None):
        await interaction.user.send("Starting submission loop. You can cancel your submission at any time by typing exactly `CANCEL`")

        self.active_submissions[interaction.user.id] = interaction.user

        cars = await tunes_manager.pull_available_cars()
        cars_with_index = [(i+1, car) for i, car in enumerate(cars)]
        chunks = [cars_with_index[i:i + 20] for i in range(0, len(cars_with_index), 20)]
        current_page = 0

        await self.send_car_selection_embed(interaction.user, chunks, current_page, log, fusions)

        response = await self.bot.wait_for('message', check=lambda m: m.author == interaction.user)
        if response.content.upper() == "CANCEL":
            await interaction.user.send("Submission cancelled. If you need to start again, use </csr2_share_tune:1276579292687630358> again.")
            self.active_submissions.pop(interaction.user.id, None)
            logger.info(f"SHARE_TUNE - Submission canceled")
            log += f"\nSHARE_TUNE - Submission canceled"
            await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
            return log

    def sub_questions(self, part_counter: int):
        parts = [
            "Engine/Motor",
            "Turbo/Battery",
            "Intake/Inverter",
            "Nitrous/Overboost",
            "Body",
            "Tires",
            "Transmission"
        ]
        sub_questions = [
            f"How many fusions have you installed on your Stage 1  {parts[part_counter-2]}",
            f"How many fusions have you installed on your Stage 2  {parts[part_counter-2]}",
            f"How many fusions have you installed on your Stage 3  {parts[part_counter-2]}",
            f"How many fusions have you installed on your Stage 4  {parts[part_counter-2]}",
            f"How many fusions have you installed on your Stage 5  {parts[part_counter-2]}",
            f"How many fusions have you installed on your Stage 6  {parts[part_counter-2]}",
        ]

        return sub_questions

    async def send_car_selection_embed(self, user, chunks, page, log, fusions=None):
        embed = await self.create_car_embed(chunks, page)
        view = CarSelectionView(chunks, page, user, self, log, fusions)
        self.car_message = await user.send(embed=embed, view=view)

    async def create_car_embed(self, chunks, page):
        embed = discord.Embed(
            title="Choose a car!",
            description="\n".join([f"{idx + 1}. {car[1][1]} ({await helpers.emojify_tier(car[1][2])} {await helpers.emojify_rarity(car[1][3])})" for idx, car in enumerate(chunks[page])]),
            color=discord.Color(0xff00ff)
        )
        embed.set_footer(text=f"Page {page + 1} of {len(chunks)}")
        embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')

        return embed

    async def handle_car_selection(self, interaction: discord.Interaction, car_data: list, log: str, fusions: int):
        logger.info(f"SHARE_TUNE - Car selected: {car_data}")
        log += f"\nSHARE_TUNE - Car selected: {car_data}"
        car = car_data[1]
        ign = car[1]
        tier = car[2]
        stars = car[3]

        selection_message = f"You selected: {ign} (Tier: {tier}, Stars: {stars})\n\nDo you want to confirm this selection?"
        view = ConfirmSelectionView(self, car, log, fusions)
        await interaction.response.send_message(selection_message, view=view)

        return log

    async def ask_questions(self, user, car, interaction: discord.Interaction, log: str, fusions: int):
        questions = [
            "How much PP does your tune have? Provide just the number!",
            "How much Evo does your tune have? Provide just the number!",
            "What stage of Engine/Motor upgrade is installed? Provide just the number!",
            "What stage of Turbo/Battery upgrade is installed? Provide just the number!",
            "What stage of Intake/Inverter upgrade is installed? Provide just the number!",
            "What stage of Nitrous/Overboost upgrade is installed? Provide just the number!",
            "What stage of Body upgrade is installed? Provide just the number!",
            "What stage of Tires upgrade is installed? Provide just the number!",
            "What stage of Transmission upgrade is installed? Provide just the number!",
            "What is your Nitrous Tuning setup? Format: <power>/duration Example: `188/4.0` If you don't have access to this part of tuning type `none`!",
            "What is your Final Drive Tuning setup? Format: x.xx Example: `3.49` If you don't have access to this part of tuning type `none`!",
            "What is your Tire Pressure Tuning setup? Format: <acceleration>/<grip> Example: `0/100` If you don't have access to this part of tuning type `none`!",
            "What is your Tuning setup's Dyno time format: x.xxx Example `12.040` If you don't have access to this part of tuning type `none`!",
            "What is the purpose of your setup? Good statements are Live Racing, Story, Tempest, Speedtraps, Sprint Races, WEC, Live Bots, etc.",
            "Give a short but good explanation of how to use your tune. When should you shift into each gear? When should you activate Nitrous? Are downshifts needed? Anything that you think is needed to use the setup like you use it."
        ]

        user_answers = {}
        noq = 0

        for idx, question in enumerate(questions):
            valid = False
            while valid == False:
                await user.send(question)
                response = await self.bot.wait_for('message', check=lambda m: m.author == user)
                if response.content.upper() == "CANCEL":
                    return log
                logger.info(f"SHARE_TUNE - {idx}: {response.content}")
                log += f"\nSHARE_TUNE - {idx}: {response.content}"
                input, valid = await self.validate_input(response.content, user, idx, None)
                if valid == True:
                    user_answers[noq] = input
                    noq = noq + 1
                    logger.info(f"SHARE_TUNE - {user_answers}")
                    log += f"SHARE_TUNE - {user_answers}"
                    await asyncio.sleep(0.1)

                    if 2 <= idx <= 8:
                        fitted_stages = int(input)
                        sub_questions = self.sub_questions(idx)
                        for index, sub_question in enumerate(sub_questions):
                            valid = False
                            while valid == False:
                                if fusions == 1:
                                    input = "All"
                                    valid = True
                                elif (fusions == 2 or index >= fitted_stages):
                                    input = "0"
                                    valid = True
                                else:
                                    await user.send(sub_question)
                                    response = await self.bot.wait_for('message', check=lambda m: m.author == user)
                                    if response.content.upper() == "CANCEL":
                                        await interaction.user.send("Submission cancelled. If you need to start again, use `/csr2_share_tune` again.")
                                        self.active_submissions.pop(interaction.user.id, None)
                                        logger.info(f"SHARE_TUNE - Submission canceled")
                                        log += f"\nSHARE_TUNE - Submission canceled"
                                        await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
                                    logger.info(f"{index}: {response.content}")
                                    log += f"\n{index}: {response.content}"
                                    input, valid = await self.validate_input(response.content, user, None, index)
                                if valid == True:
                                    user_answers[noq] = input
                                    noq = noq + 1
                                    logger.info(f"{user_answers}")
                                    await asyncio.sleep(0.1)
        log += f"\n{user_answers}"

        await user.send("Thank you for providing your information. Your submission is complete.")

        dbn = car[0]
        ign = car[1]
        tier = car[2]
        stars = car[3]
        user_name = user.display_name
        user_id = user.id

        tune_id, log = await tunes_manager.add_entry(dbn, ign, tier, stars, user_answers.get(0), user_answers.get(1), user_answers.get(2), user_answers.get(3), user_answers.get(4), user_answers.get(5), user_answers.get(6), user_answers.get(7), user_answers.get(8), user_answers.get(9), user_answers.get(10), user_answers.get(11), user_answers.get(12), user_answers.get(13), user_answers.get(14), user_answers.get(15), user_answers.get(16), user_answers.get(17), user_answers.get(18), user_answers.get(19), user_answers.get(20), user_answers.get(21), user_answers.get(22), user_answers.get(23), user_answers.get(24), user_answers.get(25), user_answers.get(26), user_answers.get(27), user_answers.get(28), user_answers.get(29), user_answers.get(30), user_answers.get(31), user_answers.get(32), user_answers.get(33), user_answers.get(34), user_answers.get(35), user_answers.get(36), user_answers.get(37), user_answers.get(38), user_answers.get(39), user_answers.get(40), user_answers.get(41), user_answers.get(42), user_answers.get(43), user_answers.get(44), user_answers.get(45), user_answers.get(46), user_answers.get(47), user_answers.get(48), user_answers.get(49), user_answers.get(50), user_answers.get(51), user_answers.get(52), user_answers.get(53), user_answers.get(54), user_answers.get(55), user_answers.get(56), user_name, user_id, log)
        await user.send(f"This tune's unique TuneID is: {tune_id}. Remember it to edit or delete it in the future.")
        results = await tunes_manager.query_tune(car = None, tune_id = tune_id, tier = None, rarity = None, purpose = None, creator = None)

        self.active_submissions.pop(user.id, None)
        await self.send_tunes_in_dm(interaction, results, log)

        return log
    
    async def validate_input(self, response: str, user: discord.User, idx: int, index: int):
        if idx is not None:
            if idx < 2:
                if response.isdigit():
                    valid = True
                else:
                    valid = False
                    await user.send(f"Please provide a valid number (integer) for question this question.")
            elif 2 <= idx <= 8:
                if (response.isdigit() and 0 <= int(response) <= 6):
                    valid = True
                else:
                    valid = False
                    await user.send(f"Please provide a valid number (integer) between 0 and 6 for question this question.")
            elif 9 <= idx <= 12:
                if response.lower() == "none":
                    response = None
                valid = True
            elif 13 <= idx <= 14:
                valid = True
        elif index is not None:
            if (response.isdigit() and 0 <= int(response) <= 5):
                valid = True
            else:
                valid = False
                await user.send(f"Please provide a valid integer between 0 and 5 for this question.")
        else:
            valid = False
            await user.send(f"Please provide a valid response for this question.")

        return response, valid

    async def send_tunes_in_channel(self, interaction: discord.Interaction, results: list, log: str):
        await interaction.followup.send("Fetching tunes, please wait...", ephemeral=True)

        messages, log = await self.construct_results(results, log)

        if messages:
            for batch in messages:
                try:
                    await interaction.followup.send(embeds=batch)
                    await asyncio.sleep(0.5)
                except discord.NotFound:
                    logger.info("COMMUNITY_TUNE - Follow-up interaction expired.")
                    log += f"\nCOMMUNITY_TUNE - Follow-up interaction expired."
                    return
            logger.info("COMMUNITY_TUNE - Results sent in Channel.")
            log += f"\nCOMMUNITY_TUNE - Results sent in Channel."

    async def send_tunes_in_dm(self, interaction: discord.Interaction, results: list, log: str):
        await interaction.followup.send("Sending results via DMs because the number of results exceeds the maximum allowed on this server.", ephemeral=True)
        user = interaction.user
        try:
            await user.send("Fetching tunes, please wait...")

            messages, log = await self.construct_results(results, log)

            if messages:
                for batch in messages:
                    try:
                        await user.send(embeds=batch)
                        await asyncio.sleep(0.5)
                    except discord.Forbidden:
                        logger.info("COMMUNITY_TUNE - DMs are closed or closed for non-friended accounts. No records will be sent. Please open your DMs and try again.")
                        log += f"\nCOMMUNITY_TUNE - DMs are closed or closed for non-friended accounts. No records will be sent. Please open your DMs and try again."
                        return
                logger.info("COMMUNITY_TUNE - Results sent in DMs.")
                log += "COMMUNITY_TUNE - Results sent in DMs."

            await asyncio.sleep(0.5)
            try:
                if interaction.guild:
                    await interaction.followup.send(f"The results were sent to you via DM.", ephemeral=True)
                await in_app_logging.send_log(self.bot, log, 2, 1, interaction)
            except discord.HTTPException as e:
                if e.status == 429:
                    logger.warning(f"COMMUNITY_TUNE - Rate Limited caught (HTTP 429)")
                    log += f"\nCOMMUNITY_TUNE - Rate Limited caught (HTTP 429)"
                    retry_after = int(e.response.headers.get('Retry-After', 5))
                    await asyncio.sleep(retry_after)
                    await interaction.followup.send(f"The results were sent to you via DM.", ephemeral=True)
                    await in_app_logging.send_log(self.bot, log, 1, 1, interaction)
        except discord.Forbidden:
            await interaction.followup.send("Unable to send DMs. Please ensure your DMs are open and try again.", ephemeral=True)
            await in_app_logging.send_log(self.bot, log, 2, 1, interaction)

    async def construct_results(self, results: list, log: str):
        logger.info("COMMUNITY_TUNE - Constructing Embeds")
        log += f"\nCOMMUNITY_TUNE - Constructing Embeds"
        messages = []
        batch = []
        for result in results:
            if not result[59]:
                result_list = list(result)
                result_list[59] = float(0.000)
                result = tuple(result_list)

            embed = discord.Embed(
                title=result[2],
                description=f"# {await helpers.emojify_tier(result[3])}   {await helpers.emojify_rarity(result[4])}",
                color=discord.Color(0xff00ff)
            )
            embed.add_field(name=f"PP: {result[5]}\nEVO: {result[6]}", value=f"", inline=False)
            embed.add_field(name="Part                                      Upgrades", value=f"`\nEngine/Motor        Stage {result[7]}\nTurbo/Battery       Stage {result[14]}\nIntake/Inverter     Stage {result[21]}\nNitrous/Overboost   Stage {result[28]}\nBody                Stage {result[35]}\nTires               Stage {result[42]}\nTransmission        Stage {result[49]}`", inline=False)
            embed.add_field(name="Part                                      Fusuions", value=f"`\n**Engine/Motor**\n - Stage 1:         {result[8]}\n - Stage 2:          {result[9]}\n - Stage 3:         {result[10]}\n - Stage 4:         {result[11]}\n - Stage 5:         {result[12]}\n - Stage 6:         {result[13]}\n**Turbo/Battery**\n - Stage 1:         {result[15]}\n - Stage 2:         {result[16]}\n - Stage 3:         {result[17]}\n - Stage 4:         {result[18]}\n - Stage 5:         {result[19]}\n - Stage 6:         {result[20]}\n**Intake/Inverter**\n - Stage 1:         {result[22]}\n - Stage 2:         {result[23]}\n - Stage 3:         {result[24]}\n - Stage 4:         {result[25]}\n - Stage 5:         {result[26]}\n - Stage 6:         {result[27]}\n", inline=False)
            embed.add_field(name=f"`Nitrous/Overboost`", value=f"` - Stage 1:         {result[29]}\n - Stage 2:         {result[30]}\n - Stage 3:         {result[31]}\n - Stage 4:         {result[32]}\n - Stage 5:         {result[33]}\n - Stage 6:         {result[34]}`\n**Body**`\n - Stage 1:         {result[36]}\n - Stage 2:         {result[37]}\n - Stage 3:         {result[38]}\n - Stage 4:         {result[39]}\n - Stage 5:         {result[40]}\n - Stage 6:         {result[41]}`\n**Tires**`\n - Stage 1:         {result[43]}\n - Stage 2:         {result[44]}\n - Stage 3:         {result[45]}\n - Stage 4:         {result[46]}\n - Stage 5:         {result[47]}\n - Stage 6:         {result[48]}`\n**Transmission**`\n - Stage 1:         {result[50]}\n - Stage 2:         {result[51]}\n - Stage 3:         {result[52]}\n - Stage 4:         {result[53]}\n - Stage 5:         {result[54]}\n - Stage 6:         {result[55]}\n`", inline=False)
            embed.add_field(name="Tuning", value=f"Nitrous: {result[56]}\nFinal Drive: {result[57]}\nTire Pressure: {result[58]}\n\nDyno: {float(result[59]):.3f}", inline=False)
            embed.add_field(name=f"Purpose: {result[60]}", value=f"**Usage**\n{result[61]}\n\n-# Creator: {result[62]} ({result[63]})", inline=False)
            embed.set_footer(text=f"TuneID: {result[0]} - DB_Name: {result[1]}")
            embed.set_thumbnail(url='https://i.imgur.com/1VWi2Di.png')

            batch.append(embed)

            if len(batch) == 2:
                messages.append(batch)
                batch = []

        if batch:
            messages.append(batch)

        logger.info(f"COMMUNITY_TUNE - Embeds constructed")
        log += f"\nCOMMUNITY_TUNE - Embeds constructed"

        return messages, log

def save_fusion_selection(fusions: int):
    if fusions:
        fs = fusions
    else:
        try:
            if fs:
                return fs
        except:
            fs = 0
            return fs

class CarSelectionView(ui.View):
    def __init__(self, chunks, page, user, cog, log, fusions):
        super().__init__()
        self.chunks = chunks
        self.page = page
        self.user = user
        self.cog = cog
        self.log = log
        self.fusions = fusions

        for idx, car in enumerate(self.chunks[self.page]):
            self.add_item(CarSelectionButton(idx + 1, car, self.cog, self.log, self.fusions))

        if len(chunks) > 1:
            self.add_item(NavigationButton(label="Previous", direction=-1, page=self.page, chunks=self.chunks, user=self.user, cog=self.cog, log=self.log))
            self.add_item(NavigationButton(label="Next", direction=1, page=self.page, chunks=self.chunks, user=self.user, cog=self.cog, log=self.log))
            self.add_item(JumpToPageButton(self))  # Pass the current view

    async def on_timeout(self):
        if self.user.id in self.cog.active_submissions:
            self.cog.active_submissions.pop(self.user.id, None)
            if self.cog.car_message:
                try:
                    await self.cog.car_message.delete()
                    await self.user.send("Your car selection has timed out. If you need to start again, use `/csr2_share_tune command`.", silent=True)
                except:
                    logger.info(f"COMMUNITY_TUNE - CarSelectionView message not found")
                    self.log += f"COMMUNITY_TUNE - CarSelectionView message not found"
        self.stop()

class CarSelectionButton(ui.Button):
    def __init__(self, index, car_data, cog, log, fusions):
        super().__init__(label=str(index), style=discord.ButtonStyle.primary)
        self.car_data = car_data
        self.cog = cog
        self.log = log
        self.fusions = fusions

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id in self.cog.active_submissions:
            await self.cog.handle_car_selection(interaction, self.car_data, self.log, self.fusions)

class NavigationButton(ui.Button):
    def __init__(self, label, direction, page, chunks, user, cog, log):
        super().__init__(label=label, style=discord.ButtonStyle.secondary)
        self.direction = direction
        self.page = page
        self.chunks = chunks
        self.user = user
        self.cog = cog
        self.log = log

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await asyncio.sleep(1)

        new_page = (self.page + self.direction) % len(self.chunks)
        new_embed = await self.cog.create_car_embed(self.chunks, new_page)
        new_view = CarSelectionView(self.chunks, new_page, self.user, self.cog, self.log)
        await self.cog.car_message.edit(embed=new_embed, view=new_view)

class JumpToPageButton(ui.Button):
    def __init__(self, view):
        super().__init__(label="Jump to Page", style=discord.ButtonStyle.secondary)
        self._view = view

    @property
    def view(self):
        return self._view

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.view.user:
            return await interaction.response.send_message("You can't interact with this!", ephemeral=True)

        await interaction.response.send_modal(PageJumpModal(self.view))

class ConfirmSelectionView(ui.View):
    def __init__(self, cog, car, log, fusions):
        super().__init__()
        self.cog = cog
        self.car = car
        self.log = log
        self.fusions = fusions

        self.add_item(ConfirmButton(cog, car, log, fusions))
        self.add_item(DeclineButton(log))

    async def on_timeout(self):
        if self.user.id in self.cog.active_submissions:
            self.cog.active_submissions.pop(self.user.id, None)
            if self.cog.selection_message:
                try:
                    await self.cog.selection_message.delete()
                    await self.user.send("Your car selection has timed out. If you need to start again, use `/csr2_share_tune command`.", silent=True)
                except:
                    logger.info(f"SHARE_TUNE - ConfirmSelectionView message not found")
                    self.log += f"SHARE_TUNE - ConfirmSelectionView message not found"
        self.stop()

class ConfirmButton(ui.Button):
    def __init__(self, cog, car, log, fusions):
        super().__init__(label="Confirm", style=discord.ButtonStyle.success)
        self.cog = cog
        self.car = car
        self.log = log
        self.fusions = fusions

    async def callback(self, interaction: discord.Interaction):
        logger.info(f"SHARE_TUNE - Car confirmed")
        self.log += f"\nSHARE_TUNE - Car confirmed"

        if self.cog.car_message:
            await self.cog.car_message.delete()

        for item in self.view.children:
            item.disabled = True

        await interaction.response.edit_message(content="Car selection confirmed! Proceeding with the next steps...")

        self.view.stop()

        self.log = await self.cog.ask_questions(interaction.user, self.car, interaction, self.log, self.fusions)
        self.cog.active_submissions.pop(interaction.user.id, None)

class DeclineButton(ui.Button):
    def __init__(self, log):
        super().__init__(label="Decline", style=discord.ButtonStyle.danger)
        self.log = log

    async def callback(self, interaction: discord.Interaction):
        await interaction.message.delete()
        logger.info("SHARE_TUNE - Car selection declined and message deleted.")
        self.log += f"\nSHARE_TUNE - Car selection declined and message deleted."

class PageJumpModal(discord.ui.Modal, title="Jump to Page"):
    page_number = discord.ui.TextInput(label="Enter Page Number or +/- Offset", required=True)

    def __init__(self, view: "CarSelectionView"):
        super().__init__()
        self.view = view

    async def on_submit(self, interaction: discord.Interaction):
        try:
            input_text = self.page_number.value.strip()

            if input_text.startswith(('+', '-')):
                offset = int(input_text)
                new_page = (self.view.page + offset) % len(self.view.chunks)
                if new_page == 0:
                    new_page = len(self.view.chunks)
            else:
                new_page = int(input_text)-1
                if new_page < 1 or new_page > len(self.view.chunks):
                    new_page = (new_page - 1) % len(self.view.chunks) + 1

            self.view.page = new_page
            new_embed = await self.view.cog.create_car_embed(self.view.chunks, self.view.page)
            new_view = CarSelectionView(self.view.chunks, self.view.page, self.view.user, self.view.cog, self.view.log, self.view.fusions)
            await interaction.response.edit_message(embed=new_embed, view=new_view)

        except ValueError:
            await interaction.response.send_message("Invalid input. Please enter a number.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ShareTuneCog(bot))
