from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Request, APIRouter, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.services.auth import get_current_user_id_from_cookie
from app.services.crud import get_detections_by_user
from app.models.database import SessionLocal
from app.controllers import history_controller
from starlette.exceptions import HTTPException as StarletteHTTPException
from ultralytics import YOLO
from datetime import datetime
from app.services.crud import get_detections_by_user, save_detection
from app.models.database import SessionLocal
import numpy as np
import exifread
import logging
import json
import cv2
import io

BASE_DIR = Path(__file__).resolve().parent.parent.parent

app = FastAPI()
router = APIRouter()
app.include_router(router)
app.include_router(history_controller.router)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")
logger = logging.getLogger(__name__)

model = YOLO(BASE_DIR / "app" / "models" / "special.pt")
CLASSES = ['ambulance', 'fire engine', 'gas emergency', 'police car', 'rescue helicopter']

def convert_to_degrees(value):
    d, m, s = value
    return float(d.num) / float(d.den) + float(m.num) / float(m.den) / 60 + float(s.num) / float(s.den) / 3600

def extract_metadata(file_bytes, filename, username="анонім"):
    try:
        if filename.lower().endswith((".webp", ".png", ".bmp")):
            return {
                "datetime": "Невідомо",
                "gps_lat": "Немає",
                "gps_lon": "Немає",
                "gps_lat_decimal": None,
                "gps_lon_decimal": None,
                "camera_model": "Невідомо",
                "brightness": "Невідомо",
                "orientation": "Невідомо",
                "source_path": filename,
                "capture_type": "aerial" if "drone" in filename.lower() else "ground",
                "username": username
            }

        tags = exifread.process_file(io.BytesIO(file_bytes), details=False)
        lat = tags.get("GPS GPSLatitude")
        lon = tags.get("GPS GPSLongitude")
        gps_lat_decimal = convert_to_degrees(lat.values) if lat else None
        gps_lon_decimal = convert_to_degrees(lon.values) if lon else None

        return {
            "datetime": str(tags.get("EXIF DateTimeOriginal", "Невідомо")),
            "gps_lat": str(lat or "Немає"),
            "gps_lon": str(lon or "Немає"),
            "gps_lat_decimal": gps_lat_decimal,
            "gps_lon_decimal": gps_lon_decimal,
            "camera_model": str(tags.get("Image Model", "Невідомо")),
            "brightness": str(tags.get("EXIF BrightnessValue", "Невідомо")),
            "orientation": str(tags.get("Image Orientation", "Невідомо")),
            "source_path": filename,
            "capture_type": "aerial" if "drone" in filename.lower() else "ground",
            "username": username
        }

    except Exception as e:
        return {
            "datetime": "Невідомо",
            "gps_lat": "Немає",
            "gps_lon": "Немає",
            "gps_lat_decimal": None,
            "gps_lon_decimal": None,
            "camera_model": "Невідомо",
            "brightness": "Невідомо",
            "orientation": "Невідомо",
            "source_path": filename,
            "capture_type": "unknown",
            "username": username,
            "error": f"EXIF помилка: {str(e)}"
        }

@router.get("/", response_class=HTMLResponse, name="home")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "metadata": None})

@router.post("/predict", response_class=HTMLResponse)
async def predict(request: Request, image: UploadFile = File(...)):
    try:
        contents = await image.read()
        metadata = extract_metadata(contents, image.filename)
        img = cv2.imdecode(np.frombuffer(contents, np.uint8), cv2.IMREAD_COLOR)

        if img is None:
            return templates.TemplateResponse("index.html", {
                "request": request,
                "metadata": metadata,
                "error": "❌ Неможливо обробити зображення. Перевірте формат файлу."
            })

        result = model(img)[0]
        save_path = BASE_DIR / "static" / "predictions" / image.filename
        result.save(filename=save_path)

        if not result.boxes or result.boxes.cls is None or len(result.boxes.cls) == 0:
            # ⛔️ НЕ ЧІПАЄМО: Твоя умова для окремої сторінки, якщо немає техніки
            return templates.TemplateResponse("error.html", {
                "request": request,
                "error_message": "Об'єкти не знайдено.",
                "metadata": metadata
            })

        class_id = int(result.boxes.cls[0])
        confidence = float(result.boxes.conf[0]) * 100
        predicted_class = CLASSES[class_id]

        db = SessionLocal()
        user_id = get_current_user_id_from_cookie(request)

        save_detection(db, {
            "user_id": user_id,
            "predicted_class": predicted_class,
            "confidence": confidence,
            "meta_info": json.dumps(metadata),
            "timestamp": datetime.now()
        })

        return templates.TemplateResponse("results.html", {
            "request": request,
            "predicted_class": predicted_class,
            "confidence": f"{confidence:.2f}",
            "metadata": metadata
        })

    except Exception as e:
        logger.error("Помилка обробки зображення:", exc_info=True)
        return templates.TemplateResponse("index.html", {
            "request": request,
            "metadata": {},
            "error": "🚨 Сталася непередбачувана помилка при обробці зображення. Спробуйте інший файл."
        })

@app.get("/history", response_class=HTMLResponse)
async def history(request: Request):
    user_id = get_current_user_id_from_cookie(request)
    if not user_id:
        return RedirectResponse("/login")

    db = SessionLocal()
    detections = get_detections_by_user(db, user_id)
    return templates.TemplateResponse("history.html", {
        "request": request,
        "detections": detections
    })

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    return HTMLResponse(content=str(exc.detail), status_code=exc.status_code)
