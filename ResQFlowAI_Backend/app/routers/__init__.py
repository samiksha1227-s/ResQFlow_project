from app.routers.incidents import router as incidents_router
from app.routers.ambulances import router as ambulances_router
from app.routers.hospitals import router as hospitals_router
from app.routers.routing import router as routing_router
from app.routers.simulation import router as simulation_router
from app.routers.ai_detect import router as ai_detect_router

__all__ = [
    "incidents_router",
    "ambulances_router",
    "hospitals_router",
    "routing_router",
    "simulation_router",
    "ai_detect_router",
]
