from sqlalchemy import Column, Integer, String, Float, ForeignKey
from app.database import Base

class Ambulance(Base):
    __tablename__ = "ambulances"

    id = Column(Integer, primary_key=True, index=True)
    callsign = Column(String(32), unique=True, index=True)
    type = Column(String(16), default="ALS") # ALS (Advanced Life Support), BLS (Basic Life Support)
    status = Column(String(32), default="available") # available, dispatched, busy, maintenance
    current_latitude = Column(Float, nullable=False)
    current_longitude = Column(Float, nullable=False)
    base_station = Column(String(64), nullable=True)
    speed_kmh = Column(Float, default=50.0)
    contact_number = Column(String(32), default="+1-800-555-AMBU")
    current_incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)
