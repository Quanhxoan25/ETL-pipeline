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
	
	primary key (city_id, updated_time)
);
create table IF NOT EXISTS dim_city(
	city_id varchar(10) primary key,
	city_name varchar(50) not NULL
)

CREATE TABLE IF NOT EXISTS dim_condition_weather(
	condition_code INT PRIMARY KEY,
	condition_day VARCHAR(100),
	condition_night VARCHAR(100)
)