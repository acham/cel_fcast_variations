from pydantic import BaseModel
from datetime import datetime, date

class HourlyForecast(BaseModel):
    time_added: datetime
    start_time: datetime
    temperature: int
    latitude: float
    longitude: float
    forecast_office: str
    grid_x: int
    grid_y: int

class ForecastSpec(BaseModel):
    latitude: float
    longitude: float
    fc_date: date
    hour_of_day: int
    