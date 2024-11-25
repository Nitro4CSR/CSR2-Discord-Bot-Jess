import sqlite3
import os
import urllib.request
import json
import logging
import schedule
import time
import helpers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Define URLs for data sources
JSON_URL = {
    'records': 'https://raw.githubusercontent.com/Nitro4CSR/CSR2WorldRecordsDB/main/JessWR.json',
    's6_effects': 'https://raw.githubusercontent.com/Nitro4CSR/CSR2WorldRecordsDB/main/JessS6.json',
    'info': 'https://raw.githubusercontent.com/Nitro4CSR/CSR2WorldRecordsDB/main/JessINFO.json',
    'updates': 'https://raw.githubusercontent.com/Nitro4CSR/CSR2WorldRecordsDB/main/JessUpdates.json'
}

DATABASE_PATH = helpers.load_external_db()

# Define table schemas
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

def check_and_create_database():
    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)
        logging.info(f"Deleted existing database: {DATABASE_PATH}")
    else:
        logging.info(f"No existing database found. Proceeding to create a new one.")

def fetch_data_with_urllib(url):
    with urllib.request.urlopen(url) as response:
        data = response.read()
        return json.loads(data)

def fetch_json_data():
    json_data = {}
    for table_name, url in JSON_URL.items():
        json_data[table_name] = fetch_data_with_urllib(url)
        logging.info(f"Fetched data for {table_name}: {json_data[table_name][:2]}... (showing first 2 records)")
    return json_data

def create_tables(cursor):
    for table_name, schema in table_schemas.items():
        cursor.execute(f"CREATE TABLE {table_name} ({', '.join(schema)})")
        logging.info(f"Created table: {table_name} with schema: {schema}")

def insert_data(cursor, json_data):
    for table_name, data in json_data.items():
        if data:
            # Extract keys and values from JSON data
            keys = list(data[0].keys())
            placeholders = ', '.join(['?' for _ in keys])
            columns = ', '.join([f'"{key}"' for key in keys])

            # Ensure the columns match the schema
            schema_keys = [col.split('" ')[0] + '"' for col in table_schemas[table_name]]
            if set(keys) != set([key.replace('"', '') for key in schema_keys]):
                logging.error(f"Column names in JSON data do not match schema for table {table_name}. JSON keys: {keys}, Schema keys: {schema_keys}")
                continue

            # Prepare data for insertion
            insert_data = [tuple(item[key] for key in keys) for item in data]

            # Log the data to be inserted
            logging.info(f"Inserting data into {table_name}: {insert_data[:2]}... (showing first 2 records)")

            cursor.executemany(
                f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})',
                insert_data
            )
        else:
            logging.warning(f"No data to insert for table: {table_name}")

def create_database(json_data):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    create_tables(cursor)
    time.sleep(1)
    insert_data(cursor, json_data)
    
    conn.commit()
    conn.close()
    logging.info("Database created and tables populated successfully")

def recreate_database():
    logging.info("Starting database update")
    check_and_create_database()
    json_data = fetch_json_data()
    create_database(json_data)
    logging.info("Database update completed")

def initial_setup():
    recreate_database()

def schedule_updates():
    schedule.every().hour.do(recreate_database)
    while True:
        schedule.run_pending()
        time.sleep(1)
