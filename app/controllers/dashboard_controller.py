from fastapi import APIRouter, Request, Depends, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.models.database import get_db, Detection, User
from app.services.auth import get_current_user
from datetime import datetime
import os
import shutil

router = APIRouter()
templates = Jinja2Templates(directory="templates")
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)

    history_list = db.query(Detection).filter(Detection.user_id == current_user.id).order_by(Detection.timestamp.desc()).all()

    last_result = None
    if history_list:
        last = history_list[0]
        last_result = {
            "predicted_class": last.predicted_class,
            "confidence": round(last.confidence * 100, 1),
            "metadata": {
                "source_path": last.meta_info,
                "datetime": last.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                "gps_lat": "50.4501",  # приклад метаданих
                "gps_lon": "30.5234",
                "camera_model": "N/A",
                "brightness": "N/A",
                "orientation": "N/A",
                "capture_type": "manual",
                "gps_lat_decimal": 50.4501,
                "gps_lon_decimal": 30.5234
            }
        }

    return templates.TemplateResponse("results.html", {
        "request": request,
        "user": current_user.username,
        "detections": history_list,
        "result": last_result
    })

@router.post("/analyze")
async def analyze_image(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)

    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    predicted_class = "tank"
    confidence = 0.93

    detection = Detection(
        user_id=current_user.id,
        timestamp=datetime.now(),
        predicted_class=predicted_class,
        confidence=confidence,
        meta_info=filename
    )
    db.add(detection)
    db.commit()

    return RedirectResponse(url="/result", status_code=302)
