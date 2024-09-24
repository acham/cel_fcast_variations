from pydantic import BaseModel
from datetime import datetime, date

class HourlyForecast(BaseModel):
    """Defines an hourly forecast point"""
    time_added: datetime
    start_time: datetime
    temperature: int
    latitude: float
    longitude: float
    forecast_office: str
    grid_x: int
    grid_y: int

class ForecastSpec(BaseModel):
    """
    Defines a forecast specification
    as it is provided by the API user.
    """
    latitude: float
    longitude: float
    fc_date: date
    hour_of_day: int
    