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

logger.info(os.path.exists(file_name))

def fetch_to_raw_database_by_csv(mysql_connection):
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

        logger.info("Success")
    except Exception as e:
        logger.info(f"Somethings went wrongs: {e}", exc_info=True)


if __name__ == "__main__":
    connection = get_mysql_connection()
    fetch_to_raw_database_by_csv(connection)
