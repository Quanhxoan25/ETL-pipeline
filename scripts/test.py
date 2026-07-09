import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def test_progres_connect():
    connection = None
    cursor = None

    try:
        connection = psycopg2.connect(
            host=os.getenv("PG_HOST", "localhost"),
            database=os.getenv("PG_DATABASE"),
            user=os.getenv("PG_USERNAME"),
            password=os.getenv("PG_PASSWORD"),
            port=int(os.getenv("PG_PORT", 5432))
        )
        cursor = connection.cursor()
        mock_city_id = "HAN"
        mock_city_name = "Hanoi"
        mock_updated_time = "2026-07-08 16:00:00"

        sql_dim = """
            INSERT INTO dim_city (city_id, city_name)
            values (%s, %s)
            ON CONFLICT (city_id) DO UPDATE SET city_name = EXCLUDED.city_name;
        """

        cursor.execute(sql_dim, (mock_city_id, mock_city_name))

        sql_fact = """
            INSERT INTO fact_historical_weather 
            (city_id, updated_time, temperature, feels_like, humidity, wind_speed, precipitation, cloud_cover, uv_index, condition_code)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (city_id, updated_time) DO NOTHING;
        """
        cursor.execute(sql_fact, (
            mock_city_id, mock_updated_time, 32.5, 36.0, 75, 12.5, 0.0, 40, 6, 1000
        ))

        connection.commit()
    except Exception as e:
        print(f"❌ THẤT BẠI: Đã xảy ra lỗi trong quá trình test: {e}")
        if connection:
            connection.rollback()
            print("🔄 Đã rollback dữ liệu tránh làm bẩn DB.")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
        print("🔌 Đã đóng kết nối an toàn.")


if __name__ == "__main__":
    test_progres_connect()
