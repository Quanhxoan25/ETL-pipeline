import pandas as pd
import os
from sqlalchemy import text
import json
from utils.init_mysql_connection import get_mysql_connection
from utils.data_base_ops import insert_to_sql_raw
from utils.logger import logger

current_dir = os.path.dirname(os.path.abspath(__file__))

file_name = os.path.join(current_dir, "..", "..", "assets",
                         "data", "GlobalWeatherRepository.csv")

METADATA_FILE = os.path.join(current_dir, "..", "..", "assets",
                         "data", "csv_metadata.csv")

logger.info(os.path.exists(file_name))

def get_csv_last_modified():
    try:
        return os.path.getmtime(file_name)
    except OSError as e:
        logger.error(f"Can't modify time for {file_name}: {e}")
        return None

def should_read_csv(current_mtime):
    if not os.path.exists(METADATA_FILE):
        return True  
    try:
        with open(METADATA_FILE, 'r') as f:
            metadata = json.load(f)
            return metadata.get("last_modified") != current_mtime
    except Exception as e:
        logger.warning(f"Error reading metadata file, will default to reading CSV: {e}")
        return True

def save_metadata(current_mtime):
    try:
        with open(METADATA_FILE, 'w') as f:
            json.dump({"last_modified": current_mtime}, f)
        logger.info(f"Saved new metadata state to {METADATA_FILE}")
    except Exception as e:
        logger.error(f"Could not save metadata: {e}")

def fetch_to_raw_database_by_csv(mysql_connection):
    current_mtime = get_csv_last_modified()
    if current_mtime is None:
        logger.error("Stop execution because CSV file metadata cannot be retrieved.")
        return

    if not should_read_csv(current_mtime):
        logger.info("[Pipeline] CSV file has NOT changed. Skipping database ingestion to save resources!")
        return
    logger.info("Starting read csv file into database")
    try:
        chunk_size = 10000
        total_row = 0

        query = text("""
            INSERT INTO data_raw (source, raw_data) 
            VALUES (:source, :raw_data)
        """)

        chunks = pd.read_csv(file_name, encoding="utf-8", chunksize=chunk_size)

        for i, chunk in enumerate(chunks):
            rows = chunk.to_dict(orient='records')
            params = []
            for row in rows:
                raw_data = json.dumps(row, ensure_ascii=False)
                params.append({
                    "source": "CSV",
                    "raw_data": raw_data
                })
            mysql_connection.execute(query, params)
            total_row += len(chunk)
            logger.info(
                f"Finished loading batch {i+1} ({len(chunk)} rows). Cumulative total: {total_row} rows.")
        save_metadata(current_mtime)
        logger.info("Success")
    except Exception as e:
        logger.info(f"Somethings went wrongs: {e}", exc_info=True)


if __name__ == "__main__":
    connection = get_mysql_connection()
    fetch_to_raw_database_by_csv(connection)
