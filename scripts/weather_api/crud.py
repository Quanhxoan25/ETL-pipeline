from sqlalchemy.orm import Session
from models import FactHistoricalWeather
from datetime import datetime

def get_weather_data(
        db: Session,
        city: str = None,
        country: str = None,
        start_date: datetime = None,
        end_date: datetime = None,
        limit: int = 100,
        offset: int = 0
):
    query = db.query(FactHistoricalWeather)

    if city:
        query = query.filter(FactHistoricalWeather.city_name.ilike(city))
    if country:
        query = query.filter(FactHistoricalWeather.country.ilike(country))
    if start_date: 
        query = query.filter(FactHistoricalWeather.updated_time >= start_date)
    if end_date:
        query = query.filter(FactHistoricalWeather.updated_time <= end_date)

    return query.order_by(FactHistoricalWeather.updated_time.desc()).offset(offset).limit(limit).all()
