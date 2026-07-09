from datetime import datetime


def validate_weather_data(location_name, weather_data):
    if not weather_data:
        print(f"Do not have any weather data of {location_name}")
        return False
    updated_time = weather_data["last_updated"]
    temperature = weather_data['temp_c']
    humidity = weather_data['humidity']
    cloud = weather_data['cloud']
    if updated_time is None or temperature is None or humidity is None or humidity is None:
        print(f'Invalid valuable field {location_name}')
        return False
    if not (0 <= humidity <= 100) or not isinstance(humidity, int):
        print(f"Strange humidity value in {location_name}")
        return False
    if not (-60 <= temperature <= 60) or not isinstance(temperature, (int, float)):
        print(f"Strange temperature value in {location_name}")
        return False
    if not (0 <= cloud <= 100) or not isinstance(cloud, int):
        print(f"Strange cloud value in {location_name}")
        return False

    return True
