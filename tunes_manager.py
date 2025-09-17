import asyncio
import os
from discord.ext import commands
import helpers
import in_app_logging

logger = helpers.load_logging()
localisation = dict(helpers.load_localisation())

table_schemas = {
    'community_tunes': ['"TuneID" INTEGER PRIMARY KEY AUTOINCREMENT', '"DB Name" TEXT', '"Ingame Name Clarification" TEXT', '"Un" TEXT', '"★" TEXT', '"PP" INTEGER', '"EVO" INTEGER', '"Engine/Motor" Integer', '"En_st.1" TEXT', '"En_st.2" TEXT', '"En_st.3" TEXT', '"En_st.4" TEXT', '"En_st.5" TEXT', '"En_st.6" TEXT', '"Turbo/Battery" Integer', '"Tu_st.1" TEXT', '"Tu_st.2" TEXT', '"Tu_st.3" TEXT', '"Tu_st.4" TEXT', '"Tu_st.5" TEXT', '"Tu_st.6" TEXT', '"Intake/Inverter" Integer', '"In_st.1" TEXT', '"In_st.2" TEXT', '"In_st.3" TEXT', '"In_st.4" TEXT', '"In_st.5" TEXT', '"In_st.6" TEXT', '"Nitrous/Overboost" Integer', '"Ni_st.1" TEXT', '"Ni_st.2" TEXT', '"Ni_st.3" TEXT', '"Ni_st.4" TEXT', '"Ni_st.5" TEXT', '"Ni_st.6" TEXT', '"Body" Integer', '"Bo_st.1" TEXT', '"Bo_st.2" TEXT', '"Bo_st.3" TEXT', '"Bo_st.4" TEXT', '"Bo_st.5" TEXT', '"Bo_st.6" TEXT', '"Tires" Integer', '"Ti_st.1" TEXT', '"Ti_st.2" TEXT', '"Ti_st.3" TEXT', '"Ti_st.4" TEXT', '"Ti_st.5" TEXT', '"Ti_st.6" TEXT', '"Transmission" Integer', '"Tr_st.1" TEXT', '"Tr_st.2" TEXT', '"Tr_st.3" TEXT', '"Tr_st.4" TEXT', '"Tr_st.5" TEXT', '"Tr_st.6" TEXT', '"NITRO" TEXT', '"FD" REAL', '"TIRE" TEXT', '"DYNO" REAL', '"Purpose" TEXT', '"Usage Guide" TEXT', '"Creator" TEXT', '"Creator ID" TEXT']
}

async def create_database(bot: commands.Bot, log: str = None):
    header = localisation.get('TUNES_LOG_HEADER')
    logger.info(f"{header}{localisation.get('TUNES_LOG_BOOT_SETUP')}")
    log = f"{header}{localisation.get('TUNES_LOG_BOOT_SETUP')}"
    TUNES_DB = await helpers.load_file_path('tunes')
    if not os.path.exists(TUNES_DB):
        logger.info(f"{header}{localisation.get('TUNES_LOG_DB_INITIAL_CREATION_START')}")
        log += f"{header}{localisation.get('TUNES_LOG_DB_INITIAL_CREATION_START')}"
        try:
            for table_name, schema in table_schemas.items():
                await helpers.execute_sql_statement("tunes", f"CREATE TABLE {table_name} ({', '.join(schema)})")
            logger.info(f"{header}{localisation.get('TUNES_LOG_DB_TABLES_CREATE_DONE')}")
            log += f"{header}{localisation.get('TUNES_LOG_DB_TABLES_CREATE_DONE')}"
        except Exception as e:
            logger.error(f"{header}{localisation.get('TUNES_LOG_DB_TABLES_CREATE_FAIL')} {e}")
            log += f"{header}{localisation.get('TUNES_LOG_DB_TABLES_CREATE_FAIL')} {e}"
            await in_app_logging.send_log(bot, log, 0, 2)
    elif bot:
        await in_app_logging.send_log(bot, log, 2, 2)
    else:
        return log

async def pull_available_cars():
    query = """SELECT "DB Name", "Ingame Name Clarification", "Un", "★"\nFROM records"""
    cars = await helpers.execute_sql_statement("WRs", query, None)
    return cars

async def get_creator_by_tune_id(tune_id):
    query = """SELECT "Creator ID"\nFROM community_tunes\nWHERE "TuneID" = ?"""
    creator_id = await helpers.execute_sql_statement("tunes", query, [str(tune_id)])
    return creator_id

async def search_tune_id(tune_id):
    query = """SELECT "TuneID"\nFROM community_tunes\nWHERE "TuneID" = ?"""
    result = await helpers.execute_sql_statement("tunes", query, [str(tune_id)])
    return result

async def add_entry(DB_Name: str, IGN: str, tier: str, stars: str, pp: str, evo: str, u1: int, u1_s1: int, u1_s2: int, u1_s3: int, u1_s4: int, u1_s5: int, u1_s6, u2: int, u2_s1: int, u2_s2: int, u2_s3: int, u2_s4: int, u2_s5: int, u2_s6, u3: int, u3_s1: int, u3_s2: int, u3_s3: int, u3_s4: int, u3_s5: int, u3_s6, u4: int, u4_s1: int, u4_s2: int, u4_s3: int, u4_s4: int, u4_s5: int, u4_s6, u5: int, u5_s1: int, u5_s2: int, u5_s3: int, u5_s4: int, u5_s5: int, u5_s6, u6: int, u6_s1: int, u6_s2: int, u6_s3: int, u6_s4: int, u6_s5: int, u6_s6, u7: int, u7_s1: int, u7_s2: int, u7_s3: int, u7_s4: int, u7_s5: int, u7_s6, nos: str, fd: str, tp: str, dyno: str, purpose: str, usage: str, creator: str, creatorID: str, log: str):
    header = localisation.get('SHARE_TUNE_LOG_HEADER')
    log = await create_database(None, log)
    logger.info(f"{header}{localisation.get('SHARE_TUNE_MSG_ADD_ENTRY')}")
    query = """
    INSERT INTO community_tunes
    ("DB Name", "Ingame Name Clarification", "Un", "★", "PP", "EVO", "Engine/Motor", "En_st.1", "En_st.2", "En_st.3", "En_st.4", "En_st.5", "En_st.6", "Turbo/Battery", "Tu_st.1", "Tu_st.2", "Tu_st.3", "Tu_st.4", "Tu_st.5", "Tu_st.6", "Intake/Inverter", "In_st.1", "In_st.2", "In_st.3", "In_st.4", "In_st.5", "In_st.6", "Nitrous/Overboost", "Ni_st.1", "Ni_st.2", "Ni_st.3", "Ni_st.4", "Ni_st.5", "Ni_st.6", "Body", "Bo_st.1", "Bo_st.2", "Bo_st.3", "Bo_st.4", "Bo_st.5", "Bo_st.6", "Tires", "Ti_st.1", "Ti_st.2", "Ti_st.3", "Ti_st.4", "Ti_st.5", "Ti_st.6", "Transmission", "Tr_st.1", "Tr_st.2", "Tr_st.3", "Tr_st.4", "Tr_st.5", "Tr_st.6", "NITRO", "FD", "TIRE", "DYNO", "Purpose", "Usage Guide", "Creator", "Creator ID")
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    values = (DB_Name, IGN, tier, stars, pp, evo, u1, u1_s1, u1_s2, u1_s3, u1_s4, u1_s5, u1_s6, u2, u2_s1, u2_s2, u2_s3, u2_s4, u2_s5, u2_s6, u3, u3_s1, u3_s2, u3_s3, u3_s4, u3_s5, u3_s6, u4, u4_s1, u4_s2, u4_s3, u4_s4, u4_s5, u4_s6, u5, u5_s1, u5_s2, u5_s3, u5_s4, u5_s5, u5_s6, u6, u6_s1, u6_s2, u6_s3, u6_s4, u6_s5, u6_s6, u7, u7_s1, u7_s2, u7_s3, u7_s4, u7_s5, u7_s6, nos, fd, tp, dyno, purpose, usage, creator, creatorID)
    tune_query = """SELECT MAX("TuneID")\nFROM community_tunes"""
    try:
        await helpers.execute_sql_statement("tunes", query, values)
        tune_ID = await helpers.execute_sql_statement("tunes", tune_query)
        logger.info(f"{header}{localisation.get('SHARE_TUNE_MSG_ADD_ENTRY_DONE')} {tune_ID[0][0]}.")
        log += f"{header}{localisation.get('SHARE_TUNE_MSG_ADD_ENTRY_DONE')} {tune_ID[0][0]}."
    except Exception as e:
        logger.error(f"{header}{localisation.get('LOG_ERROR_FETCH')} {e}")
    return tune_ID[0][0], log

async def alter_entry(tune_id: str, parameters: list, log: str):
    header = localisation.get('UPDATE_TUNE_LOG_HEADER')
    values = []
    query = """UPDATE community_tunes SET"""
    query_bits = [
        """ "PP" = ?,""",
        """ "EVO" = ?,""",
        """ "Engine/Motor" = ?,""",
        """ "En_st.1" = ?,""",
        """ "En_st.2" = ?,""",
        """ "En_st.3" = ?,""",
        """ "En_st.4" = ?,""",
        """ "En_st.5" = ?,""",
        """ "En_st.6" = ?,""",
        """ "Turbo/Battery" = ?,""",
        """ "Tu_st.1" = ?,""",
        """ "Tu_st.2" = ?,""",
        """ "Tu_st.3" = ?,""",
        """ "Tu_st.4" = ?,""",
        """ "Tu_st.5" = ?,""",
        """ "Tu_st.6" = ?,""",
        """ "Intake/Inverter" = ?,""",
        """ "In_st.1" = ?,""",
        """ "In_st.2" = ?,""",
        """ "In_st.3" = ?,""",
        """ "In_st.4" = ?,""",
        """ "In_st.5" = ?,""",
        """ "In_st.6" = ?,""",
        """ "Nitrous/Overboost" = ?,""",
        """ "Ni_st.1" = ?,""",
        """ "Ni_st.2" = ?,""",
        """ "Ni_st.3" = ?,""",
        """ "Ni_st.4" = ?,""",
        """ "Ni_st.5" = ?,""",
        """ "Ni_st.6" = ?,""",
        """ "Body" = ?,""",
        """ "Bo_st.1" = ?,""",
        """ "Bo_st.2" = ?,""",
        """ "Bo_st.3" = ?,""",
        """ "Bo_st.4" = ?,""",
        """ "Bo_st.5" = ?,""",
        """ "Bo_st.6" = ?,""",
        """ "Tires" = ?,""",
        """ "Ti_st.1" = ?,""",
        """ "Ti_st.2" = ?,""",
        """ "Ti_st.3" = ?,""",
        """ "Ti_st.4" = ?,""",
        """ "Ti_st.5" = ?,""",
        """ "Ti_st.6" = ?,""",
        """ "Transmission" = ?,""",
        """ "Tr_st.1" = ?,""",
        """ "Tr_st.2" = ?,""",
        """ "Tr_st.3" = ?,""",
        """ "Tr_st.4" = ?,""",
        """ "Tr_st.5" = ?,""",
        """ "Tr_st.6" = ?,""",
        """ "NITRO" = ?,""",
        """ "FD" = ?,""",
        """ "TIRE" = ?,""",
        """ "DYNO" = ?,""",
        """ "Purpose" = ?,""",
        """ "Usage Guide" = ?,""",
        """ "Creator" = ?"""
    ]
    for idx, parameter in enumerate(parameters):
        if parameter is not None:
            query += query_bits[idx]
            values.append(parameter)
    query = query.rstrip(",")
    query += """ WHERE "TuneID" = ?"""
    values.append(tune_id)
    logger.info(f"{header}{localisation.get('INFO_LOG_QUERY')}{query}")
    log += f"{header}{localisation.get('INFO_LOG_QUERY')}{query}"
    logger.info(f"{header}{localisation.get('INFO_LOG_PARAMETERS')}{values}")
    log += f"{header}{localisation.get('INFO_LOG_PARAMETERS')}{values}"
    await helpers.execute_sql_statement("tunes", query, values)
    status = 1
    return log, status

async def remove_entry(tune_id: int):
    query = """DELETE FROM community_tunes\nWHERE "TuneID" = ?"""
    await helpers.execute_sql_statement("tunes", query, [str(tune_id)])

async def query_tune(car, tune_id, tier, rarity, purpose, creator):
    values = []
    query = """SELECT *\nFROM community_tunes\nWHERE"""
    if car:
        if "_" in car:
            query += "\"DB Name\" COLLATE NOCASE LIKE ? "
        else:
            query += "\"Ingame Name Clarification\" COLLATE NOCASE LIKE ? "
        values.append(f"%{car}%")
        if tune_id or tier or rarity or purpose or creator:
            query += "AND "
    if tune_id:
        query += "\"TuneID\" COLLATE NOCASE LIKE ? "
        values.append(f"{tune_id}")
        if tier or rarity or purpose or creator:
            query += "AND "
    if tier:
        query += "\"Un\" COLLATE NOCASE LIKE ? "
        values.append(f"%{tier}%")
        if rarity or purpose or creator:
            query += "AND "
    if rarity:
        query += "\"★\" COLLATE NOCASE LIKE ? "
        values.append(f"%{rarity}%")
        if purpose or creator:
            query += "AND "
    if purpose:
        query += "\"Purpose\" COLLATE NOCASE LIKE ? "
        values.append(f"%{purpose}%")
        if creator:
            query += "AND "
    if creator:
        query += "\"Creator\" COLLATE NOCASE LIKE ? "
        values.append(f"%{creator}%")
    query = query.rstrip("AND ")
    results = await helpers.execute_sql_statement("tunes", query, values)
    return results

async def initial_setup():
    await create_database(None, log = "")

if __name__ == "__main__":
    asyncio.run(initial_setup())
