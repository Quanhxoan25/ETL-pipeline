from utils.init_mysql_connection import get_mysql_connection, get_postgres_connection
from scripts.fetch.fetch_to_raw_database_api import fetch_to_raw_database_by_api
from load_to_dw import load_data_to_dw
from init_database.init_database import init_postgres_database, init_sql_database
from init_database.init_condition import init_master_condition
from init_database.init_location_code import init_master_location_code


def run_etl_pipeline():
    mysql_connection = None
    postgres_connection = None

    try:
        mysql_connection = get_mysql_connection()
        postgres_connection = get_postgres_connection()

        init_sql_database(mysql_connection)
        init_postgres_database(postgres_connection)

        init_master_condition(mysql_connection)
        init_master_location_code(mysql_connection)

        fetch_to_raw_database_by_api(mysql_connection)
        load_data_to_dw(mysql_connection, postgres_connection)
    except Exception as e:
        print(f"Having troubleshot: {e}")
    finally:
        mysql_connection.close()
        postgres_connection.close()


if __name__ == "__main__":
    run_etl_pipeline()
