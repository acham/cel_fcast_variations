from .database import Base
from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.orm import relationship

class HourlyForecast(Base):
    __tablename__ = "forecasts"
    
    id = Column(Integer, primary_key=True)
    time_added = Column(DateTime)
    start_time = Column(DateTime)
    temperature = Column(Integer)
    latitude = Column(Float)
    longitude = Column(Float)
    forecast_office = Column(String)
    grid_x = Column(Integer)
    grid_y = Column(Integer)
