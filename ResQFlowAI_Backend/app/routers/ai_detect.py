import os
import shutil
from fastapi import APIRouter, UploadFile, File, Form
from app.config import settings
from app.ai_engine import yolo_detector, accident_event_engine

router = APIRouter(prefix="/ai", tags=["AI & Computer Vision Engine"])

@router.post("/analyze-media")
async def analyze_media(
    file: UploadFile = File(...),
    source_type: str = Form("cctv")
):
    """
    Analyzes an uploaded image/video frame using:
    1. YOLOv8 object detector for vehicle and pedestrian detection
    2. Event Heuristic Layer for bounding box overlaps, rollover aspect ratio, and casualty proximity
    Returns detection boxes, event confidence score, and accident verification status.
    """
    save_path = os.path.join(settings.MEDIA_DIR, file.filename)
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 1. Run YOLO object detection
    detections = yolo_detector.detect_objects(save_path)

    # 2. Run Event Heuristic Confidence analysis
    analysis_result = accident_event_engine.analyze_event(detections, image_path=save_path)

    return {
        "filename": file.filename,
        "source_type": source_type,
        "detections_count": len(detections),
        "detections": detections,
        "analysis": analysis_result,
        "media_url": f"/media/{file.filename}"
    }

@router.get("/demo-benchmark")
def get_demo_benchmark():
    """Returns baseline benchmark data for demo purposes."""
    return {
        "model_architecture": "Ultralytics YOLOv8n + Geometric Intersection Heuristic",
        "supported_classes": ["car", "truck", "bus", "motorcycle", "person"],
        "verification_metrics": {
            "spatial_overlap_threshold_iou": 0.20,
            "rollover_aspect_ratio_threshold": 1.15,
            "pedestrian_hazard_radius_px": 180
        },
        "mode": "PROTOTYPE HACKATHON EVALUATION MODE"
    }
