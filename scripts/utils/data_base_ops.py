import pymysql
from sqlalchemy import text


def insert_to_sql_raw(mysql_connection, source, raw_data):
    sql_query = text("""
            INSERT INTO data_raw (source, raw_data)
            VALUES (:source, :raw_data)
        """)

    mysql_connection.execute(
        sql_query, {"source": source, "raw_data": raw_data})


def sync_to_postgres_warehouse(mysql_conncetion, postgre_sql_connection):
    mysql_cursor = mysql_conncetion.cursor(pymysql.cursors.DictCursor)
    postgre_sql_cursor = postgre_sql_connection.cursor()
    sql_insert_dim_city = """
        INSERT INTO dim_city (city_id, city_name)
        VALUES (%s, %s) 
        ON CONFLICT (city_id) DO UPDATE SET city_name = EXCLUDED.city_name
    """

    sql_insert_fact_weather = """
        INSERT INTO fact_historical_weather 
        (city_id, updated_time, temperature, feels_like, humidity, wind_speed, precipitation, cloud_cover, uv_index, chance_of_rain, chance_of_snow, condition_code)
        VALUES (%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s, %s)
        ON CONFLICT (city_id, updated_time) DO NOTHING
    """

    sql_insert_dim_condition_weather = """
        INSERT INTO dim_condition_weather (condition_code, condition_day, condition_night)
        VALUES (%s, %s, %s) 
        ON CONFLICT (condition_code) DO NOTHING
    """

    mysql_cursor.execute(
        "SELECT city_id, city_name FROM raw_location_infor")
    cities = mysql_cursor.fetchall()
    for city in cities:
        try:

            print(city)
            postgre_sql_cursor.execute(
                sql_insert_dim_city, (city["city_id"], city["city_name"]))
            print(f"Commit successfully {city["city_name"]}")
        except Exception as e:
            postgre_sql_connection.rollback()
            print(f"Dòng dữ liệu của {city['city_name']} bị lỗi: {e}")
            continue

    mysql_cursor.execute("SELECT * FROM weather_condition")
    conditions = mysql_cursor.fetchall()
    for condition in conditions:
        print(condition)
        postgre_sql_cursor.execute(
            sql_insert_dim_condition_weather, (
                condition["condition_code"], condition["condition_day"], condition["condition_night"])
        )
        print(f"Commit successfully {condition["condition_code"]}")

    mysql_cursor.execute("SELECT * FROM raw_current_weather")
    chunk = 500
    while True:
        rows = mysql_cursor.fetchmany(chunk)
        if not rows:
            break
        for row in rows:
            print(row)
            postgre_sql_cursor.execute(sql_insert_fact_weather, (row["city_id"], row["updated_time"], row["temperature"], row["feels_like"], row["humidity"],
                                                                 row["wind_speed"], row["precipitation"], row["cloud_cover"], row["uv_index"], row["chance_of_rain"], row["chance_of_snow"], row["condition_code"]))
            print(f"Commit successfullu {row["city_id"]}")
