def validate_weather_data(parsed_row):
    if not parsed_row:
        return False
    updated_time = parsed_row["updated_time"]
    temperature = parsed_row['temperature']
    humidity = parsed_row['humidity']
    cloud = parsed_row['cloud_cover']
    if updated_time is None or temperature is None or humidity is None or humidity is None:
        print(f'Invalid valuable field {parsed_row}')
        return False
    if not (0 <= humidity <= 100) or not isinstance(humidity, int):
        print(f"Strange humidity value in {parsed_row}")
        return False
    if not (-60 <= temperature <= 60) or not isinstance(temperature, (int, float)):
        print(f"Strange temperature value in {parsed_row}")
        return False
    if not (0 <= cloud <= 100) or not isinstance(cloud, int):
        print(f"Strange cloud value in {parsed_row}")
        return False

    return True
