from utils.logger import logger
from sqlalchemy import text
import pandas as pd
import json
from utils.init_mysql_connection import get_mysql_connection, get_postgres_connection
from filters.validate_weather_data import validate_weather_data


def check_and_expand_postgres_schema(postgres_connection, target_field, table_name):
    query = text(f"""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = '{table_name}';
    """
                 )

    existing_column = {row[0].lower()
                       for row in postgres_connection.execute(query).fetchall()}

    def get_data_type_by_name(col_name):
        col_name = col_name.lower()
        if "temp" in col_name or "feel" in col_name or "speed" in col_name or "pre" "precip" in col_name or "uv" in col_name:
            return "DECIMAL(9,2)"
        elif "humidity" in col_name or "cloud" in col_name or "chance" in col_name:
            return "INT"
        else:
            return "VARCHAR(255)"

    has_changes = False
    for field in target_field:
        field_clean = field.lower()

        if field_clean not in existing_column:
            db_type = get_data_type_by_name(field_clean)
            logger.warning(
                f"Finding new column: {field_clean} Process scaling database...")

            alter_query = text(
                f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {field_clean} {db_type};")
            postgres_connection.execute(alter_query)
            has_changes = True

            logger.info(
                f"Successful in auto scaling: {field_clean} ({db_type})")

    if has_changes:
        try:
            postgres_connection.commit()
        except Exception as e:
            logger.error(f"Error in checking field: {e}")


def transform_and_load_to_dw(mysql_connetion, postgres_connection):
    try:
        logger.info("Starting transform into data warehouse...")

        column_fields = [
            "city_name",
            "country",
            "updated_time",
            "temperature",
            "feels_like",
            "humidity",
            "wind_speed",
            "precipitation",
            "cloud_cover",
            "uv_index",
            "chance_of_rain",
            "chance_of_snow",
            "condition"
        ]

        column_str = ', '.join(column_fields)
        placeholder_str = ', '.join([f":{field}" for field in column_fields])

        insert_query = text(f"""
            INSERT INTO fact_historical_weather ({column_str})
            VALUES ({placeholder_str})
            ON CONFLICT (city_name, country, updated_time) DO NOTHING          
        """
        )
        check_and_expand_postgres_schema(
            postgres_connection, column_fields, "fact_historical_weather")
        mysql_query = "SELECT source, raw_data FROM data_raw"
        chunk_size = 20000
        total_row = 0

        logger.info("Reading raw data from MySQL database")
        mysql_chunks = pd.read_sql(
            mysql_query, mysql_connetion, chunksize=chunk_size)

        for i, chunk in enumerate(mysql_chunks):
            parsed_record = []
            for _, row in chunk.iterrows():
                try:
                    data = json.loads(row['raw_data'])
                    source = row['source']
                    parsed_row = {}
                    if source == "CSV":
                        for field in column_fields:
                            if field == 'city_name':
                                val = data.get('location_name')
                            elif field == "country":
                                val = data.get('country')
                            elif field == 'updated_time':
                                val = data.get('last_updated')
                            elif field == 'temperature':
                                val = data.get('temperature_celsius')
                            elif field == 'feels_like':
                                val = data.get('feels_like_celsius')
                            elif field == 'cloud_cover':
                                val = data.get('cloud')
                            elif field == 'precipitation':
                                val = data.get('precip_mm')
                            elif field == 'wind_speed':
                                val = data.get('wind_kph')
                            elif field == "condition":
                                val = data.get('condition_text')
                            else:
                                val = data.get(field)

                            if val is not None:
                                if field in ['humidity', 'cloud_cover', 'chance_of_rain', 'chance_of_snow']:
                                    parsed_row[field] = int(val)
                                elif field in ['temperature', 'feels_like', 'wind_speed', 'precipitation', 'uv_index']:
                                    parsed_row[field] = float(val)
                                else:
                                    parsed_row[field] = str(val)
                            else:
                                parsed_row[field] = None

                    elif source == "API":
                        location = data.get("location")
                        weather = data.get("current")

                        for field in column_fields:
                            if field == 'city_name':
                                val = location.get('name')
                            elif field == "country":
                                val = location.get('country')
                            elif field == 'updated_time':
                                val = weather.get('last_updated')
                            elif field == 'temperature':
                                val = weather.get('temp_c')
                            elif field == 'feels_like':
                                val = weather.get('feelslike_c')
                            elif field == 'cloud_cover':
                                val = weather.get('cloud')
                            elif field == 'precipitation':
                                val = weather.get('precip_mm')
                            elif field == 'wind_speed':
                                val = weather.get('wind_kph')
                            elif field == "condition":
                                val = weather.get('condition').get('text')
                            elif field == "uv_index":
                                val = weather.get('uv')
                            elif field == "humidity":
                                val = weather.get("humidity")
                            elif field == "chance_of_snow":
                                val = weather.get("chance_of_snow")
                            elif field == "chance_of_rain":
                                val = weather.get("chance_of_rain")
                            else:
                                val = data.get(field)

                            if val is not None:
                                if field in ['humidity', 'cloud_cover', 'chance_of_rain', 'chance_of_snow']:
                                    parsed_row[field] = int(val)
                                elif field in ['temperature', 'feels_like', 'wind_speed', 'precipitation', 'uv_index']:
                                    parsed_row[field] = float(val)
                                else:
                                    parsed_row[field] = str(val)
                            else:
                                parsed_row[field] = None
                    if validate_weather_data(parsed_row):
                        parsed_record.append(parsed_row)
                except Exception as e:
                    logger.info(
                        f"Troubleshot when reading data from raw database: {e}")
                    continue
            if parsed_record:
                postgres_connection.execute(insert_query, parsed_record)

                total_row += len(parsed_record)
                logger.info(
                    f"Processed chunk {i+1}, total rows processed: {total_row}")
        logger.info("Transforming and loading complete successfully")
    except Exception as e:
        logger.error(f"🚨 Lỗi hệ thống: {e}", exc_info=True)


if __name__ == "__main__":
    connection = get_mysql_connection()
    pg = get_postgres_connection()
    transform_and_load_to_dw(connection, pg)
