create table IF NOT EXISTS fact_historical_weather (
	city_id VARCHAR(10),
	updated_time timestamp,
	temperature DECIMAL(5,2),
	feels_like DECIMAL(4,1),
	humidity INT,
	wind_speed DECIMAL(5, 2),
	precipitation DECIMAL(9, 2),
	cloud_cover INT,
	uv_index DECIMAL(3, 1),
	chance_of_rain INT,
	chance_of_snow INT,
	condition_code INT,
	
	PRIMARY KEY (city_name, country, updated_time),
    FOREIGN KEY (city_name, country) REFERENCES dim_city(city_name, country),
    FOREIGN KEY (condition_code) REFERENCES dim_condition_weather(condition_code)
);
create table IF NOT EXISTS dim_city(
	city_name varchar(50) not NULL,
	country  VARCHAR(20) NOT NULL,
	lat_n DECIMAL (5,2), 
	lon_n DECIMAL (5,2)

	PRIMARY KEY (city_name, country)
	FOREIGN KEY (country) REFERENCES dim_country(country)
)

create table if not exists dim_country(
	country VARCHAR(20) NOT NULL PRIMARY KEY, 
	timezone VARCHAR(50)
)

CREATE TABLE IF NOT EXISTS dim_condition_weather(
	condition_code INT PRIMARY KEY,
	condition_day VARCHAR(100),
	condition_night VARCHAR(100)
)