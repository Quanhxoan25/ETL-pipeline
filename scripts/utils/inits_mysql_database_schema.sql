CREATE TABLE IF NOT EXISTS raw_location_infor (
	city_id VARCHAR(10) PRIMARY KEY,
	city_name VARCHAR(50) NOT NULL,
	region VARCHAR(100),
	country VARCHAR(50),
	lat_n DECIMAL(10,6),
	lon_n DECIMAL(10,6),
	tz_id VARCHAR(50),
	localtime_epoch INT,
	local_time DATETIME
) Engine=InnoDB DEFAULT CHARSET=UTF8MB4;

CREATE TABLE IF NOT EXISTS location_mapping (
	city_name VARCHAR(100) PRIMARY KEY,
	abbreviation_name VARCHAR(10) 
) Engine=InnoDB DEFAULT CHARSET=UTF8MB4;

CREATE TABLE IF NOT EXISTS weather_condition (
	condition_code INT NOT NULL PRIMARY KEY,
	condition_day VARCHAR(100),
	condition_night VARCHAR(100)
) Engine=InnoDB DEFAULT CHARSET=UTF8MB4;

CREATE TABLE IF NOT EXISTS raw_current_weather ( 
	city_id VARCHAR(10) NOT NULL PRIMARY KEY,
	updated_time DATETIME,
	temperature DECIMAL(4, 1),
	feels_like DECIMAL(4,1),
	humidity INT,
	wind_speed DECIMAL(5, 2),
	precipitation DECIMAL(9, 2),
	cloud_cover INT,
	uv_index DECIMAL(3, 1),
	chance_of_rain INT,
	chance_of_snow INT,
	condition_code INT NOT NULL
) Engine=InnoDB DEFAULT CHARSET=UTF8MB4


