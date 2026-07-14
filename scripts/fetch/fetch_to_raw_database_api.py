import json
from utils.init_mysql_connection import get_api_connection, get_mysql_connection, get_postgres_connection
import pymysql
from utils.data_base_ops import insert_to_sql_raw
import os
import pandas as pd
from utils.logger import logger
from sqlalchemy import text

current_dir = os.path.dirname(os.path.abspath(__file__))

file_name = os.path.join(current_dir, "..", "..", "assets",
                         "data", "location_key.json")

logger.info(os.path.exists(file_name))


def fetch_to_raw_database_by_api(mysql_connection, pg_connection):
    logger.info("Starting crawl data into database")
    try:
        insert_query = text("""
            INSERT INTO data_raw (source, raw_data) 
            VALUES (:source, :raw_data)
        """)
        cities = []
        try:
            query = "SELECT city_name FROM dim_city"
            df_cities = pd.read_sql(query, pg_connection)

            if not df_cities.empty:
                logger.info(f"Have {len(df_cities)} cities in data_warehouse")
                cities = df_cities["city_name"].tolist()
        except Exception as e:
            logger.critical("Cannot take data from datawarehouse")

        if not cities:
            with open(file_name, "r") as file:
                json_data = json.load(file)
                cities = [item['name'] for item in json_data]
        params = []
        for city in cities:
            location = city
            try:
                response = get_api_connection(location)
                if response.status_code != 200:
                    logger.error(f"API Error for {location} (Status {response.status_code}): {response.text}")
                    continue
                data = response.json()
                raw_data = json.dumps(data, ensure_ascii=False)
                params.append({
                    "source": "API",
                    "raw_data": raw_data
                })  
                logger.info(f"Succesfully commit {location}")
            except Exception as e: 
                logger.error(f"Have trouble in {location} {e}")
                continue
        if params: 
            mysql_connection.execute(insert_query, params)
            logger.info(f"Successfully committed {len(params)} records to data_raw.")
        else: 
            logger.warning("No data commit to database")
    except Exception as e:
        logger.critical(f"Somethings went wrongs: {e}", exc_info=True)


if __name__ == "__main__":
    connection = get_mysql_connection()
    pg = get_postgres_connection()
    fetch_to_raw_database_by_api(connection, pg)
