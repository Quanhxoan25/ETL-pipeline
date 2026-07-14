from sqlalchemy import text
from utils.logger import logger
import pandas as pd
import json
from utils.init_mysql_connection import get_mysql_connection, get_postgres_connection
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

file_name = os.path.join(current_dir, "..", "..", "assets",
                         "data", "db_metadata.json")

def get_last_processed_id():
    if os.path.exists(file_name):
        try: 
            with open(file_name, "r") as f: 
                metadata = json.load(f)
                return metadata.get("last_processed_dim_id", 0)
        except Exception as e:
            logger.warning(f"Can't read file json {e}")
    return 0 

def save_last_id(last_id):
    try:
        # Đọc dữ liệu hiện tại trước để tránh ghi đè mất key của Location
        metadata = {}
        if os.path.exists(file_name):
            try:
                with open(file_name, "r") as f:
                    metadata = json.load(f)
            except Exception:
                pass
                
        # Chỉ cập nhật key của weather
        metadata["last_processed_dim_id"] = last_id
        
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        with open(file_name, 'w') as f:
            json.dump(metadata, f, indent=4) # indent=4 cho đẹp, dễ đọc
        logger.info(f"Saving new weather index: {last_id}")
    except Exception as e:
        logger.error(f"Cant write file: {e}")

def transform_to_dim_location_dw(mysql_connection, postgres_connection):
    logger.info("Starting transform to dim location data warehouse")
    last_processed_id = get_last_processed_id()
    city_column_fields = [
        "city_name",
        "country",
        "lat_n",
        "lon_n"
    ]

    country_column_fields = [
        "country",
        "timezone"
    ]

    city_column_str = (', ').join(city_column_fields)
    city_params_str = (', ').join(f":{field}" for field in city_column_fields)
    country_column_str = (', ').join(country_column_fields)
    country_params_str = (', ').join(
        f":{field}" for field in country_column_fields)

    dim_city_query = text(f"""
        INSERT INTO dim_city ({city_column_str})
        VALUES ({city_params_str})
        ON CONFLICT (lat_n, lon_n) DO NOTHING;
    """)

    dim_country_query = text(f"""
        INSERT INTO dim_country ({country_column_str})
        VALUES ({country_params_str})
        ON CONFLICT (country) DO NOTHING;
    """)

    mysql_query = "SELECT indexing, source, raw_data from data_raw where indexing > %(last_id)s ORDER BY indexing ASC"
    chunk_size = 20000
    total_rows = 0
    max_id = last_processed_id
    has_new_data = False

    logger.info("Reading data from raw database")
    mysql_chunks = pd.read_sql(
        mysql_query, mysql_connection, params={"last_id": last_processed_id},chunksize=chunk_size)

    for i, chunk in enumerate(mysql_chunks):
        has_new_data = True
        city_parsed_records = []
        country_parsed_records = []

        max_id = int(chunk['indexing'].max())
        for _, row in chunk.iterrows():
            try:
                data = json.loads(row["raw_data"])
                source = row['source']

                if source == "CSV":
                    country_data = {
                        "country": data.get("country"),
                        "timezone": data.get("timezone")
                    }

                    city_data = {
                        "city_name": data.get("location_name"),
                        "country": data.get("country"),
                        "lat_n": round(float(data.get("latitude")), 2) if data.get("latitude") else None,
                        "lon_n": round(float(data.get("longitude")), 2) if data.get("longitude") else None

                    }
                elif source == "API":
                    location = data.get("location")
                    country_data = {
                        "country": location.get("country"),
                        "timezone": data.get("tz_id")
                    }

                    city_data = {
                        "city_name": location.get("name").strip(),
                        "country": data.get("country"),
                        "lat_n": round(float(data.get("lat_n")), 2) if data.get("lat_n") else None,
                        "lon_n": round(float(data.get("lon_n")), 2) if data.get("lon_n") else None
                    }

                if country_data.get("country"):
                    country_parsed_records.append(country_data)
                if city_data.get("city_name") and city_data.get("country"):
                    city_parsed_records.append(city_data)
            except Exception as e:
                logger.error(
                    f"Troubleshot when reading data from raw database: {e}", exc_info=True)
                continue

        if city_parsed_records:
            df_city = pd.DataFrame(city_parsed_records).dropna(subset=["city_name", "country"])
        else:
            df_city = pd.DataFrame(columns=["city_name", "country", "lat_n", "lon_n"])
        df_country = pd.DataFrame(
            country_parsed_records).dropna(subset=["country"])

        if country_parsed_records:
            df_country = pd.DataFrame(country_parsed_records).dropna(subset=["country"])
        else:
            df_country = pd.DataFrame(columns=["country", "timezone"])

        logger.info("Uploading chunks to staging table")

        if df_city.empty and df_country.empty:
            logger.info(f"Chunk {i+1} has no valid data to insert. Skipping...")
            continue

        logger.info("Uploading chunks to staging table")

        if not df_city.empty:
            df_city.to_sql(
                "staging_dim_city",
                con=postgres_connection,
                if_exists="replace",
                index=False
            )

        if not df_country.empty:
            df_country.to_sql(
                "staging_dim_country",
                con=postgres_connection,
                if_exists="replace",
                index=False
            )

        if not df_country.empty:
            postgres_connection.execute(
                text("""
                INSERT INTO dim_country (country, timezone)
                SELECT DISTINCT country, timezone FROM staging_dim_country
                ON CONFLICT (country) DO NOTHING;
            """)
            )

        if not df_country.empty:
            postgres_connection.execute(
                text("""
                INSERT INTO dim_country (country, timezone)
                SELECT DISTINCT country, timezone FROM staging_dim_country
                ON CONFLICT (country) DO NOTHING;
            """)
            )

        if not df_city.empty:
            postgres_connection.execute(
                text("""
                    INSERT INTO dim_city (city_name, country, lat_n, lon_n)
                        SELECT DISTINCT stage.city_name, stage.country, stage.lat_n, stage.lon_n
                        FROM staging_dim_city stage
                        WHERE stage.city_name IS NOT NULL
                        AND stage.country IS NOT NULL
                        AND NOT EXISTS (
                            SELECT 1 FROM dim_city target
                            WHERE (
                            (stage.city_name = target.city_name AND stage.country = target.country)
                            OR (stage.country = target.country AND stage.lat_n = target.lat_n AND stage.lon_n = target.lon_n)
                            OR (stage.city_name = target.city_name AND stage.lat_n = target.lat_n AND stage.lon_n = target.lon_n)
                    ))
                    ON CONFLICT ON CONSTRAINT dim_city_unique DO NOTHING;
            """)
            )
        logger.info(f"Successfully processed and filtered chunk {i+1}")

        if country_parsed_records:
            postgres_connection.execute(
                dim_country_query, country_parsed_records)
        if city_parsed_records:
            postgres_connection.execute(dim_city_query, city_parsed_records)

        total_rows += len(chunk)
        logger.info(
            f"Processed chunk {i+1}, total rows processed: {total_rows}")
    if has_new_data:
        save_last_id(max_id)
        logger.info("Transforming and loading complete successfully")
        postgres_connection.execute(text("truncate table staging_dim_country"))
        postgres_connection.execute(text("truncate table staging_dim_city"))
    else:
        logger.info("Dont have new data")


if __name__ == "__main__":
    connection = get_mysql_connection()
    pg = get_postgres_connection()
    transform_to_dim_location_dw(connection, pg)
