import os
from dotenv import load_dotenv
import pymysql
import requests
import psycopg2

# Doc cac bien moi truong tu .env
load_dotenv()


def get_mysql_connection():
    try:
        # Khoi tao ket noi voi database sql
        connection = pymysql.connect(
            host=os.getenv("DB_HOST"),
            # tra ve dang int cho cong port
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_DATABASE"),
            charset="utf8mb4",
            client_flag=pymysql.constants.CLIENT.MULTI_STATEMENTS
        )
        return connection
    except Exception as e:
        # Tra ve loi neu nhu ket noi khong thanh cong
        print(f"Having troubleshot while connecting to database {e}")
        return None


def get_postgres_connection():
    try:
        connection = psycopg2.connect(
            host=os.getenv("PG_HOST", "localhost"),
            database=os.getenv("PG_DATABASE"),
            user=os.getenv("PG_USERNAME"),
            password=os.getenv("PG_PASSWORD"),
            port=int(os.getenv("PG_PORT", 5432))
        )
        return connection
    except Exception as e:
        print(f"Having troubleshot while connecting to database {e}")
        return None


def get_api_connection(location):
    BASE_URL = "https://api.weatherapi.com"
    api_url = f"{BASE_URL}/v1/current.json?key={os.getenv('WEATHER_API_KEY')}&q={location}&aqi=no"

    return requests.get(api_url)
