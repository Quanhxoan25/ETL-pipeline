import json
import os
from utils.init_mysql_connection import get_mysql_connection

# lay dia chi file hien tai
current_dir = os.path.dirname(os.path.abspath(__file__))

# ket hop tu dia chi hien tai de lay dia chi tuyet doi cua filename
filename = os.path.join(current_dir, "..", "..", "assets",
                        "data", "weather_conditions.json")


def init_master_condition(connection):
    try:
        cursor = connection.cursor()
        sql_query = """
            INSERT INTO weather_condition 
            (condition_code, condition_day, condition_night)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE condition_code=VALUES(condition_code)
        """

        # doc file weather_conditions
        try:
            with open(filename, "r") as file:
                data = json.load(file)
                for condition in data:
                    code = condition.get("code")
                    day = condition.get("day")
                    night = condition.get("night")
                    cursor.execute(
                        sql_query, (code, day, night))
                    print(f"Succesfull {code}")
                connection.commit()
        except FileNotFoundError:
            print("Error: File Not Found")
    except Exception as e:
        print(f"Something went wromgs: {e}")
