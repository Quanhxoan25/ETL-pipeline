from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
import pymysql
import requests
import psycopg2

# Doc cac bien moi truong tu .env
load_dotenv()


def get_mysql_connection():
    try:
        host = os.getenv("DB_HOST", "localhost")
        database = os.getenv("DB_DATABASE")
        user = os.getenv("DB_USERNAME")
        password = os.getenv("DB_PASSWORD")
        port = os.getenv("DB_PORT", "3306")

        DATABASE_URL = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"

        engine = create_engine(DATABASE_URL)

        return engine.connect()
    except Exception as e:
        # Tra ve loi neu nhu ket noi khong thanh cong
        print(f"Having troubleshot while connecting to database {e}")
        return None


def get_postgres_connection():
    try:
        host = os.getenv("PG_HOST", "localhost")
        database = os.getenv("PG_DATABASE")
        user = os.getenv("PG_USERNAME")
        password = os.getenv("PG_PASSWORD")
        port = os.getenv("PG_PORT", "5432")

        DATABASE_URL = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"

        engine = create_engine(DATABASE_URL)

        return engine.connect()

    except Exception as e:
        print(f"Having troubleshot while connecting to database {e}")
        return None


def get_api_connection(location):
    BASE_URL = "https://api.weatherapi.com"
    api_url = f"{BASE_URL}/v1/current.json?key={os.getenv('WEATHER_API_KEY')}&q={location}&aqi=no"

    return requests.get(api_url)
