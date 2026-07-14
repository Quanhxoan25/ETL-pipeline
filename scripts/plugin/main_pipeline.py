from sqlalchemy import create_engine, text
import pandas as pd
from utils.logger import logger
from init_database.init_database import init_sql_database, init_postgres_database
from fetch.fetch_to_raw_database_api import fetch_to_raw_database_by_api
from fetch.fetch_to_raw_database_csv import fetch_to_raw_database_by_csv
from transform.transform_to_dim_location_dw import transform_to_dim_location_dw
from transform.transform_to_fact_wth_dw import transform_and_load_to_dw


def run_location_transform(mysql_conn_str, postgres_conn_str, **kwargs):
    """
    Hàm này bọc lại logic của bạn để Airflow gọi qua PythonOperator.
    kwargs giúp bạn lấy các thông tin hệ thống của Airflow nếu cần (ví dụ: ngày chạy).
    """
    # Khởi tạo engine từ connection string mà Airflow truyền vào
    mysql_engine = create_engine(mysql_conn_str)
    postgres_engine = create_engine(postgres_conn_str)

    logger.info("Starting main ELT pipeline")
    with mysql_engine.begin() as mysql_connection, postgres_engine.begin() as postgres_connection:
        try:
            logger.info("Starting init database and datawarehouse schema")
            init_sql_database(mysql_connection)
            init_postgres_database(postgres_connection)

            logger.info("Crawl data into raw database")
            fetch_to_raw_database_by_csv(mysql_connection)
            fetch_to_raw_database_by_api(mysql_connection, postgres_connection)

            logger.info("Transform and loading into data warehouse")
            transform_to_dim_location_dw(mysql_connection, postgres_connection)
            transform_and_load_to_dw(mysql_connection, postgres_connection)

        except Exception as e:
            logger.error(f"Main pipeline failed in some point: {e}")
        pass
