import asyncio
import aiohttp
import json
import os
from discord.ext import commands
import helpers
import in_app_logging

logger = helpers.load_logging()
localisation = dict(helpers.load_localisation())

JSON_URL = {
    'records': 'https://raw.githubusercontent.com/Nitro4CSR/CSR2WorldRecordsDB/main/JessWR.json',
    's6_effects': 'https://raw.githubusercontent.com/Nitro4CSR/CSR2WorldRecordsDB/main/JessS6.json',
    'info': 'https://raw.githubusercontent.com/Nitro4CSR/CSR2WorldRecordsDB/main/JessINFO.json',
    'updates': 'https://raw.githubusercontent.com/Nitro4CSR/CSR2WorldRecordsDB/main/JessUpdates.json'
}

table_schemas = {
    'records': ['"UniqueID" TEXT PRIMARY KEY', '"DB Name" TEXT', '"Ingame Name Clarification" TEXT', '"Un" TEXT', '"★" TEXT', '"WR-PP" TEXT', '"WR-EVO" TEXT', '"WR-NITRO" TEXT', '"WR-FD" REAL', '"WR-TIRE" TEXT', '"WR-DYNO" REAL', '"WR-BEST ET" REAL', '"WR Addon" TEXT', '"SHIFT Links" TEXT', '"WR-DRIVER" TEXT'],
    's6_effects': ['"UniqueID" TEXT PRIMARY KEY', '"DB Name" TEXT', '"Ingame Name" TEXT', '"Un" TEXT', '"★" TEXT', '"S5 - PP" TEXT', '"S5 - EVO" TEXT', '"S5 - NOS" TEXT', '"S5 - FD" TEXT', '"S5 - TIRES" TEXT', '"S5 - DYNO" REAL', '"Engine" REAL', '"Turbo" REAL', '"Intake" REAL', '"NOS" REAL', '"Body" REAL', '"Tires" REAL', '"Trans" REAL', '"is EV?" TEXT'],
    'info': ['"UniqueID" TEXT PRIMARY KEY', '"DB Name" TEXT', '"Ingame Name" TEXT', '"Un" TEXT', '"★" TEXT', '"IMG" TEXT', '"Vision Info" TEXT', '"is EV?" TEXT', '"thread" TEXT'],
    'updates': ['"ID" TEXT PRIMARY KEY', '"Date" TEXT', '"Output Vision" TEXT']
}

etag_cache = {}

async def get_github_etag(session, url):
    async with session.head(url) as response:
        headers = response.headers
        if response.status == 200:
            return headers.get('ETag')
    return None

async def should_update_database():
    global header, log, status, etag_cache
    status = 2
    async with aiohttp.ClientSession() as session:
        for url in JSON_URL.values():
            github_etag = await get_github_etag(session, url)
            if github_etag is None:
                logger.warning(f"{header}{localisation.get('EDB_LOG_UPDATE_CHECK_FAIL')} {url}")
                log += f"\n{header}{localisation.get('EDB_LOG_UPDATE_CHECK_FAIL')} {url}"
                status = 1
                continue

            if url not in etag_cache or etag_cache[url] != github_etag:
                logger.info(f"{header}{localisation.get('EDB_LOG_UPDATE_CHECK_DONE_UPDATE_NEEDED')} {url}: {github_etag}")
                log += f"\n{header}{localisation.get('EDB_LOG_UPDATE_CHECK_DONE_UPDATE_NEEDED')} {url}: {github_etag}"
                etag_cache[url] = github_etag
                return True, status
    return False, status

async def check_and_delete_database():
    global header, log
    DATABASE_PATH = await helpers.load_file_path('EDB')
    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)
        logger.info(f"{header}{localisation.get('EDB_LOG_UPDATE_DELETE_OLD_DB')} {DATABASE_PATH}")
        log += f"\n{header}{localisation.get('EDB_LOG_UPDATE_DELETE_OLD_DB')} {DATABASE_PATH}\n"
    else:
        logger.info(f"{header}{localisation.get('EDB_LOG_UPDATE_CREATE_NEW_DB_START')}")
        log += f"\n{header}{localisation.get('EDB_LOG_UPDATE_CREATE_NEW_DB_START')}"

async def fetch_json_data():
    global header, log, status
    json_data = {}
    async with aiohttp.ClientSession() as session:
        for table_name, url in JSON_URL.items():
            async with session.get(url) as response:
                if response.status == 200:
                    json_data[table_name] = json.loads(await response.text())
                    logger.info(f"{header}{localisation.get('EDB_LOG_FETCH_DATA_DONE_1')} {table_name}: {json_data[table_name][:2]}{localisation.get('EDB_LOG_FETCH_DATA_DONE_2')}")
                    log += f"\n{header}{localisation.get('EDB_LOG_FETCH_DATA_DONE_1')} {table_name}: {json_data[table_name][:1]}{localisation.get('EDB_LOG_FETCH_DATA_DONE_2')}\n"
                    status = 2
                else:
                    logger.error(f"{header}{localisation.get('EDB_LOG_FETCH_DATA_FAIL')} {table_name} (HTTP {response.status})")
                    log += f"\n{header}{localisation.get('EDB_LOG_FETCH_DATA_FAIL')} {table_name} (HTTP {response.status})"
                    status = 0
                    json_data[table_name] = []
                    continue
    return json_data

async def create_tables(cursor):
    global header, log
    
    for table_name, schema in table_schemas.items():
        await cursor.execute(f"CREATE TABLE {table_name} ({', '.join(schema)})")
        logger.info(f"{header}{localisation.get('EDB_LOG_UPDATE_CREATE_NEW_DB_TABLE_CREATED')} {table_name}")
        log += f"\n{header}{localisation.get('EDB_LOG_UPDATE_CREATE_NEW_DB_TABLE_CREATED')} {table_name}"

async def create_database(json_data):
    global header, log
    for table_name, schema in table_schemas.items():
        await helpers.execute_sql_statement("WRs", f"CREATE TABLE {table_name} ({', '.join(schema)})")
        logger.info(f"{header}{localisation.get('EDB_LOG_UPDATE_CREATE_NEW_DB_TABLE_CREATED')} {table_name}")
        log += f"\n{header}{localisation.get('EDB_LOG_UPDATE_CREATE_NEW_DB_TABLE_CREATED')} {table_name}"
    for table_name, data in json_data.items():
        if data:
            keys = list(data[0].keys())
            placeholders = ', '.join(['?' for _ in keys])
            columns = ', '.join([f'"{key}"' for key in keys])
            schema_keys = [col.split('" ')[0] + '"' for col in table_schemas[table_name]]
            if set(keys) != set([key.replace('"', '') for key in schema_keys]):
                logger.error(f"{header}{localisation.get('EDB_LOG_POPULATE_TABLE_ERROR_KEY_MISMATCH_1')} {table_name}\n{localisation.get('EDB_LOG_POPULATE_TABLE_ERROR_KEY_MISMATCH_2')} {keys}\n{localisation.get('EDB_LOG_POPULATE_TABLE_ERROR_KEY_MISMATCH_3')} {schema_keys}")
                log += f"\n{header}{localisation.get('EDB_LOG_POPULATE_TABLE_ERROR_KEY_MISMATCH_1')} {table_name}\n{localisation.get('EDB_LOG_POPULATE_TABLE_ERROR_KEY_MISMATCH_2')} {keys}\n{localisation.get('EDB_LOG_POPULATE_TABLE_ERROR_KEY_MISMATCH_3')} {schema_keys}\n"
                continue
            insert_data = [tuple(item[key] for key in keys) for item in data]
            logger.info(f"{header}{localisation.get('EDB_LOG_POPULATE_TABLE_DONE_1')} {table_name}: {insert_data[:2]}{localisation.get('EDB_LOG_POPULATE_TABLE_DONE_2')}")
            log += f"\n{header}{localisation.get('EDB_LOG_POPULATE_TABLE_DONE_1')} {table_name}: {insert_data[:1]}{localisation.get('EDB_LOG_POPULATE_TABLE_DONE_2')}\n"
            for row in insert_data:
                await helpers.execute_sql_statement("WRs", f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})', row)
            status = 2
        else:
            logger.warning(f"{header}{localisation.get('EDB_LOG_POPULATE_TABLE_WARNING_NO_DATA')} {table_name}")
            log += f"\n{header}{localisation.get('EDB_LOG_POPULATE_TABLE_WARNING_NO_DATA')} {table_name}\n"
            status = 1
    logger.info(f"{header}{localisation.get('EDB_LOG_UPDATE_CREATE_NEW_DB_DONE')}")
    log += f"\n{header}{localisation.get('EDB_LOG_UPDATE_CREATE_NEW_DB_DONE')}"
    return status

async def recreate_database(bot: commands.Bot):
    global header, log, status
    header = localisation.get('EDB_LOG_HEADER')
    logger.info(f"{header}{localisation.get('EDB_LOG_UPDATE_CHECK_START')}")
    log = f"{header}{localisation.get('EDB_LOG_UPDATE_CHECK_START')}"
    should_update, status = await should_update_database()
    if should_update:
        logger.info(f"{header}{localisation.get('EDB_LOG_UPDATE_START')}")
        log += f"{header}{localisation.get('EDB_LOG_UPDATE_START')}"
        await check_and_delete_database()
        json_data = await fetch_json_data()
        status = await create_database(json_data)
        logger.info(f"{header}{localisation.get('EDB_LOG_UPDATE_DONE')}")
        log += f"\n{header}{localisation.get('EDB_LOG_UPDATE_DONE')}"
    else:
        logger.info(f"{header}{localisation.get('EDB_LOG_UPDATE_CHECK_DONE_UPDATE_UNNECESSARY')}")
        log += f"\n{header}{localisation.get('EDB_LOG_UPDATE_CHECK_DONE_UPDATE_UNNECESSARY')}"
        status = 2
    await in_app_logging.send_log(bot, log, status, 2)

async def initial_setup():
    await recreate_database("")

if __name__ == "__main__":
    asyncio.run(initial_setup())
