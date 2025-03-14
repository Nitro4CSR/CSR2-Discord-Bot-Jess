import asyncio
import aiohttp
import aiosqlite
import json
import os
from discord.ext import commands
import helpers
import in_app_logging

logger = helpers.load_logging()

JSON_URL = {
    'records': 'https://raw.githubusercontent.com/Nitro4CSR/CSR2WorldRecordsDB/main/JessWR.json',
    's6_effects': 'https://raw.githubusercontent.com/Nitro4CSR/CSR2WorldRecordsDB/main/JessS6.json',
    'info': 'https://raw.githubusercontent.com/Nitro4CSR/CSR2WorldRecordsDB/main/JessINFO.json',
    'updates': 'https://raw.githubusercontent.com/Nitro4CSR/CSR2WorldRecordsDB/main/JessUpdates.json'
}

table_schemas = {
    'records': [
        '"UniqueID" TEXT PRIMARY KEY', '"DB Name" TEXT', '"Ingame Name Clarification" TEXT', '"Un" TEXT', '"★" TEXT', '"WR-PP" TEXT', '"WR-EVO" TEXT', '"WR-NITRO" TEXT', '"WR-FD" REAL', '"WR-TIRE" TEXT', '"WR-DYNO" REAL', '"WR-BEST ET" REAL', '"WR Addon" TEXT', '"SHIFT Links" TEXT', '"WR-DRIVER" TEXT'
    ],
    's6_effects': [
        '"UniqueID" TEXT PRIMARY KEY', '"DB Name" TEXT', '"Ingame Name" TEXT', '"Un" TEXT', '"★" TEXT', '"S5 - PP" TEXT', '"S5 - EVO" TEXT', '"S5 - NOS" TEXT', '"S5 - FD" TEXT', '"S5 - TIRES" TEXT', '"S5 - DYNO" REAL', '"Engine" REAL', '"Turbo" REAL', '"Intake" REAL', '"NOS" REAL', '"Body" REAL', '"Tires" REAL', '"Trans" REAL', '"is EV?" TEXT'
    ],
    'info': [
        '"UniqueID" TEXT PRIMARY KEY', '"DB Name" TEXT', '"Ingame Name" TEXT', '"Un" TEXT', '"★" TEXT', '"IMG" TEXT', '"Vision Info" TEXT', '"is EV?" TEXT', '"thread" TEXT'
    ],
    'updates': [
        '"ID" TEXT PRIMARY KEY', '"Date" TEXT', '"Output Vision" TEXT'
    ]
}

etag_cache = {}

async def get_github_etag(session, url):
    async with session.head(url) as response:
        headers = response.headers
        if response.status == 200:
            return headers.get('ETag')

    return None

async def should_update_database(log: str):
    global etag_cache
    status = 2
    async with aiohttp.ClientSession() as session:
        for url in JSON_URL.values():
            github_etag = await get_github_etag(session, url)
            if github_etag is None:
                logger.warning(f"EDB - No ETag received for {url}")
                log += f"\nEDB - No ETag received for {url}"
                status = 1
                continue

            if url not in etag_cache or etag_cache[url] != github_etag:
                logger.info(f"EDB - Database update needed. New ETag for {url}: {github_etag}")
                log += f"\nEDB - Database update needed. New ETag for {url}: {github_etag}"
                etag_cache[url] = github_etag
                return True, log, status

    return False, log, status

async def check_and_create_database(log: str):
    DATABASE_PATH = await helpers.load_file_path('EDB')
    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)
        logger.info(f"EDB - Deleted existing database: {DATABASE_PATH}")
        log += f"\nEDB - Deleted existing database: {DATABASE_PATH}\n"
    else:
        logger.info("EDB - No existing database found. Creating a new one.")
        log += f"\nEDB - No existing database found. Creating a new one."

    return log

async def fetch_json_data(log: str):
    json_data = {}
    async with aiohttp.ClientSession() as session:
        for table_name, url in JSON_URL.items():
            async with session.get(url) as response:
                if response.status == 200:
                    json_data[table_name] = json.loads(await response.text())
                    logger.info(f"EDB - Fetched {table_name}: {json_data[table_name][:2]}... (showing first 2 records)")
                    log += f"\nEDB - Fetched {table_name}: {json_data[table_name][:1]}... (showing first record)\n"
                    status = 2
                else:
                    logger.error(f"EDB - Failed to fetch {table_name} (HTTP {response.status})")
                    log += f"\nEDB - Failed to fetch {table_name} (HTTP {response.status})"
                    status = 0
                    json_data[table_name] = []
                    continue

    return json_data, log, status

async def create_tables(cursor, log):
    for table_name, schema in table_schemas.items():
        await cursor.execute(f"CREATE TABLE {table_name} ({', '.join(schema)})")
        logger.info(f"EDB - Created table: {table_name}")
        log += f"\nEDB - Created table: {table_name}"

    return log

async def insert_data(cursor, json_data, log, status):
    for table_name, data in json_data.items():
        if data:
            keys = list(data[0].keys())
            placeholders = ', '.join(['?' for _ in keys])
            columns = ', '.join([f'"{key}"' for key in keys])
            schema_keys = [col.split('" ')[0] + '"' for col in table_schemas[table_name]]
            if set(keys) != set([key.replace('"', '') for key in schema_keys]):
                logger.error(f"EDB - Column mismatch for {table_name}. JSON keys: {keys}, Schema keys: {schema_keys}")
                log += f"\nEDB - Column mismatch for {table_name}. JSON keys: {keys}, Schema keys: {schema_keys}\n"
                status = 0
                continue

            insert_data = [tuple(item[key] for key in keys) for item in data]
            logger.info(f"EDB - Inserting data into {table_name}: {insert_data[:2]}... (showing first 2 records)")
            log += f"\nEDB - Inserting data into {table_name}: {insert_data[:1]}... (showing first record)\n"

            await cursor.executemany(
                f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})',
                insert_data
            )
        else:
            logger.warning(f"EDB - No data to insert for table: {table_name}")
            log += f"\nEDB - No data to insert for table: {table_name}\n"
            status = 1

    return log, status

async def create_database(json_data, log, status):
    DATABASE_PATH = await helpers.load_file_path('EDB')
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.cursor()
        log = await create_tables(cursor, log)
        log, status = await insert_data(cursor, json_data, log, status)
        await db.commit()
    logger.info("EDB - Database created and tables populated successfully")
    log += f"\nEDB - Database created and tables populated successfully"

    return log, status

async def recreate_database(bot: commands.Bot):
    logger.info("EDB - Checking Database Status")
    log = f"EDB - Checking Database Status"
    should_update, log, status = await should_update_database(log)
    if should_update:
        logger.info("EDB - Starting database update")
        log += f"EDB - Starting database update"
        log = await check_and_create_database(log)
        json_data, log, status = await fetch_json_data(log)
        log, status = await create_database(json_data, log, status)
        logger.info("EDB - Database update completed")
        log += f"\nEDB - Database update completed"
    else:
        logger.info("EDB - No updates required. Database is up to date.")
        log += f"\nEDB - No updates required. Database is up to date."
        status = 2
    await in_app_logging.send_log(bot, log, status, 2)

async def initial_setup():
    await recreate_database()

if __name__ == "__main__":
    asyncio.run(initial_setup())
