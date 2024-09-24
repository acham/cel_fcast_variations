import os
import uuid
from dotenv import load_dotenv

load_dotenv()

class Settings:
    latitude: float = float(os.getenv("LOCATION_LATITUDE"))
    longitude: float = float(os.getenv("LOCATION_LONGITUDE"))
    retrieval_interval_sec: float = 60 * float(os.getenv("RETRIEVAL_INTERVAL_MIN", 60.0))
    nws_gridpoints_base_url: str = os.getenv("NWS_GRIDPOINTS_BASE_URL")
    nws_forecasts_base_url: str = os.getenv("NWS_FORECASTS_BASE_URL")
    nws_session_id: str = str(uuid.uuid4())
    coordinate_tolerance: float = float(os.getenv("RETRIEVAL_INTERVAL_MIN", 0.001))
    run_nws_retrieval: bool = os.getenv("RUN_NWS_RETRIEVAL", "true").lower() in ("true", "1", "t")

settings = Settings()
