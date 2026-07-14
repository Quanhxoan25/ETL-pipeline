from sqlalchemy import text
from utils.logger import logger
import pandas as pd
import json
from utils.init_mysql_connection import get_mysql_connection, get_postgres_connection


def transform_to_dim_location_dw(mysql_connection, postgres_connection):
    logger.info("Starting transform to dim location data warehouse")
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

    mysql_query = "SELECT source, raw_data from data_raw"
    chunk_size = 20000
    total_rows = 0

    logger.info("Reading data from raw database")
    mysql_chunks = pd.read_sql(
        mysql_query, mysql_connection, chunksize=chunk_size)

    for i, chunk in enumerate(mysql_chunks):
        city_parsed_records = []
        country_parsed_records = []
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
        df_city = pd.DataFrame(city_parsed_records).dropna(
            subset=["city_name", "country"])
        df_country = pd.DataFrame(
            country_parsed_records).dropna(subset=["country"])

        if df_city.empty and df_country.empty:
            continue

        logger.info("Uploading chunks to staging table")

        df_city.to_sql(
            "staging_dim_city",
            con=postgres_connection,
            if_exists="replace",
            index=False
        )

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
    logger.info("Transforming and loading complete successfully")


if __name__ == "__main__":
    connection = get_mysql_connection()
    pg = get_postgres_connection()
    transform_to_dim_location_dw(connection, pg)
