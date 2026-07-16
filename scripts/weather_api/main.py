from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import database, schemas, crud

app = FastAPI(
    title="Weather Data Mart API",
    description="API query historical weather data",
    version="1.0.0"
)


@app.get("/app/v1/weather", response_model=List[schemas.WeatherResponse])
def read_weather(
    city:  str = Query(None, description="City Name"),
    country: str = Query(None, description="Country Name"),
    start_date: datetime = Query(None, description="Start date time"),
    end_date: datetime = Query(None, description="End date time"),
    limit: int = Query(None, description="Limited Report"),
    offset: int = Query(None, description="Offseted Report"),
    db: Session = Depends(database.get_db)

):
    try: 
        data = crud.get_weather_data(
            db=db,
            city=city,
            country=country,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset
        )
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
