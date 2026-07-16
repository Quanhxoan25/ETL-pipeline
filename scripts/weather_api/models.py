from sqlalchemy import Column, String, Integer, Numeric, DateTime, PrimaryKeyConstraint, Text
from database import Base

class FactHistoricalWeather(Base):
    __tablename__ = "fact_historical_weather"

    city_name = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False)
    updated_time = Column(DateTime, nullable=False)
    temperature = Column(Numeric(9, 2))
    feels_like = Column(Numeric(9, 2))
    humidity = Column(Integer)
    wind_speed = Column(Numeric(9, 2))
    precipitation = Column(Numeric(9, 2))
    cloud_cover = Column(Integer)
    uv_index = Column(Numeric(9, 2))
    chance_of_rain = Column(Integer)
    chance_of_snow = Column(Integer)
    condition = Column(Text)

    __table_args__ = (
        PrimaryKeyConstraint('city_name', 'country', 'updated_time'),
    )
