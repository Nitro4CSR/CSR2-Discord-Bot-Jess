import asyncio
import aiosqlite
import os
from discord.ext import commands
import helpers
import in_app_logging

logger = helpers.load_logging()

table_schemas = {
    'community_tunes': [
        '"TuneID" INTEGER PRIMARY KEY AUTOINCREMENT', '"DB Name" TEXT', '"Ingame Name Clarification" TEXT', '"Un" TEXT', '"★" TEXT', '"PP" INTEGER', '"EVO" INTEGER', '"Engine/Motor" Integer', '"En_st.1" TEXT', '"En_st.2" TEXT', '"En_st.3" TEXT', '"En_st.4" TEXT', '"En_st.5" TEXT', '"En_st.6" TEXT', '"Turbo/Battery" Integer', '"Tu_st.1" TEXT', '"Tu_st.2" TEXT', '"Tu_st.3" TEXT', '"Tu_st.4" TEXT', '"Tu_st.5" TEXT', '"Tu_st.6" TEXT', '"Intake/Inverter" Integer', '"In_st.1" TEXT', '"In_st.2" TEXT', '"In_st.3" TEXT', '"In_st.4" TEXT', '"In_st.5" TEXT', '"In_st.6" TEXT', '"Nitrous/Overboost" Integer', '"Ni_st.1" TEXT', '"Ni_st.2" TEXT', '"Ni_st.3" TEXT', '"Ni_st.4" TEXT', '"Ni_st.5" TEXT', '"Ni_st.6" TEXT', '"Body" Integer', '"Bo_st.1" TEXT', '"Bo_st.2" TEXT', '"Bo_st.3" TEXT', '"Bo_st.4" TEXT', '"Bo_st.5" TEXT', '"Bo_st.6" TEXT', '"Tires" Integer', '"Ti_st.1" TEXT', '"Ti_st.2" TEXT', '"Ti_st.3" TEXT', '"Ti_st.4" TEXT', '"Ti_st.5" TEXT', '"Ti_st.6" TEXT', '"Transmission" Integer', '"Tr_st.1" TEXT', '"Tr_st.2" TEXT', '"Tr_st.3" TEXT', '"Tr_st.4" TEXT', '"Tr_st.5" TEXT', '"Tr_st.6" TEXT', '"NITRO" TEXT', '"FD" REAL', '"TIRE" TEXT', '"DYNO" REAL', '"Purpose" TEXT', '"Usage Guide" TEXT', '"Creator" TEXT', '"Creator ID" TEXT'
    ]
}

async def create_database(bot: commands.Bot, log: str):
    logger.info("TUNES - Running boot setup for tunes DB")
    log += f"TUNES - Running boot setup for tunes DB"
    TUNES_DB = await helpers.load_file_path('tunes')
    if not os.path.exists(TUNES_DB):
        logger.info("TUNES - Database not found. Creating new database...")
        log += f"TUNES - Database not found. Creating new database..."
        async with aiosqlite.connect(TUNES_DB) as conn_tunes:
            async with conn_tunes.cursor() as tunes_cursor:
                try:
                    for table_name, schema in table_schemas.items():
                        await tunes_cursor.execute(f"CREATE TABLE {table_name} ({', '.join(schema)})")
                    logger.info("TUNES - Tables created successfully.")
                    log += "TUNES - Tables created successfully."
                except aiosqlite.Error as e:
                    logger.error(f"TUNES - An error occurred while creating tables: {e}")
                    log += f"TUNES - An error occurred while creating tables: {e}"
                    await in_app_logging.send_log(bot, log, 0, 2)
                finally:
                    await conn_tunes.commit()
        await conn_tunes.close()
    else:
        logger.info("TUNES - Database already exists.")
        log += f"\nTUNES - Database already exists."
        if bot:
            await in_app_logging.send_log(bot, log, 2, 2)
        else:
            return log

async def pull_available_cars():
    DATABASE_PATH = await helpers.load_file_path('EDB')
    async with aiosqlite.connect(DATABASE_PATH) as conn_wrs:
        async with conn_wrs.cursor() as wr_cursor:
            cars_query = """
                SELECT "DB Name", "Ingame Name Clarification", "Un", "★"
                FROM records
            """
            await wr_cursor.execute(cars_query)
            cars = await wr_cursor.fetchall()

    await conn_wrs.close()

    return cars

async def get_creator_by_tune_id(tune_id):
    TUNES_DB = await helpers.load_file_path('tunes')
    values = [f"{tune_id}"]
    query = """
        SELECT "Creator ID"
        FROM community_tunes
        WHERE "TuneID" = ?
    """
    async with aiosqlite.connect(TUNES_DB) as conn_tunes:
        async with conn_tunes.cursor() as tunes_cursor:
            await tunes_cursor.execute(query, values)
            creator_id = await tunes_cursor.fetchone()

    await conn_tunes.close()

    return creator_id

async def search_tune_id(tune_id):
    TUNES_DB = await helpers.load_file_path('tunes')
    query = """
        SELECT "TuneID"
        FROM community_tunes
        WHERE "TuneID" = ?
    """
    async with aiosqlite.connect(TUNES_DB) as conn_tunes:
        async with conn_tunes.cursor() as tunes_cursor:
            await tunes_cursor.execute(query, [tune_id])
            result = await tunes_cursor.fetchone()

    await conn_tunes.close()

    return result

async def add_entry(DB_Name: str, IGN: str, tier: str, stars: str, pp: str, evo: str, u1: int, u1_s1: int, u1_s2: int, u1_s3: int, u1_s4: int, u1_s5: int, u1_s6, u2: int, u2_s1: int, u2_s2: int, u2_s3: int, u2_s4: int, u2_s5: int, u2_s6, u3: int, u3_s1: int, u3_s2: int, u3_s3: int, u3_s4: int, u3_s5: int, u3_s6, u4: int, u4_s1: int, u4_s2: int, u4_s3: int, u4_s4: int, u4_s5: int, u4_s6, u5: int, u5_s1: int, u5_s2: int, u5_s3: int, u5_s4: int, u5_s5: int, u5_s6, u6: int, u6_s1: int, u6_s2: int, u6_s3: int, u6_s4: int, u6_s5: int, u6_s6, u7: int, u7_s1: int, u7_s2: int, u7_s3: int, u7_s4: int, u7_s5: int, u7_s6, nos: str, fd: str, tp: str, dyno: str, purpose: str, usage: str, creator: str, creatorID: str, log: str):
    TUNES_DB = await helpers.load_file_path('tunes')
    log = await create_database(None, log)
    async with aiosqlite.connect(TUNES_DB) as conn_tunes:
        async with conn_tunes.cursor() as tunes_cursor:
            logger.info(f"TUNES - Adding submitted tune to DataBase")

            query = """
            INSERT INTO community_tunes
            ("DB Name", "Ingame Name Clarification", "Un", "★", "PP", "EVO", "Engine/Motor", "En_st.1", "En_st.2", "En_st.3", "En_st.4", "En_st.5", "En_st.6", "Turbo/Battery", "Tu_st.1", "Tu_st.2", "Tu_st.3", "Tu_st.4", "Tu_st.5", "Tu_st.6", "Intake/Inverter", "In_st.1", "In_st.2", "In_st.3", "In_st.4", "In_st.5", "In_st.6", "Nitrous/Overboost", "Ni_st.1", "Ni_st.2", "Ni_st.3", "Ni_st.4", "Ni_st.5", "Ni_st.6", "Body", "Bo_st.1", "Bo_st.2", "Bo_st.3", "Bo_st.4", "Bo_st.5", "Bo_st.6", "Tires", "Ti_st.1", "Ti_st.2", "Ti_st.3", "Ti_st.4", "Ti_st.5", "Ti_st.6", "Transmission", "Tr_st.1", "Tr_st.2", "Tr_st.3", "Tr_st.4", "Tr_st.5", "Tr_st.6", "NITRO", "FD", "TIRE", "DYNO", "Purpose", "Usage Guide", "Creator", "Creator ID")
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            values = (DB_Name, IGN, tier, stars, pp, evo, u1, u1_s1, u1_s2, u1_s3, u1_s4, u1_s5, u1_s6, u2, u2_s1, u2_s2, u2_s3, u2_s4, u2_s5, u2_s6, u3, u3_s1, u3_s2, u3_s3, u3_s4, u3_s5, u3_s6, u4, u4_s1, u4_s2, u4_s3, u4_s4, u4_s5, u4_s6, u5, u5_s1, u5_s2, u5_s3, u5_s4, u5_s5, u5_s6, u6, u6_s1, u6_s2, u6_s3, u6_s4, u6_s5, u6_s6, u7, u7_s1, u7_s2, u7_s3, u7_s4, u7_s5, u7_s6, nos, fd, tp, dyno, purpose, usage, creator, creatorID)

            tune_query = """
            SELECT MAX("TuneID")
            FROM community_tunes
            """

            try:
                await tunes_cursor.execute(query, values)
                await conn_tunes.commit()
                await tunes_cursor.execute(tune_query)
                tune_ID = await tunes_cursor.fetchone()
                logger.info(f"TUNES - Entry added successfully with TuneID: {tune_ID[0]}.")
                log += f"TUNES - Entry added successfully with TuneID: {tune_ID[0]}."
            except aiosqlite.Error as e:
                logger.error(f"TUNES - An error occurred while adding the entry: {e}")

    await conn_tunes.close()

    return tune_ID[0], log

async def alter_entry(tune_id: str, pp: str, evo: str, engine_motor: int, engine_motor_stage1: int, engine_motor_stage2: int, engine_motor_stage3: int, engine_motor_stage4: int, engine_motor_stage5: int, engine_motor_stage6, turbo_battery: int, turbo_battery_stage1: int, turbo_battery_stage2: int, turbo_battery_stage3: int, turbo_battery_stage4: int, turbo_battery_stage5: int, turbo_battery_stage6, intake_inverter: int, intake_inverter_stage1: int, intake_inverter_stage2: int, intake_inverter_stage3: int, intake_inverter_stage4: int, intake_inverter_stage5: int, intake_inverter_stage6, nitrous_overboost: int, nitrous_overboost_stage1: int, nitrous_overboost_stage2: int, nitrous_overboost_stage3: int, nitrous_overboost_stage4: int, nitrous_overboost_stage5: int, nitrous_overboost_stage6, body: int, body_stage1: int, body_stage2: int, body_stage3: int, body_stage4: int, body_stage5: int, body_stage6, tires: int, tires_stage1: int, tires_stage2: int, tires_stage3: int, tires_stage4: int, tires_stage5: int, tires_stage6, transmission: int, transmission_stage1: int, transmission_stage2: int, transmission_stage3: int, transmission_stage4: int, transmission_stage5: int, transmission_stage6, nitrous: str, final_drive: str, tire_pressure: str, dyno: str, purpose: str, usage: str):
    TUNES_DB = await helpers.load_file_path('tunes')
    async with aiosqlite.connect(TUNES_DB) as conn_tunes:
        async with conn_tunes.cursor() as tunes_cursor:
            values = []
            query = """UPDATE community_tunes SET"""
            if pp:
                query += """ "PP" = ?,"""
                values.append(pp)

            if evo:
                query += """ "EVO" = ?,"""
                values.append(evo)

            if engine_motor:
                query += """ "Engine/Motor" = ?,"""
                values.append(engine_motor)

            if engine_motor_stage1:
                query += """ "En_st.1" = ?,"""
                values.append(engine_motor_stage1)

            if engine_motor_stage2:
                query += """ "En_st.2" = ?,"""
                values.append(engine_motor_stage2)

            if engine_motor_stage3:
                query += """ "En_st.3" = ?,"""
                values.append(engine_motor_stage3)

            if engine_motor_stage4:
                query += """ "En_st.4" = ?,"""
                values.append(engine_motor_stage4)

            if engine_motor_stage5:
                query += """ "En_st.5" = ?,"""
                values.append(engine_motor_stage5)

            if engine_motor_stage6:
                query += """ "En_st.6" = ?,"""
                values.append(engine_motor_stage6)

            if turbo_battery:
                query += """ "Turbo/Battery" = ?,"""
                values.append(turbo_battery)

            if turbo_battery_stage1:
                query += """ "Tu_st.1" = ?,"""
                values.append(turbo_battery_stage1)

            if turbo_battery_stage2:
                query += """ "Tu_st.2" = ?,"""
                values.append(turbo_battery_stage2)

            if turbo_battery_stage3:
                query += """ "Tu_st.3" = ?,"""
                values.append(turbo_battery_stage3)

            if turbo_battery_stage4:
                query += """ "Tu_st.4" = ?,"""
                values.append(turbo_battery_stage4)

            if turbo_battery_stage5:
                query += """ "Tu_st.5" = ?,"""
                values.append(turbo_battery_stage5)

            if turbo_battery_stage6:
                query += """ "Tu_st.6" = ?,"""
                values.append(turbo_battery_stage6)

            if intake_inverter:
                query += """ "Intake/Inverter" = ?,"""
                values.append(intake_inverter)

            if intake_inverter_stage1:
                query += """ "In_st.1" = ?,"""
                values.append(intake_inverter_stage1)

            if intake_inverter_stage2:
                query += """ "In_st.2" = ?,"""
                values.append(intake_inverter_stage2)

            if intake_inverter_stage3:
                query += """ "In_st.3" = ?,"""
                values.append(intake_inverter_stage3)

            if intake_inverter_stage4:
                query += """ "In_st.4" = ?,"""
                values.append(intake_inverter_stage4)

            if intake_inverter_stage5:
                query += """ "In_st.5" = ?,"""
                values.append(intake_inverter_stage5)

            if intake_inverter_stage6:
                query += """ "In_st.6" = ?,"""
                values.append(intake_inverter_stage6)

            if nitrous_overboost:
                query += """ "Nitrous/Overboost" = ?,"""
                values.append(nitrous_overboost)

            if nitrous_overboost_stage1:
                query += """ "Ni_st.1" = ?,"""
                values.append(nitrous_overboost_stage1)

            if nitrous_overboost_stage2:
                query += """ "Ni_st.2" = ?,"""
                values.append(nitrous_overboost_stage2)

            if nitrous_overboost_stage3:
                query += """ "Ni_st.3" = ?,"""
                values.append(nitrous_overboost_stage3)

            if nitrous_overboost_stage4:
                query += """ "Ni_st.4" = ?,"""
                values.append(nitrous_overboost_stage4)

            if nitrous_overboost_stage5:
                query += """ "Ni_st.5" = ?,"""
                values.append(nitrous_overboost_stage5)

            if nitrous_overboost_stage6:
                query += """ "Ni_st.6" = ?,"""
                values.append(nitrous_overboost_stage6)

            if body:
                query += """ "Body" = ?,"""
                values.append(body)

            if body_stage1:
                query += """ "Bo_st.1" = ?,"""
                values.append(body_stage1)

            if body_stage2:
                query += """ "Bo_st.2" = ?,"""
                values.append(body_stage2)

            if body_stage3:
                query += """ "Bo_st.3" = ?,"""
                values.append(body_stage3)

            if body_stage4:
                query += """ "Bo_st.4" = ?,"""
                values.append(body_stage4)

            if body_stage5:
                query += """ "Bo_st.5" = ?,"""
                values.append(body_stage5)

            if body_stage6:
                query += """ "Bo_st.6" = ?,"""
                values.append(body_stage6)

            if tires:
                query += """ "Tires" = ?,"""
                values.append(tires)

            if tires_stage1:
                query += """ "Ti_st.1" = ?,"""
                values.append(tires_stage1)

            if tires_stage2:
                query += """ "Ti_st.2" = ?,"""
                values.append(tires_stage2)

            if tires_stage3:
                query += """ "Ti_st.3" = ?,"""
                values.append(tires_stage3)

            if tires_stage4:
                query += """ "Ti_st.4" = ?,"""
                values.append(tires_stage4)

            if tires_stage5:
                query += """ "Ti_st.5" = ?,"""
                values.append(tires_stage5)

            if tires_stage6:
                query += """ "Ti_st.6" = ?,"""
                values.append(tires_stage6)

            if transmission:
                query += """ "Transmission" = ?,"""
                values.append(transmission)

            if transmission_stage1:
                query += """ "Tr_st.1" = ?,"""
                values.append(transmission_stage1)

            if transmission_stage2:
                query += """ "Tr_st.2" = ?,"""
                values.append(transmission_stage2)

            if transmission_stage3:
                query += """ "Tr_st.3" = ?,"""
                values.append(transmission_stage3)

            if transmission_stage4:
                query += """ "Tr_st.4" = ?,"""
                values.append(transmission_stage4)

            if transmission_stage5:
                query += """ "Tr_st.5" = ?,"""
                values.append(transmission_stage5)

            if transmission_stage6:
                query += """ "Tr_st.6" = ?,"""
                values.append(transmission_stage6)

            if nitrous:
                query += """ "NITRO" = ?,"""
                values.append(nitrous)

            if final_drive:
                query += """ "FD" = ?,"""
                values.append(final_drive)

            if tire_pressure:
                query += """ "TIRE" = ?,"""
                values.append(tire_pressure)

            if dyno:
                query += """ "DYNO" = ?,"""
                values.append(dyno)

            if purpose:
                query += """ "Purpose" = ?,"""
                values.append(purpose)

            if usage:
                query += """ "Usage Guide" = ?,"""
                values.append(usage)

            query = query.rstrip(",")

            query += """ WHERE "TuneID" = ?"""
            values.append(tune_id)
            logger.info(f"TUNES - {query}")
            log += f"TUNES - {query}"
            logger.info(f"TUNES - {values}")
            log += f"TUNES - {values}"

            try:
                await tunes_cursor.execute(query, values)
                await conn_tunes.commit()
                status = 1
            except Exception as e:
                logger.warning(f"TUNES - {e}")
                log += f"TUNES - {e}"
                status = 1

    await conn_tunes.close()

    return log, status

async def remove_entry(tune_id: int):
    TUNES_DB = await helpers.load_file_path('tunes')
    async with aiosqlite.connect(TUNES_DB) as conn_tunes:
        async with conn_tunes.cursor() as tunes_cursor:

            values = [tune_id]
            query = """
                SELECT "Usage Guide"
                FROM community_tunes
                WHERE "TuneID" = ?
            """
            await tunes_cursor.execute(query, values)
            result = await tunes_cursor.fetchone()

            query = """
                DELETE FROM community_tunes
                WHERE "TuneID" = ?
            """
            await tunes_cursor.execute(query, values)
            await conn_tunes.commit()

    await conn_tunes.close()

    return result

async def query_tune(car, tune_id, tier, rarity, purpose, creator):
    TUNES_DB = await helpers.load_file_path('tunes')
    async with aiosqlite.connect(TUNES_DB) as conn_tunes:
        async with conn_tunes.cursor() as tunes_cursor:
            values = []
            query = """
                SELECT *
                FROM community_tunes
                WHERE
            """
            if car:
                db_name_valid = "_" in car
                values.append(f"%{car}%")
                if db_name_valid:
                    query += "\"DB Name\" COLLATE NOCASE LIKE ? "
                else:
                    query += "\"Ingame Name Clarification\" COLLATE NOCASE LIKE ? "
                if tune_id or tier or rarity or purpose or creator:
                    query += "AND "

            if tune_id:
                values.append(f"{tune_id}")
                query += "\"TuneID\" COLLATE NOCASE LIKE ? "
                if tier or rarity or purpose or creator:
                    query += "AND "

            if tier:
                values.append(f"%{tier}%")
                query += "\"Un\" COLLATE NOCASE LIKE ? "
                if rarity or purpose or creator:
                    query += "AND "

            if rarity:
                values.append(f"%{rarity}%")
                query += "\"★\" COLLATE NOCASE LIKE ? "
                if purpose or creator:
                    query += "AND "

            if purpose:
                values.append(f"%{purpose}%")
                query += "\"Purpose\" COLLATE NOCASE LIKE ? "
                if creator:
                    query += "AND "

            if creator:
                values.append(f"%{creator}%")
                query += "\"Creator\" COLLATE NOCASE LIKE ? "

            query = query.rstrip("AND ")

            await tunes_cursor.execute(query, values)
            results = await tunes_cursor.fetchall()

    await conn_tunes.close()

    return results

async def initial_setup():
    await create_database(None, log = "")

if __name__ == "__main__":
    asyncio.run(initial_setup())
