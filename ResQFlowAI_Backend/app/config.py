import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "ResQFlow AI"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Source-Agnostic AI Emergency Response and Coordination System"
    API_V1_STR: str = "/api"
    DATABASE_URL: str = "sqlite:///./resqflow.db"
    
    # City Center Coordinates (Metropolitan Demo Area)
    CITY_CENTER_LAT: float = 12.9719
    CITY_CENTER_LNG: float = 77.5937
    CITY_NAME: str = "Metro Central City"
    
    # Deduplication Thresholds (DBSCAN)
    DBSCAN_EPS_METERS: float = 250.0  # meters
    DBSCAN_TIME_WINDOW_MINS: float = 15.0  # minutes
    
    # Storage for uploaded media
    MEDIA_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "media")

settings = Settings()
os.makedirs(settings.MEDIA_DIR, exist_ok=True)
