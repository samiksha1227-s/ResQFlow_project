from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    incident_code = Column(String(32), unique=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String(255), nullable=True)
    primary_source = Column(String(32), default="citizen") # cctv, citizen, dashcam, authority
    status = Column(String(32), default="reported") # reported, verified, dispatched, on_scene, transporting, arrived, closed, rejected
    severity = Column(String(16), default="medium") # low, medium, high, critical
    ai_confidence = Column(Float, default=0.0)
    ai_verified = Column(Boolean, default=False)
    is_demo_mode = Column(Boolean, default=True)
    
    victim_count = Column(Integer, default=1)
    vehicle_count = Column(Integer, default=2)
    description = Column(Text, nullable=True)
    media_url = Column(String(255), nullable=True)
    
    assigned_ambulance_id = Column(Integer, ForeignKey("ambulances.id"), nullable=True)
    recommended_hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    reports = relationship("IncidentReport", back_populates="incident", cascade="all, delete-orphan")
    ambulance = relationship("Ambulance", foreign_keys=[assigned_ambulance_id])
    hospital = relationship("Hospital", foreign_keys=[recommended_hospital_id])
    routes = relationship("Route", back_populates="incident", cascade="all, delete-orphan")
    activity_logs = relationship("ActivityLog", back_populates="incident", cascade="all, delete-orphan")
