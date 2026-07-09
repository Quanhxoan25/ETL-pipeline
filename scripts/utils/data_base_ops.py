def insert_to_sql_raw(cursor, abbre_name, location_data, weather_data):
    sql_location_query = """
            INSERT INTO raw_location_infor
            (city_id, city_name, region, country, lat_n, lon_n, tz_id, localtime_epoch, local_time)
            VALUES (%s, %s,%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE country=VALUES(country)
        """

    cursor.execute(sql_location_query, (abbre_name, location_data.get('name'), location_data.get('region'), location_data.get('country'), location_data.get(
                   'lat'), location_data.get('lon'), location_data.get('tz_id'), location_data.get('localtime_epoch'), location_data.get('localtime')))

    sql_weather_query = """
            INSERT INTO raw_current_weather
            (city_id, updated_time, temperature, feels_like, humidity, wind_speed, precipitation, cloud_cover, uv_index, chance_of_rain, chance_of_snow, condition_code) 
            VALUES (%s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                updated_time = VALUES(updated_time),
                temperature = VALUES(temperature),
                feels_like = VALUES(feels_like),
                humidity = VALUES(humidity),
                wind_speed = VALUES(wind_speed),
                precipitation = VALUES(precipitation),
                cloud_cover = VALUES(cloud_cover),
                uv_index = VALUES(uv_index),
                chance_of_rain = VALUES(chance_of_rain),
                chance_of_snow = VALUES(chance_of_snow),
                condition_code = VALUES(condition_code);
        """
    cursor.execute(sql_weather_query,
                   (
                       abbre_name,
                       weather_data.get("last_updated"),
                       weather_data.get("temp_c"),
                       weather_data.get('feelslike_c'),
                       weather_data.get('humidity'),
                       weather_data.get('wind_kph'),
                       weather_data.get('pressure_mb'),
                       weather_data.get('cloud'),
                       weather_data.get('uv'),
                       weather_data.get('chance_of_rain'),
                       weather_data.get('chance_of_snow'),
                       weather_data.get('condition')['code']
                   ))


def sync_to_postgres_warehouse(mysql_cursor, postgre_sql_cursor):
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
        print(city)
        postgre_sql_cursor.execute(
            sql_insert_dim_city, (city["city_id"], city["city_name"]))
        print(f"Commit successfully {city["city_name"]}")

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
