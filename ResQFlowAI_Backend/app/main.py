import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.database import engine, Base, SessionLocal
from app.models import Ambulance
from app.seed_data import seed_database
from app.routers import (
    incidents_router,
    ambulances_router,
    hospitals_router,
    routing_router,
    simulation_router,
    ai_detect_router,
)

# Initialize database schema
Base.metadata.create_all(bind=engine)

# Auto-seed database if empty
db = SessionLocal()
try:
    if db.query(Ambulance).count() == 0:
        print("Empty database detected. Auto-seeding initial fleet and demo scenario...")
        seed_database(db)
finally:
    db.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION
)

# CORS setup for seamless frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount media directory for uploaded photos and annotated vision frames
if os.path.exists(settings.MEDIA_DIR):
    app.mount("/media", StaticFiles(directory=settings.MEDIA_DIR), name="media")

# Include API routers
app.include_router(incidents_router, prefix=settings.API_V1_STR)
app.include_router(ambulances_router, prefix=settings.API_V1_STR)
app.include_router(hospitals_router, prefix=settings.API_V1_STR)
app.include_router(routing_router, prefix=settings.API_V1_STR)
app.include_router(simulation_router, prefix=settings.API_V1_STR)
app.include_router(ai_detect_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "OPERATIONAL",
        "demo_mode": True,
        "docs_url": "/docs",
        "city": settings.CITY_NAME,
        "coordinates": {"lat": settings.CITY_CENTER_LAT, "lng": settings.CITY_CENTER_LNG}
    }
