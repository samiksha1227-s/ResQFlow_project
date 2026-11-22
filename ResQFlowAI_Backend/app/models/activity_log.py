from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)
    event_type = Column(String(64), nullable=False) # "AI_VERIFIED", "DEDUPLICATED", "DISPATCHED", "REROUTED", "OVERRIDE", "STATUS_CHANGE"
    message = Column(Text, nullable=False)
    severity = Column(String(16), default="info") # info, warning, danger, success
    payload_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    incident = relationship("Incident", back_populates="activity_logs")
