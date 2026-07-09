import json
from dotenv import load_dotenv
from utils.init_mysql_connection import get_mysql_connection, get_api_connection
import pymysql
from utils.data_base_ops import insert_to_sql_raw
import os
from filters.validate_weather_data import validate_weather_data
load_dotenv()
current_dir = os.path.dirname(os.path.abspath(__file__))

file_name = os.path.join(current_dir, "..", "assets",
                         "data", "location_key.json")


def fetch_to_raw_database_by_api(connection):
    try:
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        with open(file_name, "r") as file:
            cities = json.load(file)

        for city in cities:
            location = city['name']
            abbre = city['code']
            response = get_api_connection(location)

            if response.status_code == 200:
                data = response.json()
                location_data = data['location']
                weather_data = data['current']

                if not validate_weather_data(location, weather_data):
                    print("Cannot validate weather data")
                    return
                insert_to_sql_raw(cursor, abbre, location_data, weather_data)
                print(f"Succesfully commit {location} {abbre}")
        connection.commit()
    except Exception as e:
        print(f"Somethings went wrongs: {e}")
