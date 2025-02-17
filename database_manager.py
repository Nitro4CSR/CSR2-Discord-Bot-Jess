import asyncio
import aiohttp
import aiosqlite
import os
import logging
import time
import helpers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

JSON_URL = {
    'records': 'https://raw.githubusercontent.com/Nitro4CSR/CSR2WorldRecordsDB/main/JessWR.json',
    's6_effects': 'https://raw.githubusercontent.com/Nitro4CSR/CSR2WorldRecordsDB/main/JessS6.json',
    'info': 'https://raw.githubusercontent.com/Nitro4CSR/CSR2WorldRecordsDB/main/JessINFO.json',
    'updates': 'https://raw.githubusercontent.com/Nitro4CSR/CSR2WorldRecordsDB/main/JessUpdates.json'
}

DATABASE_PATH = helpers.load_external_db()

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

async def get_github_last_modified(session, url):
    async with session.head(url) as response:
        if response.status == 200:
            return response.headers.get('Last-Modified')
    return None

def get_local_file_creation_date(file_path):
    if os.path.exists(DATABASE_PATH):
        if os.name == 'nt':  # Windows
            return os.path.getctime(file_path)
        else:  # Unix-based
            stat = os.stat(file_path)
            return getattr(stat, 'st_birthtime', stat.st_mtime)
    else:
        return 0

async def should_update_database():
    async with aiohttp.ClientSession() as session:
        for url in JSON_URL.values():
            github_last_modified = await get_github_last_modified(session, url)
            if github_last_modified:
                github_time = time.mktime(time.strptime(github_last_modified, "%a, %d %b %Y %H:%M:%S GMT"))
                local_time = get_local_file_creation_date(DATABASE_PATH)
                if github_time > local_time:
                    return True
    return False

def check_and_create_database():
    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)
        logging.info(f"Deleted existing database: {DATABASE_PATH}")
    else:
        logging.info("No existing database found. Creating a new one.")

async def fetch_data_with_aiohttp(session, url):
    async with session.get(url) as response:
        return await response.json()

async def fetch_json_data():
    json_data = {}
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_data_with_aiohttp(session, url) for _, url in JSON_URL.items()]
        results = await asyncio.gather(*tasks)
        for (table_name, _), data in zip(JSON_URL.items(), results):
            json_data[table_name] = data
            logging.info(f"Fetched data for {table_name}: {json_data[table_name][:2]}... (showing first 2 records)")
    return json_data

async def create_tables(cursor):
    for table_name, schema in table_schemas.items():
        await cursor.execute(f"CREATE TABLE {table_name} ({', '.join(schema)})")
        logging.info(f"Created table: {table_name}")

async def insert_data(cursor, json_data):
    for table_name, data in json_data.items():
        if data:
            keys = list(data[0].keys())
            placeholders = ', '.join(['?' for _ in keys])
            columns = ', '.join([f'"{key}"' for key in keys])

            schema_keys = [col.split('" ')[0] + '"' for col in table_schemas[table_name]]
            if set(keys) != set([key.replace('"', '') for key in schema_keys]):
                logging.error(f"Column mismatch for {table_name}. JSON keys: {keys}, Schema keys: {schema_keys}")
                continue

            insert_data = [tuple(item[key] for key in keys) for item in data]
            logging.info(f"Inserting data into {table_name}: {insert_data[:2]}... (showing first 2 records)")

            await cursor.executemany(
                f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})',
                insert_data
            )
        else:
            logging.warning(f"No data to insert for table: {table_name}")

async def create_database(json_data):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.cursor()
        await create_tables(cursor)
        await insert_data(cursor, json_data)
        await db.commit()
    logging.info("Database created and tables populated successfully")

async def recreate_database():
    logging.info("Checking Database Status")
    if await should_update_database():
        logging.info("Starting database update")
        check_and_create_database()
        json_data = await fetch_json_data()
        await create_database(json_data)
        logging.info("Database update completed")
    else:
        logging.info("No updates required. Database is up to date.")

async def initial_setup():
    await recreate_database()

async def schedule_updates():
    while True:
        await recreate_database()
        await asyncio.sleep(3600)  # Runs every hour

if __name__ == "__main__":
    asyncio.run(initial_setup())
    asyncio.run(schedule_updates())
