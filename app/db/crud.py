from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy import func

from . import models
from app.model.schemas import ForecastSpec, HourlyForecast
from app.config import settings

def add_fc_periods(db: Session, forecasts: list[HourlyForecast]):
    for fc_period in forecasts:
        db_fc = models.HourlyForecast(
            time_added=fc_period.time_added,
            start_time=fc_period.start_time,
            temperature=fc_period.temperature,
            latitude=fc_period.latitude,
            longitude=fc_period.longitude,
            forecast_office=fc_period.forecast_office,
            grid_x=fc_period.grid_x,
            grid_y=fc_period.grid_y
        )
        
        db.add(db_fc)
    
    db.commit()
    print(f"added {len(forecasts)} new forecast points")
    
def get_fc_range(db: Session, fc_spec: ForecastSpec) -> tuple[dict, dict]:
    utc_datetime = datetime(fc_spec.fc_date.year, fc_spec.fc_date.month, fc_spec.fc_date.day, fc_spec.hour_of_day, tzinfo=timezone.utc)
    
    forecast_points = db.query(
            models.HourlyForecast)\
        .filter(func.abs(models.HourlyForecast.latitude - fc_spec.latitude) < settings.coordinate_tolerance)\
        .filter(func.abs(models.HourlyForecast.longitude - fc_spec.longitude) < settings.coordinate_tolerance)\
        .filter(models.HourlyForecast.start_time == utc_datetime)\
        .all()
        
    if len(forecast_points) == 0:
        raise Exception("No forecasts found for specification")
        
    min_temp_point = min(forecast_points, key=lambda fc: fc.temperature)
    max_temp_point = max(forecast_points, key=lambda fc: fc.temperature)
    
    return min_temp_point, max_temp_point
