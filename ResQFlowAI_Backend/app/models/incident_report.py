from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class IncidentReport(Base):
    __tablename__ = "incident_reports"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)
    source_type = Column(String(32), nullable=False) # cctv, citizen, dashcam, authority
    source_identifier = Column(String(64), nullable=True) # Camera ID, Phone number, sensor ID
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    raw_text = Column(Text, nullable=True)
    media_url = Column(String(255), nullable=True)
    cluster_group_id = Column(Integer, nullable=True)
    reported_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    incident = relationship("Incident", back_populates="reports")
