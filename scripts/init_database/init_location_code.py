import json
import os
from utils.init_mysql_connection import get_mysql_connection

# lay dia chi file hien tai
current_dir = os.path.dirname(os.path.abspath(__file__))

# ket hop tu dia chi hien tai de lay dia chi tuyet doi cua filename
filename = os.path.join(current_dir, "..", "..", "assets",
                        "data", "location_key.json")


def init_master_location_code(connection):
    try:
        cursor = connection.cursor()
        sql_query = """
            INSERT INTO location_mapping 
            (city_name, abbreviation_name) VALUES
            (%s, %s)
            ON DUPLICATE KEY UPDATE city_name=VALUES(city_name)
        """
        try:
            with open(filename, "r", encoding="utf-8") as file:
                data = json.load(file)
                for item in data:
                    name = item.get("name")
                    abbre = item.get("code")
                    cursor.execute(sql_query, (name, abbre))
                    print(f"Successfully {name} {abbre}")
                connection.commit()
        except FileNotFoundError:
            print("Cannot find file data")
    except Exception as e:
        print(f"Something went wrongs: {e}")
