import asyncio
from datetime import datetime, timezone
import requests
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.model.schemas import HourlyForecast, ForecastSpec
from app.db import crud, models
from app.db.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.run_nws_retrieval:
        asyncio.create_task(retrieve_new_forecasts())
    
    yield
    
fast_app = FastAPI(lifespan=lifespan)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@fast_app.get("/")
async def root():
    return {"message": "forecast variations API is up"}

@fast_app.get("/forecast_range")
async def get_forecast_range(fc_spec: ForecastSpec, db: Session = Depends(get_db)):
    """ Get the min and max temperatures for a provided forecast specification """
    try:
        min_temp_fc, max_temp_fc = crud.get_fc_range(db, fc_spec)
    except Exception as e:
        print(f"Error getting forecast range: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=str(e))
    
    return {
        "min": min_temp_fc,
        "max": max_temp_fc
    }

async def retrieve_new_forecasts():
    """ 
    Get metadata from the NWS for the provided coordinates and retrieve 
    and store hourly forecast points for up to 72 hours at regular interval.
    """
    nws_header = {
        "User-Agent": settings.nws_session_id
    }
    
    # Get NWS gridpoints and office for coordinates
    gridpoints_url: str = settings.nws_gridpoints_base_url + f"/{settings.latitude},{settings.longitude}"
    try:
        gridpoints_response = requests.get(gridpoints_url, headers=nws_header)
        gridpoints_response.raise_for_status()
        gridpoints_data: dict = gridpoints_response.json()
        forecast_office: str = gridpoints_data["properties"]["gridId"]
        grid_x: int = gridpoints_data["properties"]["gridX"]
        grid_y: int = gridpoints_data["properties"]["gridY"]
    except Exception as e:
        print(f"Error fetching NWS metadata: {e}", file=sys.stderr)
        sys.exit(1)
    
    forecasts_url: str = settings.nws_forecasts_base_url + f"/{forecast_office}/{grid_x},{grid_y}/forecast/hourly"
    
    while True:
        db = SessionLocal()
        
        try:
            fc_response = requests.get(forecasts_url, headers=nws_header)
            fc_response.raise_for_status()
            fc_data = fc_response.json()
        except Exception as e:
            print(f"Error fetching NWS data: {e}", file=sys.stderr)
            db.close()
            await asyncio.sleep(settings.retrieval_interval_sec)
            continue
            
        try:
            if len(fc_data['properties']['periods']) < 72:
                periods_to_write = len(fc_data['properties']['periods'])
            else: 
                periods_to_write = 72
            
            fc_periods = []
            time_added = datetime.now().astimezone(timezone.utc)
            for period in fc_data['properties']['periods'][:periods_to_write]:
                hourly_fc = HourlyForecast(
                    time_added=time_added,
                    start_time=datetime.fromisoformat(period['startTime']).astimezone(timezone.utc),
                    temperature=period['temperature'],
                    latitude=settings.latitude,
                    longitude=settings.longitude,
                    forecast_office=forecast_office,
                    grid_x=grid_x,
                    grid_y=grid_y
                )
                
                fc_periods.append(hourly_fc)
                
            crud.add_fc_periods(db, fc_periods)
        except Exception as e:
            print(f"Error adding forecast data: {e}", file=sys.stderr)
        finally:
            db.close()
        
        await asyncio.sleep(settings.retrieval_interval_sec)
