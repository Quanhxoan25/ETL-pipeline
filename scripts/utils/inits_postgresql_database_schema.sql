CREATE TABLE IF NOT EXISTS staging_dim_country (
    country VARCHAR(255),
    timezone VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS staging_dim_city (
    city_name VARCHAR(255),
    country VARCHAR(255),
    lat_n NUMERIC(9, 2), 
    lon_n NUMERIC(9, 2)
);

CREATE INDEX IF NOT EXISTS idx_stage_city_lookup ON staging_dim_city (city_name, country, lat_n, lon_n);

create table if not exists dim_country(
	country VARCHAR(100) NOT NULL PRIMARY KEY, 
	timezone VARCHAR(100)
);

create table IF NOT EXISTS dim_city(
	city_name varchar(100) not NULL,
	country  VARCHAR(100) NOT NULL,
	lat_n DECIMAL (9,2), 
	lon_n DECIMAL (9,2),

	CONSTRAINT dim_city_unique PRIMARY KEY (city_name, country)
);

CREATE INDEX IF NOT EXISTS idx_dim_city_name_country ON dim_city (city_name, country);
CREATE INDEX IF NOT EXISTS idx_dim_city_country_geo ON dim_city (country, lat_n, lon_n);
CREATE INDEX IF NOT EXISTS idx_dim_city_name_geo ON dim_city (city_name, lat_n, lon_n);

create table IF NOT EXISTS fact_historical_weather (
	city_name VARCHAR(100) NOT NULL,
	country VARCHAR(100) NOT NULL,
	updated_time timestamp NOT NULL,
	temperature DECIMAL(9,2),
	feels_like DECIMAL(9,2),
	humidity INT,
	wind_speed DECIMAL(9, 2),
	precipitation DECIMAL(9, 2),
	cloud_cover INT,	
	uv_index DECIMAL(9, 2),
	chance_of_rain INT,
	chance_of_snow INT,
	condition VARCHAR(100),
	
	PRIMARY KEY (city_name, country, updated_time)
    /* FOREIGN KEY (city_name, country) REFERENCES dim_city(city_name, country), */
);

