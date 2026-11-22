from sqlalchemy import Column, Integer, String, Float, Text
from app.database import Base

class Hospital(Base):
    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), unique=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    trauma_level = Column(Integer, default=1) # 1: Comprehensive Regional Trauma Center, 2: Major, 3: General
    total_icu_beds = Column(Integer, default=20)
    available_icu_beds = Column(Integer, default=5)
    total_er_beds = Column(Integer, default=40)
    available_er_beds = Column(Integer, default=12)
    specialties = Column(Text, default="['Trauma', 'Neurosurgery', 'Cardiac', 'Burns']")
    contact_number = Column(String(32), default="+1-800-555-HOSP")
