from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    ambulance_id = Column(Integer, ForeignKey("ambulances.id"), nullable=False)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False)
    
    # Stored as JSON string of [[lat, lng], ...]
    polyline_geojson = Column(Text, nullable=False)
    distance_km = Column(Float, nullable=False)
    eta_minutes = Column(Float, nullable=False)
    
    # Blockage & dynamic rerouting state
    has_blockage = Column(Boolean, default=False)
    blocked_segment = Column(String(128), nullable=True)
    original_route_geojson = Column(Text, nullable=True)
    original_eta_minutes = Column(Float, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationship
    incident = relationship("Incident", back_populates="routes")
