from utils.data_base_ops import sync_to_postgres_warehouse
from utils.init_mysql_connection import get_mysql_connection, get_postgres_connection
import pymysql


def load_data_to_dw(mysql_connection, postgres_connection):
    try:
        if not mysql_connection or not postgres_connection:
            print("Checking your connection to your database")
            return

        sync_to_postgres_warehouse(mysql_connection, postgres_connection)
        postgres_connection.commit()
    except Exception as e:
        print(f"Having trouble on commiting data: {e}")
