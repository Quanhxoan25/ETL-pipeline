import os
from utils.init_mysql_connection import get_mysql_connection
from utils.init_mysql_connection import get_postgres_connection
from utils.pipeline import logger

current_dir = os.path.dirname(os.path.abspath(__file__))

# ket hop tu dia chi hien tai de lay dia chi tuyet doi cua filename
sql_filename = os.path.join(current_dir, "..", "utils",
                            "inits_mysql_database_schema.sql")

postgres_filename = os.path.join(current_dir, "..", "utils",
                                 "inits_postgresql_database_schema.sql")


def execute_sql_file(connection, filepath):
    if not os.path.exists(filepath):
        return False
    sql_script = None
    with open(filepath, "r") as f:
        sql_script = f.read().split(";")
    print(sql_script)
    for command in sql_script:
        sql_command = command.strip()
        logger.info(sql_command)
        if sql_command:
            try:
                connection.execute(sql_command)
                logger.info("Building database successed")
            except Exception as e:
                logger.critical(
                    f"Building database failed in {command}", exc_info=True)
                return False
    return True


def init_sql_database(connection):
    try:
        if not connection:
            return
        cursor = connection.cursor()
        if execute_sql_file(cursor, sql_filename):
            connection.commit()
            print("Commiting database successed")
    except Exception as e:
        print(f"Failure when access/init database: {e}")


def init_postgres_database(connection):
    try:
        if not connection:
            return
        cursor = connection.cursor()
        if execute_sql_file(cursor, postgres_filename):
            connection.commit()
            print("Commiting database successed")
    except Exception as e:
        print(f"Failure when access/init database: {e}")


if __name__ == "__main__":
    connection = get_mysql_connection()
    cursor = connection.cursor()
    if execute_sql_file(cursor, sql_filename):
        connection.commit()
